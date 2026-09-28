# Cognitive Well v0.3.263

This is the final unified successor to v0.3.260 for the September 5 experiment.
It retains v0.3.260's 32,768-token minimum for every same-trace budget-forcing
continuation and combines the two recoveries that were exercised separately as
v0.3.261 and v0.3.262.

The v0.3.261 compatibility is now cross-record guarded. A Resolver response that
says `ORIGINAL_PROOF_VALID` with `fusion_assessment: VALIDATED` is accepted only
when the exact paired Fusion record is valid and says `ACCEPT_AS_WRITTEN`. Model
text is not edited. Every other parser error remains fatal.

The v0.3.262 recovery is now confined to the third resolver. When all inherited
v0.3.79 attempts end with empty repetition responses, v0.3.263 performs exactly
one fresh full-task retry under a new seed namespace. It never continues the
failed repetition trace. Length, protocol, transport, and mixed failures remain
fatal.

No reference solution, gold score, or Codex feedback enters generation.

## Entry point

```bash
python -m cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905 \
  --problem-file math_harness_inputs/imo2026_p4_p2_v0313_20260815/imo2026_p3.json \
  --problem-id imo2026_p3 \
  --problem-number 3 \
  --output-dir runs/example_v0263_p3
```

Use `--dry-run` for a no-model-call manifest check.

## Consolidating the completed September 5 run

The historical v0.3.261 P5 and v0.3.262 P3 recoveries can be sealed into one
hash-validated v0.3.263 record without making model calls or modifying proofs:

```bash
python -m cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905.consolidate \
  --run-root runs/v0257_v108_six_problem_bf_temp_transition_20260904
```

