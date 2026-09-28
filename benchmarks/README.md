# Proof Workshop benchmarks

[Official problem sources and cited papers](../docs/sources.md).

[Public release evaluation report](../docs/public_release_report.md): the
separate IMO-ProofBench and IMO 2026 score matrices, grading schemes, checkpoint selection, coverage, and
portable proof/grade evidence with an offline verification script.

[Environment and reproduction details](../ENVIRONMENT.md) include hardware,
separate Gemma/Qwen serving settings, checkpoints, dependency locks and the
external grader configuration. New experiments use `run_experiment.py` to save
an environment snapshot before invoking the existing versioned solver.

| Benchmark | Problems | Directory |
|---|---:|---|
| IMO 2026 | 6 | [imo2026](imo2026/README.md) |
| IMO-ProofBench Basic | 30 | [imo-proofbench/basic](imo-proofbench/basic/README.md) |
| IMO-ProofBench Advanced | 30 | [imo-proofbench/advanced](imo-proofbench/advanced/README.md) |

Each benchmark has `problems/`, `results/`, `runs/`, `scores/`, `reports/`, and a
`catalog.json`. `problems/` contains byte-identical snapshots of the existing
statement-only JSON inputs; their original paths and SHA-256 hashes are recorded
in the catalog. Only pass `problems/` to the solver. It contains no grading
guidelines, reference answers, reports, or source manifests.

Each experiment has a subdirectory in `results/`:

```text
results/<experiment>/
  proofs/        # Copies of the submitted proofs, by problem/candidate/checkpoint
  grades/        # Saved scores, full grade records, manifests and grading prompts
  grading/       # Rubric, references, per-problem guidelines and grader model settings
  generation/    # Generation manifests, solver settings and available harness snapshots
  manifest.json  # Proof-to-grade bindings and copied-file SHA-256 inventory
  README.md      # Clickable proof/grade matrix and provenance notes
```

Result archives contain actual proof and grade copies; code archives and original
run navigation use links where indicated. IMOBench grader source snapshots match
the recorded runner hashes. Older strict grading has its exact saved rubric and
model records, with current scorer code explicitly labeled as such. Original
generation manifests identify historical harness versions; later source freezes
are not asserted to reproduce every older experiment.

The saved model identifier for these grades is `gpt-5.6-sol` with `xhigh` reasoning.
The historical strict 0–7 rubric and the IMOBench 0/1/6/7 rubric remain separate.
Grading references and guidelines live only under the evaluation archives, outside
the statement-only generation inputs.

Verify the published results with the current offline script:

```bash
python3 -B scripts/reproduce.py
```

It checks the saved proof/grade bindings and reproduces the core score table.
The old catalog-export script depended on omitted research runs, older releases
and a local grading skill; it has been removed. Commands inside saved experiment
READMEs are historical provenance, not current reproduction instructions.

Original run paths in manifests may point to omitted working directories.
The portable report evidence is self-contained; it does not need those paths.
Generated proofs and grades remain in their existing result directories.

For newly completed 6+3+3 runs, `scripts/grade_sampled_suite.py --run-id <run_id>`
builds final-proof manifests and invokes the separate Strict Olympiad v2 and
IMOBench B.5 graders. See the [setup, background command and result paths](../docs/local_reproduction.md#grade-a-completed-sampled-suite).
Generation itself still makes no external grading calls.

## Destination for future experiments

Every future experiment gets its own directory under the appropriate benchmark:

```text
benchmarks/imo2026/results/<run_id>/
benchmarks/imo-proofbench/basic/results/<run_id>/
benchmarks/imo-proofbench/advanced/results/<run_id>/
```

Use a unique ID such as `workshop_20260917_001`. Within that directory:

| Path | Contents |
|---|---|
| `generation/run/` | Native harness output: proofs, checkpoints, prompts, logs, release identity and model settings |
| `proofs/` | Selected submitted proof snapshots, bound to their grades by hashes |
| `grades/` | Published score records and full grading explanations |
| `grading/` | Rubric, per-problem guidelines, references and grader model configuration |
| `grading/work/` | Working output of the separate grading process |
| `reports/` | Score matrices and comparisons |
| `manifest.json` | Experiment identity, proof/grade bindings and provenance |

Launch through `benchmarks/run_experiment.py`; it captures the environment and
invokes the existing versioned [Workshop Pipeline](../harnesses/proof_workshop/README.md)
with `--output-dir` pointing to `generation/run/`. The launcher records the
release and run ID automatically. Other experiment archives are populated from the saved
outputs; directory naming alone does not launch scoring or export snapshots.

Generation reads only the benchmark's statement-only `problems/` directory.
Scoring runs in its separate environment and writes into the same experiment's
evaluation directories. Live `generation/run/` and `grading/work/` are ignored by
Git; selected proof, grade and provenance snapshots remain trackable. Former
`runs/`, `scores/`, and `reports/` aliases are recorded in the
[legacy path inventory](../docs/reproduction/legacy_paths.json); their original
workspaces are not included in the checkout.

For example, an offline check on one Advanced problem, from the repository root:

```bash
python -B benchmarks/run_experiment.py \
  --benchmark imo-proofbench/advanced \
  --run-id workshop_dryrun_001 --release 1.12.0 \
  --limit 1 --dry-run
```

Use a new output directory for each experiment; do not pre-create the final
`generation/run/` directory. Existing historical runs must be resumed with their
recorded original launcher and paths. The routing instructions are also saved in
[AGENTS.md](AGENTS.md) and each benchmark's `catalog.json`.
