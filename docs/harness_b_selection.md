# Harness B 1.12.0: progress-aware final selection

New runs use the frozen B 1.12.0 generation engine with a captured Qwen-only
cross-lane selection policy. Earlier runs retain their recorded selector.
R2/R3 uses the comparative-progress prompt and requires all four explicit raw
ACCEPT_CANDIDATE decisions (Gemma/Qwen, independent forward/reverse calls).
Proof/request/response bindings and unambiguous decisions remain mandatory.
Body status consistency is retained as a diagnostic; it no longer vetoes a raw
unanimous decision. Missing R3 retains R2; missing R2 retains the earlier proof.

The cross-lane voter uses the tested symmetric obligation-audit prompt, all six
pairs in both independent orders with Qwen only: twelve comparisons and up to
twelve concurrent calls, with the pre-recorded seed tie order. At 600
seconds per logical comparison it uses a valid initial answer, or at most one
answer-only continuation (thinking off, 8192 tokens, 120 seconds), with no fresh
timeout retry. A failed continuation leaves selection incomplete. A missing
checks label can be restored only from existing explicit line-cited evidence.

Original 0.1 lazy-check / 0.4 full-proof expansion, raw generation, B refinement
extended reasoning, three refinement stages, model identities, sampling, seeds, and ordinary extended reasoning
cues are retained. No reference solutions or external grades enter selection.

Historical B 1.12.0 development evidence: imo2026_raw_unanimous_20260922T111000Z and
imo2026_cross_lane_audit_prompt_20260922T124815Z. P2-P6 chosen-grade sum was
21.5 -> 22/35, unequal-grade vote agreement 47/80 -> 52/80. These are development
results; the latter test also changed timeout behavior on P5/P6. No new full
end-to-end benchmark or oracle improvement was claimed by those trials.

## Use and verify

B 1.12.0 is the default of the public pipeline and benchmark launchers.

```bash
python3 -B harnesses/proof_workshop/run.py --verify
python3 -B harnesses/proof_workshop/run.py --release 1.12.0 --verify
```

All lane finals and the separately selected problem winner are retained. The
vote report includes every model/order choice, order-disagreement rates, actual
concurrency, and timeout fallback events. Existing grades and results remain
attached to their original run IDs. Promotion itself does not launch model calls.
The subsequent fresh P1–P6 runs and their two-pass grading are complete; see the
[six-problem results and evidence](results/imo2026_b112_selection_20260922/README.md).
All six used this frozen B 1.12.0 release with the same recorded settings.
Earlier reselection results retain their provisional development status.
The current [Qwen-only scores](results/qwen_selection_20260928/README.md) re-tally
those archived final comparisons with the original proofs and grades.
