#!/usr/bin/env python3
"""Verify published results offline or generate fresh proofs with local models."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ('imo2026', 'imo-proofbench/basic', 'imo-proofbench/advanced')


def generation_seed(value):
    try:
        seed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('Generation seed must be an integer from 0 to 4294967295')
    if not 0 <= seed <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError('Generation seed must be an integer from 0 to 4294967295')
    return seed


def offline():
    # This path imports no model/client library and starts no network process.
    subprocess.run([sys.executable, '-B', str(ROOT / 'docs/public_release/verify_scores.py')], check=True, cwd=ROOT)


def generate(args):
    if not args.run_id:
        raise ValueError('Fresh generation requires --run-id')
    # A venv's python can be a symlink; retain that path to keep its site-packages.
    solver = args.solver_python.expanduser().absolute()
    if not solver.is_file():
        raise ValueError('Solver interpreter missing; run setup_environment.py --install')
    groups = BENCHMARKS if args.benchmark == 'all' else (args.benchmark,)
    if args.benchmark == 'all' and args.problem_id:
        raise ValueError('--problem-id requires a single benchmark')
    seed = (secrets.randbits(32) if getattr(args, 'random_generation_seed', False)
            else getattr(args, 'generation_seed', None))
    if seed is not None:
        print(f'Generation seed: {seed}', flush=True)
    environment = dict(os.environ, HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    for group in groups:
        run_id = args.run_id if len(groups) == 1 else args.run_id + '_' + group.replace('/', '_')
        command = [str(solver), '-B', str(ROOT / 'benchmarks/run_experiment.py'),
                   '--benchmark', group, '--run-id', run_id, '--release', args.release,
                   '--solver-python', str(solver), '--gemma-port', '8030', '--qwen-port', '8027']
        if seed is not None:
            command += ['--raw-seed-offset', str(seed), '--seed-namespace', f'workshop-generation:{seed}']
        for problem in args.problem_id or []:
            command += ['--problem-id', problem]
        command += ['--dry-run' if args.dry_run else '--execute-models']
        subprocess.run(command, check=True, cwd=ROOT, env=environment)
        print(f'Final proofs: benchmarks/{group}/results/{run_id}/generation/run/proofs/', flush=True)
    print('New proofs are ungraded. Historical published grades are not assigned to them.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('report', 'generate'), nargs='?', default='report')
    parser.add_argument('--benchmark', choices=(*BENCHMARKS, 'all'), default='imo-proofbench/basic')
    parser.add_argument('--problem-id', action='append')
    parser.add_argument('--run-id')
    parser.add_argument('--release', default='1.12.0')
    parser.add_argument('--solver-python', type=Path, default=ROOT / '.venv-solver/bin/python')
    seeds = parser.add_mutually_exclusive_group()
    seeds.add_argument('--generation-seed', type=generation_seed, metavar='N',
                       help='Unsigned 32-bit seed for raw generation and refinement; omit to preserve recorded defaults')
    seeds.add_argument('--random-generation-seed', action='store_true',
                       help='Draw and print one generation seed for this invocation')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.mode == 'report':
        if (args.run_id or args.problem_id or args.dry_run
                or args.generation_seed is not None or args.random_generation_seed):
            parser.error('Generation options require generate mode')
        offline()
    else:
        try:
            generate(args)
        except ValueError as error:
            parser.error(str(error))


if __name__ == '__main__':
    main()
