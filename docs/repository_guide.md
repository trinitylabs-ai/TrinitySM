# Repository guide

TrinitySM is the project name used in the main README. The pinned CLI still
reports `TrinitySM 0.1.0-rc.1`; its default implementation is B 1.12.0.
These existing execution identities are preserved for reproducibility.

| Path | Purpose |
|---|---|
| [Workshop Pipeline](../harnesses/proof_workshop/README.md) | Composite harness and public entry point |
| [Workshop modules](../harnesses/modules/README.md) | Draft and Refine components and implementation mapping |
| [Versioned releases](../harnesses/imo_proof_pipeline/README.md) | Frozen source inventories, release controller and version policy |
| [Workshop Tools](../experiments/workshop_tools/README.md) | Experimental tool-call extension |
| [benchmarks](../benchmarks/README.md) | Statement-only datasets, experiment launcher and result layout |
| [docs/public_release_report.md](public_release_report.md) | Evaluation methods, score matrices and limitations |
| [docs/public_release](public_release/score_snapshot.json) | Portable selected proofs, grading records, policies and verifier |
| [ENVIRONMENT.md](../ENVIRONMENT.md) | Recorded hardware, checkpoints, serving commands and package versions |

Experiment directories separate native generation output, published proofs,
grades, grading work and reports. Many older `runs/` paths and native working
directories are archival locations and are not included in a checkout. The
public report's evidence bundle is self-contained for score verification.

Raw runtime logs and log archives are excluded from the release tree. Proofs,
prompts, configurations and grades stay in place. See the
[reproduction and publication notes](reproduction/README.md) for verification
commands and historical replay limitations. Old research commit IDs are
provenance identifiers; a snapshot publication need not contain those commits.

Broken aliases to omitted workspaces have been replaced by a
[legacy path inventory](reproduction/legacy_paths.json). It retains every
alias and original target without presenting unavailable paths as live files.
