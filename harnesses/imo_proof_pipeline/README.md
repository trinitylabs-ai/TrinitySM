# Workshop Pipeline implementation

This directory contains the current implementation, **B (1.12.0)**, and its integrity
checks. Use the [official entry point](../proof_workshop/README.md) to run the
complete **Draft → Refinement 1 → Refinement 2 → Refinement 3** workflow.
The public controller automatically schedules the final pass for every available
lane and exports its final proof. No manual continuation is required.

The [registry](releases/index.json) contains default B (1.12.0) and preserved
earlier A/B engines for historical replay. Preserved releases retain their
registered hashes. B 1.12.0 combines the [B refinement extended reasoning policy](../../docs/harness_b.md)
with [original expansion at 0.4 and the final replacement audit](../../docs/harness_b_selection.md),
followed by a [cross-lane voter](../../docs/cross_lane_voter.md).
Internal package names identify required implementation modules; they are not
additional supported harness releases.

The engine bundles Workshop Draft and Workshop Refine with their recorded
prompts, schemas, seed rules, sampling settings, extended reasoning and recovery
behavior. Models and installed Python dependencies remain external. The
[current profile](releases/1.12.0/profile.json) pins the model revisions and
server configuration.

```bash
python3 -B harnesses/proof_workshop/run.py --list-releases
python3 -B harnesses/proof_workshop/run.py --release 1.12.0 --verify
```

Verification checks every bundled file against the registered digest before
execution. The internal launcher is used by the public controller; it is not
the complete public workflow on its own. The final-pass driver only schedules
the existing refinement implementation. Experimental tool dispatch has been
removed from it and lives under [experiments](../../experiments/workshop_tools/README.md).

## Regression checks

From the repository root:

```bash
python3 -B -m pytest -q -p no:cacheprovider \
  tests/test_pipeline_regression.py tests/test_public_reproduction.py \
  tests/test_release_prompt_boundary.py benchmarks/test_environment_capture.py \
  harnesses/imo_proof_pipeline/tests/test_releases.py
```

The pipeline replay tests execute the real orchestration with scripted model
responses and network access blocked. Both certified and rejected repair briefs
exercise all four lanes through three passes. Final proof and prompt hashes
must match fixtures recorded before dependency cleanup. This verifies workflow
behavior without invoking models; it does not measure fresh mathematical quality.

The publisher utility remains available to assemble future versions with
explicit source inventories. Saved benchmark artifacts retain their original
release identities and are not relabeled as new runs.
