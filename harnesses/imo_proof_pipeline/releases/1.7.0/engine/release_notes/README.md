# Frozen Basic solve harness

Release: `v263-v290-mtp4-original-recovery-20260912T141117Z`.

This snapshot preserves the running v263 frontend -> v290 R1-C1/C2/C3
statement-only Basic solve, its local source/prompt dependencies, queue runner,
support scripts, and recorded runtime settings. Every copied source file is
byte-identical to the working tree at freeze time. The P26 solve continues in
its existing tmux worker; freezing neither starts nor restarts inference.

Gemma and Qwen both use MTP=4. The repetition detector/fresh-retry policy is
removed. Original budget forcing, token-cap/format recovery, model roles,
sampling, four candidate lanes, and failed-lane continuation are preserved.
The independent P26 attempt's seeds and configuration are recorded separately
from the default queue settings in `runtime_profile.json`.

Future harness changes require a new release; do not edit this snapshot.
Run the queue from `source/` so local imports use this copy. Supply an external
problem-only input directory and a new writable output directory. The queue
requires `--execute-models` for live calls. Use `--dry-run` for inspection.
The recorded active command refers to the original live paths for provenance;
replace its launcher path with this snapshot's `source/scripts/run_v263_v290.py`
when starting a separate future run. Never resume the current run twice.

Historical and active run outputs, problem statements, proofs, gold references,
model weights, and installed environments are external. The copied grading
watcher is separate tooling with external dataset/skill/run dependencies, not
part of the solver's mathematical input. No new score is claimed by this freeze.
Environment versions are observations rather than an installation lock.

Verify with `python -B verify_release.py --verify /absolute/path/to/this/release`.
The manifest and SHA256SUMS bind all payloads; the ZIP provides a separate copy.
