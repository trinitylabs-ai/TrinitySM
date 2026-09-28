# Dependency asset packaging correction

This release derives from `v263-v290-mtp4-original-recovery-20260912T141117Z`. It restores the original lazy
in-place proof expansion prompt and 20 original dependency schemas omitted by
the static import packager. It adds no problem-specific content. Every payload
already present in the original release, including every Python file and
existing prompt, remains byte-for-byte identical. The original release and ZIP
are preserved. The new release identity and added asset hashes are in freeze.json.

The solver's MTP=4 settings, sampling, seeds, caps, budget forcing, original
recovery, and lane continuation are unchanged. The launcher uses a new output
directory for a future manual run; this packaging operation starts no models
or experiments and performs no grading. The launcher has no Codex calls.

The preserved runtime_profile.json, environment.json and original README record
the original freeze, not a new run. The removed repetition policy described in
that README is the new global transport detector/fresh-retry policy. The
original Reviewer-1 detector (8-128-token patterns, three repeats) remains.

The live packaging utility now discovers prompt and schema directories in
imported dependencies. Its old frozen copy remains unchanged for provenance.
Validation includes the real conditional expansion path with a mocked model
response, a package asset regression test, release checksums, and queue dry run.
