# V356 — V349 with the V353 discrete extension

This consolidated release restores the V349 geometry exporter and retains its root-classification path, including the Basic-008 tool. It adds the generic V353 discrete tools and synthesis binding used for Basic-009. Geometry compilation, certificate search, polynomial export, root solving, proof-writing prompts, audits, final revision and budget forcing retain their V349 implementations.

The selection and synthesis binding extension is operation-based. No problem IDs, saved answers, grading feedback or problem-specific mathematical rules are added to runtime code. V354/V355 geometry derivation export is not included.

`selected_resume` replays the originally selected audited geometry, root or discrete certificate from a completed source worker and reruns proof synthesis. It validates task identity, source hashes, semantic audits, exact evidence and budget-forcing records, and rechecks them before each new model call. It never supplies prior rewritten proofs, audits or external grades as initial synthesis inputs. A new final revision uses only the newly generated proof under the inherited policy.

Launch normal runs with `benchmarks/run_experiment.py --tool-harness-version 0.3.356`. For synthesis-only validation, add `--resume-selected-certificate-from SOURCE_NATIVE_RUN` and the exact original source proof. All benchmark runs require a fresh run ID and the explicit pipeline release.

Historical success evidence is Basic-008 1→6 (V344), IMO P2 t07_r02 4→6 (V349), and Basic-009 1→7 (V353). Those saved scores are historical observations, not a guarantee for a regenerated proof. Release validation records source compatibility and new grading separately.
