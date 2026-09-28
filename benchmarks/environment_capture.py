#!/usr/bin/env python3
"""Read-only environment capture; never initializes a model or reads credentials."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SAFE_ENV = {'CUDA_VISIBLE_DEVICES', 'CUDA_DEVICE_ORDER', 'PYTHONPATH', 'PYTHONNOUSERSITE',
            'PYTHONDONTWRITEBYTECODE', 'HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'VLLM_HOST_IP',
            'VLLM_ENABLE_V1_MULTIPROCESSING', 'NCCL_SOCKET_IFNAME', 'GLOO_SOCKET_IFNAME',
            'NVIDIA_VISIBLE_DEVICES', 'VLLM_USE_V1'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def command(argv, timeout=20, env=None):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env)
        return {'argv': argv, 'returncode': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'argv': argv, 'error': type(e).__name__}


def sanitize_argv(argv):
    result, redact_next = [], False
    for item in argv:
        if redact_next:
            result.append('[REDACTED]'); redact_next = False; continue
        key = item.split('=', 1)[0].lower()
        if item.startswith('--') and any(s in key for s in ('api-key', 'api_key', 'password', 'access-token', 'auth-token', 'hf-token', 'authorization')):
            if '=' in item:
                result.append(key + '=[REDACTED]')
            else:
                result.append(item); redact_next = True
        else:
            clean = re.sub(r'(https?://)[^/@\s]+:[^/@\s]+@', r'\1[REDACTED]@', item)
            result.append(re.sub(r'([?&](?:token|api_key|access_token|key)=)[^&#\s]+', r'\1[REDACTED]', clean))
    return result


def process_record(pid):
    p = Path('/proc') / str(pid)
    argv = (p / 'cmdline').read_bytes().decode().rstrip('\0').split('\0')
    env = dict(s.split('=', 1) for s in (p / 'environ').read_bytes().decode().split('\0') if '=' in s)
    return {'pid': pid, 'argv': sanitize_argv(argv), 'executable': os.readlink(p / 'exe'),
            'cwd': os.readlink(p / 'cwd'), 'environment': {k: env[k] for k in sorted(SAFE_ENV) if k in env},
            'cgroup': (p / 'cgroup').read_text().strip(),
            'start_ticks': (p / 'stat').read_text().split(') ', 1)[1].split()[19]}


def find_server(model, port):
    found = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            argv = (p / 'cmdline').read_bytes().decode().rstrip('\0').split('\0')
            if '--port' in argv and argv[argv.index('--port') + 1] == str(port) and \
                    '--served-model-name' in argv and argv[argv.index('--served-model-name') + 1] == model:
                found.append(process_record(int(p.name)))
        except (OSError, ValueError, IndexError):
            continue
    if len(found) != 1:
        raise ValueError(f'Expected one {model} server on port {port}; found {len(found)}')
    return found[0]


def flag(argv, name, default=None):
    if name in argv:
        return argv[argv.index(name) + 1]
    return next((s.split('=', 1)[1] for s in argv if s.startswith(name + '=')), default)


def cache_metrics(port):
    # This GET reads existing counters/configuration; no inference request.
    text = urlopen(f'http://127.0.0.1:{int(port)}/metrics', timeout=10).read().decode()
    line = next(x for x in text.splitlines() if x.startswith('vllm:cache_config_info{'))
    values = {k: json.loads('"' + v + '"') for k, v in re.findall(r'(\w+)="((?:\\.|[^"\\])*)"', line)}
    return {'source': 'GET /metrics vllm:cache_config_info', 'labels': values, 'raw_metric': line}


PACKAGE_PROBE = r'''
import ast,importlib.metadata as m,json,sys,pathlib,platform
packages={d.metadata['Name']:d.version for d in m.distributions() if d.metadata.get('Name')}
builds={}
for name,filename in [('torch','torch/version.py'),('vllm','vllm/_version.py')]:
 try:
  dist=m.distribution(name); path=pathlib.Path(dist.locate_file(filename)); vals={}
  if path.exists():
   for node in ast.parse(path.read_text()).body:
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
     try:value=ast.literal_eval(node.value)
     except Exception:continue
     targets=node.targets if isinstance(node,ast.Assign) else [node.target]
     for target in targets:
      if isinstance(target,ast.Name):vals[target.id]=value
  direct=dist.read_text('direct_url.json')
  builds[name]={'version_file':str(path),'constants':vals,
               'vcs_info':json.loads(direct).get('vcs_info') if direct else None}
 except m.PackageNotFoundError:pass
print(json.dumps({'python':sys.version,'executable':sys.executable,'prefix':sys.prefix,
                 'platform':platform.platform(),'packages':packages,'builds':builds}))
'''


def software(executable, dest):
    env = dict(os.environ)
    for name in ('PYTHONPATH', 'PYTHONHOME'):
        env.pop(name, None)
    env.update(CUDA_VISIBLE_DEVICES='', PYTHONDONTWRITEBYTECODE='1')
    result = command([str(executable), '-B', '-c', PACKAGE_PROBE], env=env)
    if result.get('returncode') != 0:
        raise RuntimeError(f'Package inventory failed: {executable}')
    data = json.loads(result['stdout'])
    write(dest / 'packages.json', data)
    (dest / 'requirements.freeze.txt').write_text(
        '# Installed distribution versions; build metadata is in packages.json.\n' +
        '\n'.join(f'{k}=={v}' for k, v in sorted(data['packages'].items(), key=lambda x: x[0].lower())) + '\n')
    return data


def checkpoint(path, dest):
    path = Path(path)
    files = {}
    for p in sorted(path.iterdir()):
        if not p.is_file():
            continue
        info = {'bytes': p.stat().st_size, 'source': str(p)}
        if p.suffix == '.safetensors':
            blob = p.resolve().name
            info['huggingface_lfs_blob_sha256'] = blob if re.fullmatch('[0-9a-f]{64}', blob) else None
            info['verification'] = 'HF cache content address; large weight file not reread during running experiment'
        else:
            info['sha256'] = sha(p)
            if p.name in ('config.json', 'generation_config.json', 'tokenizer_config.json', 'chat_template.jinja',
                          'model.safetensors.index.json', 'configuration.json'):
                shutil.copyfile(p, dest / p.name)
        files[p.name] = info
    cache_name = path.parent.parent.name
    return {'repository_id': cache_name.removeprefix('models--').replace('--', '/'),
            'revision': path.name, 'local_path': str(path), 'files': files,
            'tokenizer_source': 'same pinned snapshot unless server argv explicitly overrides tokenizer',
            'chat_template': 'chat_template.jinja in this snapshot unless server argv overrides --chat-template'}


def capture(output, run_id, phase, solver_python, grader_python=None, release='1.0.0', live=True,
            gemma_port=8030, qwen_port=8027, container_image=None, container_digest=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    now = datetime.now(timezone.utc).isoformat()
    host = {'os_release': Path('/etc/os-release').read_text(), 'uname': command(['uname', '-a']),
            'cpu': command(['lscpu', '-J']), 'memory_kib': {line.split(':')[0]: int(line.split()[1])
                for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemTotal:', 'SwapTotal:'))},
            'gpus': command(['nvidia-smi', '--query-gpu=index,name,uuid,memory.total,driver_version,pci.bus_id', '--format=csv,noheader']),
            'gpu_topology': command(['nvidia-smi', 'topo', '-m']),
            'container_detection': command(['systemd-detect-virt', '--container']),
            'container_image': container_image, 'container_digest': container_digest,
            'container_note': 'No image/digest inferred when none is supplied; see process cgroups and detection result.'}
    host['pci_links'] = {}
    for device in Path('/sys/bus/pci/devices').iterdir():
        try:
            if (device / 'vendor').read_text().strip() != '0x10de':
                continue
            host['pci_links'][device.name] = {name: (device / name).read_text().strip() for name in
                ('current_link_speed', 'current_link_width', 'max_link_speed', 'max_link_width') if (device / name).exists()}
        except OSError:
            pass
    data = {'schema': 'imo-environment-v1', 'run_id': run_id, 'captured_at': now, 'capture_phase': phase,
            'hardware_system': host, 'servers': {}, 'software': {}, 'checkpoints': {},
            'git': {'head': command(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']),
                    'status': command(['git', '-C', str(ROOT), 'status', '--porcelain', '--untracked-files=no'])},
            'capture_code_sha256': sha(__file__)}
    for role, model, port in [('gemma', 'google/gemma-4-31B-it', gemma_port), ('qwen', 'Qwen/Qwen3.6-27B', qwen_port)]:
        if not live:
            data['servers'][role] = {'state': 'not_observed_offline'}
            continue
        record = find_server(model, port)
        argv = record['argv']
        record['cache_metrics'] = cache_metrics(port)
        record['parallelism'] = {k: int(flag(argv, f'--{k.replace("_", "-")}', '1')) for k in
                                 ('tensor_parallel_size', 'pipeline_parallel_size', 'data_parallel_size')}
        record['parallelism_source'] = 'explicit argv or installed vLLM default of 1'
        record['speculative_config'] = json.loads(flag(argv, '--speculative-config', '{}'))
        record['thinking'] = json.loads(flag(argv, '--default-chat-template-kwargs', '{}'))
        data['servers'][role] = record
        sd = output / 'software' / role
        sd.mkdir(parents=True)
        data['software'][role] = software(argv[0], sd)
        model_path = flag(argv, 'serve')
        extra = [(role, model_path)]
        if record['speculative_config'].get('model'):
            extra.append((role + '_mtp_assistant', record['speculative_config']['model']))
        if flag(argv, '--tokenizer') and flag(argv, '--tokenizer') != model_path:
            extra.append((role + '_tokenizer', flag(argv, '--tokenizer')))
        for label, path in extra:
            md = output / 'models' / label
            md.mkdir(parents=True)
            data['checkpoints'][label] = checkpoint(path, md)
        template = flag(argv, '--chat-template')
        if template:
            tp = Path(template)
            shutil.copyfile(tp, output / 'models' / role / 'server_chat_template_override.jinja')
        cmd = ['env', *[f'{k}={v}' for k, v in sorted(record['environment'].items())], *argv]
        script = '#!/usr/bin/env bash\nset -euo pipefail\ncd ' + shlex.quote(record['cwd']) + '\nexec ' + shlex.join(cmd) + '\n'
        (output / f'launch_{role}.sh').write_text(script)
    for role, executable in [('solver', solver_python), ('grader', grader_python)]:
        if executable:
            sd = output / 'software' / role
            sd.mkdir(parents=True)
            data['software'][role] = software(executable, sd)
    release_path = ROOT / 'harnesses/imo_proof_pipeline/releases' / release
    for name in ('profile.json', 'release.json'):
        shutil.copyfile(release_path / name, output / name)
    data['harness'] = {'name': 'IMO Proof Pipeline', 'release': release,
                       'release_sha256': sha(release_path / 'release.json'),
                       'profile_sha256': sha(release_path / 'profile.json'),
                       'source_archive': str(release_path / 'engine'),
                       'release_git_commit': command(['git', '-C', str(ROOT), 'rev-parse', f'imo-proof-pipeline/v{release}^{{commit}}'])}
    patch = ROOT / 'vllm_compat/sitecustomize.py'
    if patch.exists():
        shutil.copyfile(patch, output / 'vllm_sitecustomize.py')
        data['serving_compatibility_patch'] = {'source': str(patch), 'sha256': sha(patch)}
    data['grading_client'] = command(['codex', '--version']) if grader_python else {'state': 'not_observed'}
    shutil.copyfile(__file__, output / 'capture_source.py')
    launcher_source = ROOT / 'benchmarks/run_experiment.py'
    if launcher_source.exists():
        shutil.copyfile(launcher_source, output / 'experiment_launcher_source.py')
    write(output / 'environment.json', data)
    (output / 'ENVIRONMENT.md').write_text(render_markdown(data))
    inventory = {str(p.relative_to(output)): sha(p) for p in output.rglob('*') if p.is_file()}
    write(output / 'SHA256SUMS.json', {'run_id': run_id, 'files': inventory})
    return data


def render_markdown(data, prefix=''):
    host = data['hardware_system']
    gpu = host['gpus'].get('stdout', 'Unavailable')
    try:
        cpu = {x['field'].rstrip(':'): x['data'] for x in json.loads(host['cpu']['stdout'])['lscpu']}
    except (KeyError, ValueError):
        cpu = {}
    os_name = next((x.split('=', 1)[1].strip('"') for x in host['os_release'].splitlines() if x.startswith('PRETTY_NAME=')), 'Unknown')
    lines = [f'# Environment — {data["run_id"]}', '',
             f'Captured **{data["captured_at"]}**; phase **{data["capture_phase"]}**.', '',
             f'[Full configuration]({prefix}environment.json) · [Launch scripts]({prefix or "./"}) · '
             f'[Dependency locks]({prefix}software) · [Hashes]({prefix}SHA256SUMS.json)', '',
             '## Hardware and system', '',
             f'- OS: {os_name}; kernel: `{host["uname"].get("stdout", "unavailable")}`.',
             f'- CPU: {cpu.get("Model name", "unknown")}; {cpu.get("CPU(s)", "unknown")} logical CPUs.',
             f'- RAM: {host["memory_kib"]["MemTotal"] / 1048576:.2f} GiB as reported by Linux.',
             f'- Container detection: `{host["container_detection"].get("stdout", "unknown")}`; '
             f'image: `{host.get("container_image")}`; digest: `{host.get("container_digest")}`. Missing values are not inferred.', '',
             'GPU index, model, UUID, VRAM (MiB), NVIDIA driver, PCI bus:', '', '```text', gpu, '```', '',
             'GPU interconnect/topology:', '', '```text',
             re.sub(r'\x1b\[[0-9;]*m', '', host['gpu_topology'].get('stdout', 'unavailable')), '```', '',
             '## Software', '', '| Environment | Python | PyTorch | vLLM | Transformers |', '|---|---|---|---|---|']
    for role, sw in data['software'].items():
        packages = {k.lower(): v for k, v in sw['packages'].items()}
        torch = sw['builds'].get('torch', {}).get('constants', {})
        lines.append(f'| {role} | {sw["python"].split()[0]} | {torch.get("__version__", packages.get("torch", "—"))} | '
                     f'{packages.get("vllm", "—")} | {packages.get("transformers", "—")} |')
    lines += ['', 'Build commits and CUDA runtime package versions are in each `software/<role>/packages.json`. '
              '`requirements.freeze.txt` pins installed distribution versions; it does not contain wheel hashes, '
              'system driver packages, or a container image. The model weights are separately identified by repository revisions '
              'and HF cache blob IDs, without rereading all weights during a live run.', '', '## Separate serving configurations', '']
    for role, server in data['servers'].items():
        lines += [f'### {role}', '']
        if not server.get('argv'):
            lines += ['Serving process not observed in this offline snapshot.', '']; continue
        argv = server['argv']; cache = server['cache_metrics']['labels']
        fields = {'GPU visibility': server['environment'].get('CUDA_VISIBLE_DEVICES'),
                  'Model': flag(argv, '--served-model-name'), 'Weight dtype': flag(argv, '--dtype'),
                  'Weight quantization CLI': flag(argv, '--quantization', 'unset; inspect pinned model config'),
                  'KV-cache dtype': cache.get('cache_dtype'), 'Recurrent-state dtype': cache.get('mamba_ssm_cache_dtype'),
                  'Maximum context': flag(argv, '--max-model-len'), 'Maximum sequences': flag(argv, '--max-num-seqs'),
                  'Batched token limit': flag(argv, '--max-num-batched-tokens'), 'Prefix caching': cache.get('enable_prefix_caching'),
                  'Parallelism': server['parallelism'], 'Speculative decoding': server['speculative_config'],
                  'Chat template kwargs': server['thinking'], 'Asynchronous scheduling': '--async-scheduling' in argv}
        lines += ['| Setting | Value |', '|---|---|']
        lines += [f'| {key} | `{value}` |' for key, value in fields.items()]
        lines += ['', f'[Exact launch command]({prefix}launch_{role}.sh).', '']
    lines += ['Both recorded servers coexist. Compare their GPU visibility values to determine whether they share GPUs; '
              'concurrency varies by pipeline stage. Their prefix caches and compilation state are not reset by capture.', '',
              '## Model and tokenizer revisions', '', '| Role | Repository | Revision |', '|---|---|---|']
    lines += [f'| {role} | {m["repository_id"]} | `{m["revision"]}` |' for role, m in data['checkpoints'].items()]
    lines += ['', 'Tokenizer/chat-template file hashes, generation defaults, and checkpoint file inventories are in '
              '`environment.json` and `models/`. Explicit tokenizer/template overrides appear in server argv.', '',
              '## Harness and generation policy', '', f'Release: **{data["harness"]["release"]}**, '
              f'digest `{data["harness"]["release_sha256"]}`. '
              'The pinned `profile.json` records model roles, temperatures, base seeds, caps, extended reasoning, '
              'three R1 cycles and stopping policies; `release.json` hashes the complete source/prompt inventory. '
              'Actual derived seeds and per-request settings remain in native generation metadata.', '',
              '## External grading and runtime', '',
              'Record the actual grading provider, model ID, parameters and evaluation timestamps under the experiment’s '
              '`grading/` directory. Local GPU details do not describe external provider hardware. '
              'The environment observation time is not a grading date.', '',
              'Measure solver wall time from worker launch to worker exit, excluding environment capture and grading. '
              'Native request metadata separates call latency, usage, and extended reasoning continuation; parallel call '
              'latencies cannot simply be summed to obtain experiment wall time. Historical or retrospective snapshots '
              'do not establish the cache state or package state at an earlier launch.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--phase', choices=['before_generation', 'retrospective'], required=True)
    parser.add_argument('--solver-python', default='/home/user/miniconda3/envs/math/bin/python')
    parser.add_argument('--grader-python')
    parser.add_argument('--release', default='1.0.0')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    result = capture(args.output_dir, args.run_id, args.phase, args.solver_python, args.grader_python, args.release, not args.offline)
    print(json.dumps({'run_id': result['run_id'], 'captured_at': result['captured_at'], 'output': str(args.output_dir)}, indent=2))
