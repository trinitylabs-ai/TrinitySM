"""One GPU, exhaustive model sweeps, persistent sleeping vLLM servers."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import signal
import threading
import time
import urllib.request

ENDPOINTS = {'gemma': 'http://127.0.0.1:8030', 'qwen': 'http://127.0.0.1:8027'}


def now(): return datetime.now(timezone.utc).isoformat()


def request(role, path, post=False, timeout=300):
    req = urllib.request.Request(ENDPOINTS[role] + path, data=b'' if post else None)
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=timeout) as response:
        raw = response.read()
    return json.loads(raw) if raw else {}


class Scheduler:
    def __init__(self, directory, *, grace=20, proof_limit=4, comparison_limit=12, gpu=0):
        self.root = Path(directory)
        self.gpu = gpu
        self.grace = grace
        self.proof_limit = proof_limit
        self.proof_limits_by_model = {role: proof_limit for role in ENDPOINTS}
        self.comparison_limit = comparison_limit
        self.lock = threading.RLock()
        self.tickets = {}
        self.current = 'gemma'
        self.state = 'ready'
        self.error = None
        self.idle_since = None
        self.switches = 0
        self.started = now()
        self.stop = False
        self.wait_for_admission = False
        self.health_checked_at = None
        self.health_error = None
        self.unhealthy_since = None
        self.server_restarts = Counter()

    def event(self, action, **fields):
        row = dict(at=now(), action=action, **fields)
        with (self.root / 'scheduler_events.jsonl').open('a') as f:
            f.write(json.dumps(row) + '\n')
        print(json.dumps(row), flush=True)

    def snapshot(self):
        counts = {role: dict(Counter(t['state'] for t in self.tickets.values() if t['role'] == role))
                  for role in ENDPOINTS}
        active = [t for t in self.tickets.values() if t['state'] == 'granted']
        queued = [t for t in self.tickets.values() if t['state'] == 'waiting']
        return dict(state=self.state, current_model=self.current, model_switches=self.switches,
            started_at=self.started, updated_at=now(), pid=os.getpid(), gpu=self.gpu, directory=str(self.root.resolve()),
            policy='drain-all-ready-work-for-current-model-before-switching',
            proof_concurrency=self.proof_limits_by_model[self.current], comparison_concurrency=self.comparison_limit,
            proof_concurrency_by_model=dict(self.proof_limits_by_model),
            switch_quiet_seconds=self.grace, counts=counts, active=active, queued=queued,
            error=self.error, health_checked_at=self.health_checked_at, health_error=self.health_error,
            server_restarts=dict(self.server_restarts))

    def pause(self, reason):
        if self.state not in ('failed', 'stopped', 'switching'):
            if self.state != 'paused': self.event('server_unhealthy_queue_paused', reason=reason)
            self.state = 'paused'
            self.health_error = reason
            if self.unhealthy_since is None: self.unhealthy_since = time.monotonic()
            self.idle_since = None

    def check_health(self, probe=None):
        if self.state not in ('ready', 'paused'): return
        try:
            if probe is None:
                request(self.current, '/health', timeout=3)
                if request(self.current, '/is_sleeping', timeout=3)['is_sleeping']:
                    raise RuntimeError('The active server is unexpectedly asleep')
            else: probe()
        except Exception as error:
            with self.lock: self.pause(repr(error)); self.health_checked_at=now()
        else:
            with self.lock:
                self.health_checked_at=now()
                if self.state=='paused':
                    self.event('server_health_restored', role=self.current)
                    self.state='ready';self.health_error=None
                    self.unhealthy_since=None

    def save(self):
        tmp = self.root / 'scheduler_status.json.tmp'
        tmp.write_text(json.dumps(self.snapshot(), indent=2) + '\n')
        tmp.replace(self.root / 'scheduler_status.json')

    def configure(self, proof_limit, comparison_limit, reason, proof_limits_by_model=None):
        if type(proof_limit) is not int or not 1 <= proof_limit <= 12:
            raise ValueError('Proof concurrency must be an integer in [1,12]')
        if type(comparison_limit) is not int or not 1 <= comparison_limit <= 12:
            raise ValueError('Comparison concurrency must be an integer in [1,12]')
        limits = dict.fromkeys(ENDPOINTS, proof_limit) if proof_limits_by_model is None else dict(proof_limits_by_model)
        if set(limits) != set(ENDPOINTS) or any(type(v) is not int or not 1 <= v <= 12 for v in limits.values()):
            raise ValueError('Per-model proof concurrency requires gemma and qwen integers in [1,12]')
        previous=dict(proof_concurrency=self.proof_limits_by_model[self.current],comparison_concurrency=self.comparison_limit,
                      proof_concurrency_by_model=dict(self.proof_limits_by_model))
        self.proof_limit=proof_limit;self.comparison_limit=comparison_limit
        self.proof_limits_by_model=limits
        record=dict(at=now(),proof_concurrency=limits[self.current],comparison_concurrency=comparison_limit,
                    proof_concurrency_by_model=dict(limits),
                    previous=previous,reason=reason,active_calls_interrupted=0)
        temporary=self.root/'runtime_limits.json.tmp'
        temporary.write_text(json.dumps(record,indent=2)+'\n');temporary.replace(self.root/'runtime_limits.json')
        self.event('concurrency_changed',**{k:v for k,v in record.items() if k!='at'})
        self.save()
        return record

    def restore(self, snapshot, journal):
        """Restore acknowledged leases before accepting connections after handoff."""
        if snapshot['state']!='ready':raise ValueError('Handoff requires a healthy, ready scheduler')
        self.current=snapshot['current_model'];self.switches=snapshot['model_switches']
        self.started=snapshot['started_at'];self.server_restarts.update(snapshot.get('server_restarts') or {})
        switching=False
        lines=journal.splitlines()
        for index,line in enumerate(lines):
            try:row=json.loads(line)
            except ValueError:
                if index==len(lines)-1 and not journal.endswith('\n'):break
                raise
            action=row['action'];key=row.get('id')
            if action in ('queued','granted'):
                self.tickets[key]={k:v for k,v in row.items() if k not in ('action','at')}
            elif action=='released':
                self.tickets[key].update(state='released',released_at=row['at'])
            elif action=='switch_started':switching=True
            elif action=='switch_completed':
                switching=False;self.current=row['current'];self.switches=row['model_switches']
        if switching:raise ValueError('Cannot hand off during a model switch')
        active=[t for t in self.tickets.values() if t['state']=='granted']
        if any(t['role']!=self.current for t in active):raise ValueError('Active role differs from loaded model')
        self.event('scheduler_handoff_restored',active=len(active),
                   queued=sum(t['state']=='waiting' for t in self.tickets.values()),
                   previous_pid=snapshot['pid'],new_pid=os.getpid())

    def enqueue(self, value):
        if value['role'] not in ENDPOINTS: raise ValueError('Unknown role')
        key = value['id']
        if key not in self.tickets:
            self.tickets[key] = dict(value, state='waiting', queued_at=now())
            self.event('queued', **self.tickets[key])
        else:
            for field in ('role', 'pid', 'stage', 'output_dir', 'comparison'):
                if self.tickets[key][field] != value[field]: raise ValueError('Ticket identity changed')
        return self.ticket(key)

    def ticket(self, key):
        if self.state in ('failed', 'stopped'):
            return dict(state=self.state, error=self.error)
        return self.tickets[key]

    def release(self, key):
        ticket = self.tickets[key]
        if ticket['state'] != 'released':
            ticket.update(state='released', released_at=now())
            self.event('released', id=key, role=ticket['role'], stage=ticket['stage'])
        return dict(state='released')

    def step(self, clock=time.monotonic):
        if self.state != 'ready': return None
        active = [t for t in self.tickets.values() if t['state'] == 'granted']
        if any(t['role'] != self.current for t in active):
            raise RuntimeError('Active lease belongs to the sleeping model')
        ready = [t for t in self.tickets.values() if t['state'] == 'waiting' and t['role'] == self.current]
        if ready:
            self.idle_since = None
            for ticket in ready:
                limit = self.comparison_limit if ticket['comparison'] and all(t['comparison'] for t in active) else self.proof_limits_by_model[self.current]
                if len(active) >= limit: break
                ticket.update(state='granted', granted_at=now())
                active.append(ticket)
                self.event('granted', **ticket)
        if active:
            self.idle_since = None
            return None
        if ready: return None
        if self.wait_for_admission and not (self.root / 'all_problems_admitted.json').exists():
            return None
        other = 'qwen' if self.current == 'gemma' else 'gemma'
        if not any(t['state'] == 'waiting' and t['role'] == other for t in self.tickets.values()):
            self.idle_since = None
            return None
        if self.idle_since is None: self.idle_since = clock()
        if clock() - self.idle_since < self.grace: return None
        self.state = 'switching'
        return other

    def switch(self, destination):
        previous = self.current
        self.event('switch_started', previous=previous, destination=destination)
        # No request may be aborted merely because its client released a lease.
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(ENDPOINTS[previous] + '/metrics', timeout=10) as r:
            metrics = r.read().decode()
        for metric in ('num_requests_running', 'num_requests_waiting'):
            values = re.findall(r'^vllm:' + metric + r'(?:\{[^\n]*\})?\s+([0-9.eE+-]+)', metrics, re.M)
            if not values or any(float(v) != 0 for v in values):
                raise RuntimeError('Server requests have not drained: ' + metric)
        request(previous, '/sleep?level=1&mode=wait', post=True)
        if not request(previous, '/is_sleeping')['is_sleeping']:
            raise RuntimeError('Previous model did not sleep')
        request(destination, '/wake_up', post=True)
        if request(destination, '/is_sleeping')['is_sleeping']:
            raise RuntimeError('Destination model did not wake')
        with self.lock:
            self.current = destination
            self.switches += 1
            self.state = 'ready'
            self.idle_since = None
            self.event('switch_completed', current=destination, model_switches=self.switches)
            self.save()

    def run(self):
        while not self.stop:
            try:
                # Check the engine before granting any new leases, every sweep.
                # /v1/models alone remains available even after EngineCore dies.
                self.check_health()
                with self.lock:
                    destination = self.step()
                    for t in self.tickets.values():
                        if t['state'] == 'granted' and not Path('/proc', str(t['pid'])).exists():
                            raise RuntimeError('Lease owner exited unexpectedly: ' + t['id'])
                    self.save()
                if destination: self.switch(destination)
            except Exception as error:
                with self.lock:
                    self.state = 'failed'; self.error = repr(error)
                    self.event('failed', error=self.error); self.save()
                break
            time.sleep(1)


def serve(directory, port, restore_directory=None, proof_limit=None, owner_pid=None, proof_limits_by_model=None, gpu=0):
    scheduler = Scheduler(directory, gpu=gpu)
    scheduler.wait_for_admission = True
    if restore_directory:
        source=Path(restore_directory)
        scheduler.restore(json.loads((source/'scheduler_status.json').read_text()),
                          (source/'scheduler_events.jsonl').read_text())
    if not restore_directory:
        awake = [role for role in ENDPOINTS if not request(role, '/is_sleeping', timeout=5)['is_sleeping']]
        if len(awake) != 1: raise RuntimeError('Expected exactly one awake model')
        scheduler.current = awake[0]
    other='qwen' if scheduler.current=='gemma' else 'gemma'
    if request(scheduler.current, '/is_sleeping', timeout=3)['is_sleeping'] or not request(other, '/is_sleeping', timeout=3)['is_sleeping']:
        raise RuntimeError('Loaded/sleeping model state does not match the scheduler')
    request(scheduler.current,'/health',timeout=3)
    limits=Path(directory)/'runtime_limits.json'
    previous=json.loads(limits.read_text()) if limits.exists() else {}
    if proof_limits_by_model is None and proof_limit is None:
        proof_limits_by_model = previous.get('proof_concurrency_by_model')
    scheduler.configure(proof_limit if proof_limit is not None else previous.get('proof_concurrency',4),
                        previous.get('comparison_concurrency',12),'restore configured admission limits; preserve active leases',
                        proof_limits_by_model)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def dispatch(self):
            try:
                with scheduler.lock:
                    if self.path == '/status': result = scheduler.snapshot()
                    elif self.path.startswith('/ticket/'): result = scheduler.ticket(self.path.split('/')[-1])
                    elif self.path in ('/enqueue', '/release', '/server_fault', '/configure'):
                        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                        if self.path=='/configure':
                            result=scheduler.configure(data['proof_concurrency'],data['comparison_concurrency'],data['reason'],
                                                       data.get('proof_concurrency_by_model'))
                        elif self.path=='/server_fault':
                            scheduler.pause(data['error']);scheduler.save();result={'state':scheduler.state}
                        else: result = scheduler.enqueue(data) if self.path == '/enqueue' else scheduler.release(data['id'])
                    else: raise ValueError('Unknown operation')
                raw = json.dumps(result).encode(); self.send_response(200)
            except Exception as error:
                raw = json.dumps({'error': repr(error)}).encode(); self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(raw))); self.end_headers()
            self.wfile.write(raw)
        do_GET = dispatch
        do_POST = dispatch
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    if owner_pid:
        owner=Path('/proc',str(owner_pid),'stat')
        identity=owner.read_text().split(') ',1)[1].split()[19]
        def watch_owner():
            while not scheduler.stop:
                try:
                    fields=owner.read_text().split(') ',1)[1].split()
                    alive=fields[19]==identity and fields[0]!='Z'
                except FileNotFoundError:alive=False
                if not alive:
                    with scheduler.lock:
                        scheduler.event('controller_exited',pid=owner_pid)
                        scheduler.stop=True
                    server.shutdown()
                    return
                time.sleep(2)
        threading.Thread(target=watch_owner,daemon=True).start()
    threading.Thread(target=scheduler.run, daemon=True).start()
    scheduler.event('broker_started', port=port)
    server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', required=True)
    parser.add_argument('--port', type=int, default=18890)
    parser.add_argument('--restore-directory')
    parser.add_argument('--proof-limit',type=int)
    parser.add_argument('--gemma-proof-limit',type=int)
    parser.add_argument('--qwen-proof-limit',type=int)
    parser.add_argument('--owner-pid',type=int)
    parser.add_argument('--gpu',type=int,default=0)
    args = parser.parse_args()
    if (args.gemma_proof_limit is None) != (args.qwen_proof_limit is None):
        parser.error('Supply both --gemma-proof-limit and --qwen-proof-limit')
    per_model = None if args.gemma_proof_limit is None else {'gemma': args.gemma_proof_limit, 'qwen': args.qwen_proof_limit}
    serve(args.directory, args.port, args.restore_directory, args.proof_limit, args.owner_pid, per_model, args.gpu)
