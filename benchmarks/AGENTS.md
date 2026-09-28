# Future benchmark runs

Use the benchmark directories in this tree as the destination for future
experiments. Each experiment gets a new, unique run ID under
`<benchmark>/results/<run_id>/`, where `<benchmark>` is `imo2026`,
`imo-proofbench/basic`, or `imo-proofbench/advanced`.

- Pass `<benchmark>/problems/` as the statement-only solver input.
- Pass `<benchmark>/results/<run_id>/generation/run/` as the native harness
  output directory. Do not create this final `run/` directory before the
  versioned launcher starts; the launcher requires a fresh output path.
- Record the explicit IMO Proof Pipeline release in the launch. Preserve the
  generated release identity, manifests, model settings, seeds and prompts.
- Use `benchmarks/run_experiment.py` for new launches so the environment and
  configuration are captured before generation. It invokes the existing pinned
  solver and never starts grading. See the repository `ENVIRONMENT.md`.
- Retain the same run ID in published artifact sidecars. After separately
  publishing grades, use the launcher's `--index-only` mode to update the
  proof/verification/score/timing index without modifying native solver files.
- Run grading in a separate environment, with working files under
  `<benchmark>/results/<run_id>/grading/work/`. Keep rubrics, references and
  grading feedback outside the solver's inputs and generation work directory.
- Store submitted proof snapshots in `proofs/`, published grades in `grades/`,
  rubric and grader configuration in `grading/`, and readable comparisons in
  `reports/`, all inside the same experiment directory. Record proof hashes and
  provenance in its `manifest.json`.
- For the current Advanced scoring policy, grade only raw before lazy and
  the final refinement output after the whole problem worker finishes.
- Resume an existing experiment using its original paths, version and recorded
  settings. Do not relocate current or historical jobs to adopt this layout.

Former `runs/`, `scores/`, and `reports/` aliases to omitted workspaces are recorded
in `docs/reproduction/legacy_paths.json`; they are provenance, not live inputs.
New experiments use the result directory layout above. Creating this
layout does not authorize starting an experiment or changing the frozen harness.
