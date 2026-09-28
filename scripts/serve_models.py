#!/usr/bin/env python3
"""Serve one recorded model on loopback; no hosted inference or automatic download."""
import argparse
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def plan(model, model_dir, gpu, port=None, *, sleep_mode=False, swap_dir=None):
    catalog = json.loads((ROOT / 'configs/workshop_models.json').read_text())
    profile = json.loads((ROOT / 'harnesses/imo_proof_pipeline/releases' /
                          catalog['pipeline_release'] / 'profile.json').read_text())
    def snapshot(role):
        spec = catalog['models'][role]
        return model_dir / ('models--' + spec['repository'].replace('/', '--')) / 'snapshots' / spec['revision']
    checkpoint = snapshot(model)
    spec = profile['servers'][model]
    if checkpoint.name != spec['snapshot'] or catalog['models'][model]['repository'] != spec['model']:
        raise ValueError('Model catalog differs from the pinned release profile')
    python = ROOT / '.venv-serving/bin/python'
    command = [str(python), str(python.parent / 'vllm'), 'serve', str(checkpoint),
               '--served-model-name', spec['model']]
    for name, value in spec['flags'].items():
        command += [name, value]
    command += ['--host', '127.0.0.1', '--port', str(port or (8030 if model == 'gemma' else 8027)),
                '--language-model-only', '--default-chat-template-kwargs',
                json.dumps({'enable_thinking': True}), '--async-scheduling']
    speculative = {'method': 'mtp', 'num_speculative_tokens': 4}
    required = [checkpoint]
    if model == 'gemma':
        assistant = snapshot('gemma_assistant')
        if assistant.name != spec['assistant_snapshot']:
            raise ValueError('Assistant revision differs from the pinned release profile')
        speculative['model'] = str(assistant)
        required.append(assistant)
    command += ['--speculative-config', json.dumps(speculative)]
    environment = {
        'CUDA_VISIBLE_DEVICES': str(gpu), 'GLOO_SOCKET_IFNAME': 'lo',
        'NCCL_SOCKET_IFNAME': 'lo', 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
        'VLLM_ENABLE_V1_MULTIPROCESSING': '0', 'VLLM_HOST_IP': '127.0.0.1',
        'PYTHONPATH': str(ROOT / '.workshop/compat'), 'PYTHONDONTWRITEBYTECODE': '1',
    }
    if sleep_mode:
        command += ['--enable-sleep-mode']
        if model == 'gemma':
            command += ['--kv-cache-memory-bytes', '30064771072']
        environment.update(
            VLLM_SERVER_DEV_MODE='1',
            GPU0_SWAP_STORAGE=str(swap_dir or ROOT / '.workshop/servers/swap'),
            VLLM_CACHE_ROOT=str(ROOT / '.workshop/servers/sleep_cache'),
            WORKSHOP_BASE_COMPAT=str(ROOT / '.workshop/compat/sitecustomize.py'),
            PYTHONPATH=str(ROOT / 'harnesses/single_gpu/server_compat'))
    return command, environment, required


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=('gemma', 'qwen'), required=True)
    parser.add_argument('--model-dir', type=Path, default=ROOT / '.models')
    parser.add_argument('--gpu', type=int)
    parser.add_argument('--port', type=int, help='Loopback port; useful for a second Gemma server')
    parser.add_argument('--sleep-mode', action='store_true', help='Recorded one-GPU weight offload and sleep/wake settings.')
    parser.add_argument('--swap-dir', type=Path, help='Local disk directory for file-backed sleeping weights.')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    gpu = args.gpu if args.gpu is not None else (0 if args.model == 'gemma' else 1)
    if gpu < 0:
        parser.error('--gpu must be nonnegative')
    if args.port is not None and not 1 <= args.port <= 65535:
        parser.error('--port must be in 1..65535')
    if args.swap_dir and not args.sleep_mode:
        parser.error('--swap-dir requires --sleep-mode')
    swap_dir = args.swap_dir.expanduser().resolve() if args.swap_dir else None
    command, environment, required = plan(args.model, args.model_dir.expanduser().resolve(), gpu, args.port,
                                           sleep_mode=args.sleep_mode, swap_dir=swap_dir)
    if args.dry_run:
        print(json.dumps({'command': command, 'environment': environment}, indent=2))
        return
    if not Path(command[0]).is_file():
        parser.error('Run scripts/setup_environment.py --install first.')
    for checkpoint in required:
        if not (checkpoint / 'config.json').is_file() or not any(checkpoint.glob('*.safetensors')):
            parser.error(f'Missing local checkpoint: {checkpoint}; run setup with --download-models.')
    compat = ROOT / '.workshop/compat'
    compat.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/vllm_sitecustomize.py'
    shutil.copyfile(source, compat / 'sitecustomize.py')
    os.chdir(ROOT)
    env = dict(os.environ)
    env.pop('PYTHONHOME', None)
    env.update(environment)
    os.execve(command[0], command, env)


if __name__ == '__main__':
    main()
