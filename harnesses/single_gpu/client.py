"""Schedule complete logical calls outside frozen inference deadlines."""
from contextlib import contextmanager
from contextvars import ContextVar
import functools
import json
import os
import time
import urllib.request
import uuid
import urllib.error

ACTIVE = ContextVar('gpu0_bulk_lease', default=None)


def api(path, body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(os.environ['GPU0_BULK_URL'] + path, data=data,
        headers={'Content-Type': 'application/json'})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=15) as response:
        return json.load(response)


def actor(arguments):
    model = str(arguments['model']).lower()
    if 'gemma' in model: return 'gemma'
    if 'qwen' in model: return 'qwen'
    raise RuntimeError('Unrecognized bulk-scheduler model: ' + model)


@contextmanager
def lease(arguments):
    role = actor(arguments)
    prior = ACTIVE.get()
    if prior:
        if prior['role'] != role:
            raise RuntimeError('A logical call changed models while holding a GPU lease')
        yield
        return
    key = uuid.uuid4().hex
    stage = arguments.get('stage_name', arguments.get('stage', 'unknown'))
    ticket = dict(id=key, role=role, pid=os.getpid(), stage=stage,
                  output_dir=str(arguments.get('output_dir', '')),
                  comparison='cross_lane_proof_comparison' in stage)
    # Admission retries are idempotent and cannot issue an inference request.
    while True:
        try:
            state = api('/enqueue', ticket)
            break
        except (OSError, TimeoutError):
            time.sleep(3)
    try:
        while state['state'] != 'granted':
            if state['state'] in ('failed', 'stopped'):
                raise RuntimeError('GPU scheduler stopped: ' + str(state))
            time.sleep(2)
            try:
                state = api('/ticket/' + key)
            except (OSError, TimeoutError):
                continue
        token = ACTIVE.set(ticket)
        try:
            yield
        finally:
            ACTIVE.reset(token)
    finally:
        # Do not return to a frozen retry/fallback loop before releasing a lease.
        for attempt in range(10):
            try:
                api('/release', {'id': key})
                break
            except (OSError, TimeoutError):
                time.sleep(1)
        else:
            raise RuntimeError('Cannot release GPU scheduler lease; fail closed')


def wrap(function):
    if getattr(function, '_gpu0_bulk_wrapped', False): return function
    @functools.wraps(function)
    def call(*args, **kwargs):
        if args:
            raise TypeError('Expected keyword-only frozen model invocation')
        with lease(kwargs):
            return function(**kwargs)
    call._gpu0_bulk_wrapped = True
    return call


def patch_module(module):
    name = module.__name__
    if name.endswith('.runtime'):
        original=module.run_openai_chat_generation
        @functools.wraps(original)
        def guarded_transport(**kwargs):
            try:
                return original(**kwargs)
            except Exception as error:
                if isinstance(error, urllib.error.URLError) or any(s in str(error) for s in
                    ('EngineCore', 'EngineDead', 'Connection refused', 'HTTP 500', 'stream server error')):
                    try: api('/server_fault', {'error': repr(error), 'role': actor(kwargs)})
                    except OSError: pass
                raise
        module.run_openai_chat_generation = wrap(guarded_transport)
    elif name.endswith('.budget_forcing'):
        module._call_with_budget_forcing = wrap(module._call_with_budget_forcing)
    elif name.endswith('.repair_boundary'):
        module.default_markdown_call = wrap(module.default_markdown_call)
    elif name.endswith('.timeout_adapter'):
        original = module.install
        @contextmanager
        @functools.wraps(original)
        def install(*args, **kwargs):
            with original(*args, **kwargs) as caller:
                # The comparison's 600s logical deadline starts inside caller.
                yield wrap(caller)
        module.install = install
