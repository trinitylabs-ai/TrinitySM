# Reproduction artifacts and release cleanup

The release keeps the current Workshop Pipeline and its required bundled
dependencies. The [registry](../../harnesses/imo_proof_pipeline/releases/index.json)
contains default B 1.12.0 and preserved earlier engines for historical replay.
Obsolete standalone harness folders have been removed. The experimental tool runtime, dependencies, tests
and documentation live under [experiments](../../experiments/workshop_tools/README.md).

Generated benchmark proofs, grades, model responses, prompts, request settings,
seeds and provenance remain in their existing locations. Raw runtime logs, log
directories and compressed log archives are excluded. Historical metadata may
refer to omitted working directories; it is evidence of the original runs,
not an assertion that every historical run can be resumed from this checkout.

The [legacy path inventory](legacy_paths.json) preserves 72 former symlink
targets. Those targets were all absent from the release checkout; only the
broken aliases were removed. Included proofs, grades, manifests and frozen
engines remain in place. This inventory is provenance, not a resume plan.

## Verify

Follow the root [README](../../README.md) for local setup and the complete
statement-to-proof workflow. No Codex or hosted inference service is required.

```bash
python3 -B scripts/reproduce.py
python3 -B harnesses/proof_workshop/run.py --release 1.12.0 --verify
python3 -B experiments/workshop_tools/run.py --verify
```

The score verifier checks artifact hashes, proof-to-grade bindings and score
arithmetic, then recomputes the core matrices, ablations and per-proof tool tables
from saved grades. The release `--verify` commands check source-inventory
integrity. These checks do not assess mathematical correctness or rerun external
grading. Experimental records do not contribute to the core matrices.

The [validation record](release_validation.json) records pipeline replay tests,
source integrity and artifact preservation. The [boundary audit](generation_boundary_audit.md)
describes the tested generation/evaluation separation and its limits.
[Sanitization provenance](sanitization.md) records earlier location redactions.

## Research history and snapshot publication

Cleanup applies to the release branch's current tree. It does not modify other
research branches or erase files from earlier commits. The research repository
retains its original history. A separately published snapshot can start with a
new root commit and need not include that history. Research commit IDs and old
paths in provenance records do not imply that those objects are included in a
snapshot checkout. This cleanup does not publish or rewrite either repository.
