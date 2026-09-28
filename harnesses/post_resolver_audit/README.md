# Post-resolver audit validation

Decision (2026-09-21): retain the auditor with mechanical validation and independent
forward/reverse calls. See [the retention decision and evidence](RETENTION_DECISION.md).

This directory preserves the auditor used by earlier B releases, including
[B 1.11.0](../../docs/harness_b_audited.md). The current default
[B 1.12.0](../../docs/harness_b_selection.md) runs its frozen auditor with the
raw-unanimous acceptance rule; body-consistency checks are diagnostic there.
The historical behavior described below and completed experiment prompts remain
preserved in this directory.

V2 treats model-echoed proof hashes as optional diagnostic text. It checks unique
changed-block coverage, required fields, and consistency of an ACCEPT with every
reported obligation, preservation, scope and repair status. Invalid audits keep R2.

Before adopting a verdict, `verify_audit_binding(root, task, result, call)` verifies
the actual proof files, pinned prompt and input packet, task/result identity,
transport metadata, saved request files and response content hashes. Missing or
mismatched model-echoed hashes never substitute for these code-level checks.
`validate_audit` alone validates record content, not request identity or mathematics.

`select_candidate` requires both independent orders for each requested model.
The combined strategy requires four valid approvals.

`revalidate.replay(roots, output)` revalidates completed saved responses, including
partially completed runs, without model or grading calls. It writes selections
before reading evaluation-only grades, supports single-pass B.5 and two-pass
Strict Olympiad labels, and keeps the grading regimes in separate reports. V1 is
preserved in `validation_v1.py` for same-response before/after comparisons.

The original two-pass replay CLI is also supported. Both replay paths verify
request/response bindings in code. Saved response text, prompts and prior run
artifacts remain unchanged.

`live.py` prepares bound statement/proof inputs, runs both auditors in both orders
with up to twenty-four logical calls concurrent (twelve Gemma and twelve Qwen), and
revalidates saved results during collection. Each changed lane still receives
exactly four independent calls. B 1.9.0 retains its original four-slot scheduler.
The live worker has no grading imports and resumes without repeating completed calls.
