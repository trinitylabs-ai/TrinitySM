# Harness B 1.12.0: progress-aware final selection

Promotes both evaluated selection changes while preserving immutable B 1.11.0.
R2/R3 uses the comparative-progress prompt and requires all four explicit raw
ACCEPT_CANDIDATE decisions (Gemma/Qwen, independent forward/reverse calls).
Proof/request/response bindings and unambiguous decisions remain mandatory.
Body status consistency is retained as a diagnostic; it no longer vetoes a raw
unanimous decision. Missing R3 retains R2; missing R2 retains the earlier proof.

The cross-lane voter uses the tested symmetric obligation-audit prompt, all six
pairs in both independent orders on both models, twelve concurrent calls per
model, pooled forced-choice votes and the pre-recorded seed tie order. At 600
seconds per logical comparison it uses a valid initial answer, or at most one
answer-only continuation (thinking off, 8192 tokens, 120 seconds), with no fresh
timeout retry. A failed continuation leaves selection incomplete. A missing
checks label can be restored only from existing explicit line-cited evidence.

Original 0.1 lazy-check / 0.4 full-proof expansion, raw generation, B refinement
BF, three refinement stages, model identities, sampling, seeds, and ordinary BF
cues are retained. No reference solutions or external grades enter selection.

Evidence: imo2026_raw_unanimous_20260922T111000Z and
imo2026_cross_lane_audit_prompt_20260922T124815Z. P2-P6 chosen-grade sum was
21.5 -> 22/35, unequal-grade vote agreement 47/80 -> 52/80. These are development
results; the latter test also changed timeout behavior on P5/P6. No new full
end-to-end benchmark or oracle improvement is claimed by this release.
