import contextlib
import importlib.util
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from harnesses.single_gpu import broker, client


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        guard = patch('socket.create_connection', side_effect=AssertionError('Model-free scheduler tests must not contact a server'))
        guard.start()
        self.addCleanup(guard.stop)

    def scheduler(self, root, **kw):
        s = broker.Scheduler(root, grace=20, **kw)
        s.event = lambda *a, **kw: None
        return s

    def enqueue(self, s, key, role='gemma', comparison=False):
        return s.enqueue(dict(id=key, role=role, pid=os.getpid(), stage='test',
                              output_dir='/tmp/test', comparison=comparison))

    def test_drains_all_problems_and_waits_for_active_continuation(self):
        with tempfile.TemporaryDirectory() as root:
            s = self.scheduler(root)
            for i in range(9): self.enqueue(s, str(i))
            self.enqueue(s, 'q', 'qwen')
            for batch in (range(4), range(4, 8), range(8, 9)):
                self.assertIsNone(s.step(lambda: 0))
                self.assertEqual(sum(t['state'] == 'granted' for t in s.tickets.values()), len(batch))
                # Time alone cannot preempt even the last active continuation.
                self.assertIsNone(s.step(lambda: 9999))
                for i in batch: s.release(str(i))
            self.assertIsNone(s.step(lambda: 10000))
            self.assertIsNone(s.step(lambda: 10019))
            self.assertEqual(s.step(lambda: 10020), 'qwen')

    def test_late_ready_work_prevents_switch(self):
        with tempfile.TemporaryDirectory() as root:
            s = self.scheduler(root)
            self.enqueue(s, 'q', 'qwen'); s.step(lambda: 0)
            self.enqueue(s, 'g'); self.assertIsNone(s.step(lambda: 21))
            self.assertEqual(s.ticket('g')['state'], 'granted')

    def test_no_first_switch_before_all_problem_workers_admitted(self):
        with tempfile.TemporaryDirectory() as root:
            s = self.scheduler(root);s.wait_for_admission=True
            self.enqueue(s, 'q', 'qwen')
            self.assertIsNone(s.step(lambda: 0));self.assertIsNone(s.step(lambda: 100))
            (Path(root)/'all_problems_admitted.json').write_text('{}')
            self.assertIsNone(s.step(lambda: 100))
            self.assertEqual(s.step(lambda: 120),'qwen')

    def test_comparisons_have_separate_limit(self):
        with tempfile.TemporaryDirectory() as root:
            s = self.scheduler(root)
            for i in range(15): self.enqueue(s, str(i), comparison=True)
            s.step()
            self.assertEqual(sum(t['state'] == 'granted' for t in s.tickets.values()), 12)

    def test_nested_bf_and_transport_share_one_lease(self):
        events = []
        def api(path, body=None):
            events.append(path)
            return dict(state='granted' if path != '/release' else 'released')
        @client.wrap
        def transport(**kw):
            self.assertIsNotNone(client.ACTIVE.get())
            return kw
        @client.wrap
        def logical(**kw):
            return transport(**kw), transport(**kw)
        original = dict(model='google/gemma-4-31B-it', stage='review', output_dir=Path('/tmp/a'), prompt='same', seed=123)
        with patch.object(client, 'api', api):
            first, second = logical(**original)
        self.assertEqual(first, original); self.assertEqual(second, original)
        self.assertEqual(events, ['/enqueue', '/release'])

    def test_comparison_deadline_starts_after_admission(self):
        events = []
        def api(path, body=None):
            events.append(path)
            return dict(state='granted')
        @contextlib.contextmanager
        def install():
            def deadline_caller(**kw):
                events.append('start_deadline')
                return 42
            yield deadline_caller
        module = types.SimpleNamespace(__name__='x.timeout_adapter', install=install)
        client.patch_module(module)
        with patch.object(client, 'api', api), module.install() as call:
            self.assertEqual(call(model='qwen', stage_name='cross_lane_proof_comparison'), 42)
        self.assertEqual(events, ['/enqueue', 'start_deadline', '/release'])

    def test_idle_metrics_required_before_sleep(self):
        with tempfile.TemporaryDirectory() as root:
            s = self.scheduler(root)
            class Reply:
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def read(self): return b'vllm:num_requests_running{model="gemma"} 1\nvllm:num_requests_waiting 0\n'
            opener = types.SimpleNamespace(open=lambda *a, **kw: Reply())
            with patch.object(broker.urllib.request, 'build_opener', return_value=opener), patch.object(broker, 'request') as call:
                with self.assertRaisesRegex(RuntimeError, 'not drained'): s.switch('qwen')
                call.assert_not_called()

    def test_unhealthy_engine_pauses_without_exhausting_queue(self):
        with tempfile.TemporaryDirectory() as root:
            s=self.scheduler(root)
            for i in range(176): self.enqueue(s,str(i))
            def failed(): raise OSError('EngineCore died')
            s.check_health(failed)
            self.assertEqual(s.state,'paused');self.assertIsNone(s.step())
            self.assertEqual(sum(t['state']=='waiting' for t in s.tickets.values()),176)
            self.assertEqual(s.ticket('0')['state'],'waiting')
            s.check_health(lambda:None);s.step()
            self.assertEqual(s.state,'ready')
            self.assertEqual(sum(t['state']=='granted' for t in s.tickets.values()),4)

    def test_explicit_server_fault_stops_granting_new_work(self):
        with tempfile.TemporaryDirectory() as root:
            s=self.scheduler(root)
            for i in range(8): self.enqueue(s,str(i))
            s.step();s.pause('physical request saw EngineDeadError')
            for i in range(4):s.release(str(i))
            s.step()
            self.assertEqual(sum(t['state']=='waiting' for t in s.tickets.values()),4)
            self.assertEqual(sum(t['state']=='granted' for t in s.tickets.values()),0)

    def test_live_increase_to_six_and_lowering_never_interrupts_active_calls(self):
        with tempfile.TemporaryDirectory() as root:
            s=self.scheduler(root)
            for i in range(10):self.enqueue(s,str(i))
            s.step();s.configure(6,12,'user request');s.step()
            self.assertEqual(sum(t['state']=='granted' for t in s.tickets.values()),6)
            s.configure(4,12,'drain down');s.step()
            self.assertEqual(sum(t['state']=='granted' for t in s.tickets.values()),6)
            for i in range(3):s.release(str(i))
            s.step();self.assertEqual(sum(t['state']=='granted' for t in s.tickets.values()),4)

    def test_handoff_preserves_active_queued_released_and_idempotent_release(self):
        import json
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            s=broker.Scheduler(first)
            for i in range(9):self.enqueue(s,str(i))
            s.step();snapshot=s.snapshot()
            s.release('0')  # Event newer than last periodic snapshot.
            self.enqueue(s,'late','qwen')
            journal=(Path(first)/'scheduler_events.jsonl').read_text()
            restored=broker.Scheduler(second)
            restored.restore(snapshot,journal+'{"action":')
            self.assertEqual(restored.ticket('0')['state'],'released')
            self.assertEqual(restored.ticket('1')['state'],'granted')
            self.assertEqual(restored.ticket('8')['state'],'waiting')
            self.assertEqual(restored.ticket('late')['role'],'qwen')
            restored.release('0')
            restored.configure(6,12,'increase')
            restored.step()
            self.assertEqual(sum(t['state']=='granted' for t in restored.tickets.values()),6)
            self.assertEqual(json.loads((Path(second)/'runtime_limits.json').read_text())['proof_concurrency'],6)

    def test_qwen_uses_six_during_its_bulk_turn(self):
        with tempfile.TemporaryDirectory() as root:
            s=self.scheduler(root);s.current='qwen';s.configure(6,12,'user requested Qwen six')
            self.enqueue(s,'g','gemma')
            for i in range(10):self.enqueue(s,str(i),'qwen')
            s.step()
            active=[t for t in s.tickets.values() if t['state']=='granted']
            self.assertEqual(len(active),6)
            self.assertTrue(all(t['role']=='qwen' for t in active))
            self.assertEqual(s.ticket('g')['state'],'waiting')

    def test_per_model_limits_apply_before_first_admission_after_each_switch(self):
        with tempfile.TemporaryDirectory() as root:
            s=self.scheduler(root);s.current='qwen'
            s.configure(8,12,'approved Qwen twelve, Gemma eight',{'gemma':8,'qwen':12})
            for role in ('gemma','qwen'):
                for i in range(14):self.enqueue(s,f'{role}{i}',role)
            s.step()
            self.assertEqual(len(s.snapshot()['active']),12)
            for i in range(12):s.release(f'qwen{i}')
            s.step()
            for i in range(12,14):s.release(f'qwen{i}')
            self.assertIsNone(s.step(lambda:0))
            self.assertEqual(s.step(lambda:20),'gemma')
            class Reply:
                def __enter__(self):return self
                def __exit__(self,*args):pass
                def read(self):return b'vllm:num_requests_running 0\nvllm:num_requests_waiting 0\n'
            def request(role,path,**kwargs):
                return {'is_sleeping':role=='qwen'} if path=='/is_sleeping' else {}
            opener = types.SimpleNamespace(open=lambda *a, **kw: Reply())
            with patch.object(broker.urllib.request,'build_opener',return_value=opener), patch.object(broker,'request',side_effect=request):
                s.switch('gemma')
            s.step()
            self.assertEqual(s.snapshot()['proof_concurrency'],8)
            self.assertEqual(len(s.snapshot()['active']),8)
            self.assertEqual(s.snapshot()['proof_concurrency_by_model'],{'gemma':8,'qwen':12})

    def test_per_model_configuration_survives_handoff_with_active_calls(self):
        import json
        with tempfile.TemporaryDirectory() as first,tempfile.TemporaryDirectory() as second:
            s=broker.Scheduler(first,proof_limit=8);s.current='qwen'
            for i in range(15):self.enqueue(s,str(i),'qwen')
            s.step();before=s.snapshot()
            s.configure(8,12,'approved',{'gemma':8,'qwen':12})
            s.release('0')
            restored=broker.Scheduler(second)
            restored.restore(before,(Path(first)/'scheduler_events.jsonl').read_text())
            limits=json.loads((Path(first)/'runtime_limits.json').read_text())
            restored.configure(limits['proof_concurrency'],limits['comparison_concurrency'],'restore',limits['proof_concurrency_by_model'])
            restored.step()
            self.assertEqual(restored.ticket('0')['state'],'released')
            self.assertEqual(len(restored.snapshot()['active']),12)
            for i in range(1,8):
                self.assertEqual(restored.ticket(str(i))['granted_at'],s.ticket(str(i))['granted_at'])
            self.assertEqual(restored.snapshot()['proof_concurrency_by_model'],{'gemma':8,'qwen':12})

    def test_invalid_per_model_limit_changes_nothing(self):
        with tempfile.TemporaryDirectory() as root:
            s=self.scheduler(root,proof_limit=8)
            for limits in ({'qwen':12},{'gemma':8,'qwen':13},{'gemma':8,'qwen':True}):
                with self.assertRaises(ValueError):s.configure(8,12,'invalid',limits)
                self.assertEqual(s.snapshot()['proof_concurrency_by_model'],{'gemma':8,'qwen':8})


if __name__ == '__main__': unittest.main()
