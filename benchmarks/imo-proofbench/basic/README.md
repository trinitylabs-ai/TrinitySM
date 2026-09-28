# IMO-ProofBench Basic

[Official problem sources and cited papers](../../../docs/sources.md).

[Problems](problems): **30 statement-only JSON files**. Exact source paths and hashes are in [catalog.json](catalog.json).

Historical Basic runs span multiple recorded configurations and retain their original identities. The old `runs/pipeline_selected` aliases identified the attempts used by the raw-before-lazy inventory, including the selected P9 and P26 reruns. Their original targets are preserved in the [legacy path inventory](../../../docs/reproduction/legacy_paths.json). The without extended reasoning comparison uses its separate raw-only harness.

## Result archives

[Current B 1.12.0 results: final proofs, selections and both grading passes](../../../docs/results/proofbench_b112_final_20260926/README.md).

[Experiment directories with proofs, grades, rubrics, model settings and harness provenance](results/README.md).

## Runs

The historical working directories `pipeline_p1`, `pipeline_main`,
`pipeline_p26_rerun`, `pipeline_p27`, `pipeline_p28_30`, `pipeline_p9_rerun`
and `raw_no_budget_forcing` are not bundled. Preserved copies are linked below.

## Scores

Published IMOBench ProofAutoGrader rubric and official per-problem guidelines, with scores 0/1/6/7.

- [Raw with extended reasoning](results/pipeline_raw_bf/README.md)
- [Final refinement proofs](results/pipeline_final/README.md)
- [Raw without extended reasoning](results/raw_no_bf/README.md)

## Reports

- [Published matrices, ablations and their limitations](../../../docs/public_release_report.md)
- [Current two-pass results and per-problem comparisons](../../../docs/results/proofbench_b112_final_20260926/README.md)

See the [shared layout and launch conventions](../../README.md) for new experiments. Links above point to included copies; original run names remain provenance.
