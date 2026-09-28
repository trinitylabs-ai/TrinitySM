# IMO 2026

[Official problem sources and cited papers](../../docs/sources.md).

[Problems](problems): **6 statement-only JSON files**. Exact source paths and hashes are in [catalog.json](catalog.json).

The archive includes historical review, fusion, revision and recovery experiments.
Their recorded implementation identities remain attached to each result. The
current Workshop Pipeline runs all three refinement passes automatically.
Experimental tool results are reported separately from the core workflow.

## Result archives

[Current B 1.12.0 results: all six problems, final proofs, votes and both grading passes](../../docs/results/imo2026_b112_selection_20260922/README.md).

[Experiment directories with proofs, grades, rubrics, model settings and harness provenance](results/README.md).

## Runs

Historical working directories were named `raw_lazy`, `review_fusion_p5`,
`review_fusion_remaining`, `cycle1_recoveries` and `p2_tool_call_r47`.
Those runtime directories are not included in this checkout. Preserved proof,
grade and provenance copies are available in the result archives above.

## Scores

- [Role-specific refinement extended reasoning: completed B matrix and A/B comparison](results/refinement_bf_B6_selection_first_20260920_1426/README.md)
  — 24 B proofs, 48 grading judgments; B mean 4.396/7 versus archived A 4.042/7.

Historical strict gold-informed Olympiad scoring, 0–7; separate from IMOBench grading.

- [Archived review/fusion grades](results/review_fusion/grades)
- [Archived P2 tool-call grades](results/p2_tool_call_r47/grades)

## Reports

- [Archived review/fusion score table and proof links](results/review_fusion/README.md)

See the [shared layout and launch conventions](../README.md) for new experiments.
Historical run identifiers refer to their original experiments; the links above
point to files included in this checkout.
