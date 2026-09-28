# Explicit task bindings

`--task-manifest` accepts a JSON object with a `tasks` list. Each row has
`problem_id` (e.g. PB-Basic-029), `candidate_id`, and `proof_path`. Paths are relative
to the manifest. Optional `expected_hashes` maps any of `problem_sha256`,
`reference_sha256`, `guidelines_sha256`, `proof_sha256` to expected SHA-256 values.
Text hashes use stripped UTF-8 text. Supplied hashes are always checked.

The official dataset supplies problem/reference/guidelines by Problem ID.
Explicit manifests may intentionally select intermediate proofs; these are labeled
explicit rather than pipeline-completed. Do not supply alternative gold inputs.

`--source-report` accepts the Basic inventory's `rows` list, extracting only source
bindings and hashes; any prior grade is ignored. `--source-run` accepts a queue
root containing `problems/PB-*/summary.json` or one completed problem directory.
Current proof and last-checkpoint hashes must agree for source-bound inputs.

Changed task selections require a new output directory. Resume requires unchanged
selection, source hashes, rubric, model and reasoning settings.
