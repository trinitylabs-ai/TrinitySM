# IMO-ProofBench Advanced

[Official problem sources and cited papers](../../../docs/sources.md).

[Problems](problems): **30 statement-only JSON files**. Exact source paths and hashes are in [catalog.json](catalog.json).

The historical Advanced run used the frozen v263/v290 engine subsequently packaged as IMO Proof Pipeline v1.0.0. Its original launch command and run identity remain authoritative. This checkout contains archived evidence, not the original live queue or scoring workspace.

## Result archives

[Current B 1.12.0 results: final proofs, selections and both grading passes](../../../docs/results/proofbench_b112_final_20260926/README.md).

[Experiment directories with proofs, grades, rubrics, model settings and harness provenance](results/README.md).

## Runs

The historical `pipeline_run01` workspace is not bundled. Its former alias is recorded in the [legacy path inventory](../../../docs/reproduction/legacy_paths.json).

## Scores

Published IMOBench ProofAutoGrader rubric and official per-problem guidelines, with scores 0/1/6/7. Score only the raw draft before lazy checking and the final refinement output, after the entire problem worker finishes, in the existing separate scoring environment.

- [Archived raw and final scores with proof links](results/pipeline_raw_r1c3/README.md)

## Reports

- [Published matrices and ablations](../../../docs/public_release_report.md)
- [Current two-pass results and per-problem comparisons](../../../docs/results/proofbench_b112_final_20260926/README.md)

See the [shared layout and launch conventions](../../README.md) for new experiments. Links above point to included copies; original run names remain provenance.
