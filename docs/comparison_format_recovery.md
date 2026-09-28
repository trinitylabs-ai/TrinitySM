# Deterministic comparison recovery

This guard recovers the observed duplicated-Markdown comparison failure without
changing prompts, model calls, proof text, grades, or a running frozen release.

The final `# Proof comparison` block must be the sole complete comparison and
pass the original strict parser. Earlier blocks must have no Decision section.
Every explicit Winner must be a well-formed A/B choice agreeing with the final
choice. Conflicts, multiple completed answers, incomplete final answers, quoted
code blocks, transport truncation, and request/proof binding mismatches fail.
No preference is inferred from prose or external grades.

The additional `explicit-winner-proof-prefix-v1` rule accepts a single explicit
`Winner: Proof A` or `Winner: Proof B` by deleting only the literal `Proof `
prefix. All remaining text must pass the unchanged strict parser, including
exactly one winner. This rule does not accept ties, alternate choices, or prose
from which a preference would need to be inferred.

The third rule, `missing-checks-heading-existing-inline-line-citations-v2`,
recovers one omitted **Decisive checks** heading. It copies the existing
**Qualifications and supplied repairs** bullet list verbatim under that heading.
There must be at least two substantive bullets, each at least 80 characters and
already citing positive proof-line numbers or ascending ranges. Citations may
appear at the start or inside a bullet. A present-but-empty heading, missing
citations, descending ranges, fenced content, duplicate/out-of-order sections
or a response that still fails the strict parser is rejected. The winner and
all original text remain unchanged; no mathematical content is invented.

`restore_checks_label()` in the reusable module implements this v2 rule for
both the current recovery monitor and `export_proofbench_final.py --verify`.
Thus live recovery and offline replay use the same line-citation checks. The
older v1 helper embedded in frozen release 1.12.0 requires prefix-form citations;
it remains an unchanged historical implementation and is not used to replay v2.

The [final ProofBench evidence](results/proofbench_b112_final_20260926/README.md)
includes the Advanced-003 original response, normalized response and recovery
receipt. Its former `repair_script_sha256` referred to an unpublished script and
has been removed from the portable scorecard. Verification instead replays the
recorded operation, checks the receipt's hashes and winner, and requires the
same normalized response bytes. This establishes replayability, not possession
of the original script.

The reusable unfrozen parser lives in
`harnesses/cross_lane_voter/{validation,mechanical_recovery}.py`. Historical
release 1.12.0 remains frozen. The independent suite monitor applies the same
rules after completed generation and grading, so the ongoing run needs no
restart or changed pins. It recovers saved answer-only timeout continuations
with the duplicate-block failure, and bound canonical responses with these
supported format errors. Other failures stay unresolved.

Run a read-only preflight (temporary derived response files only):

```sh
python -B scripts/recover_proofbench_votes.py --config /path/to/suite/config.json --problem-id PB-Basic-008
```

Add `--write` to save a bound recovery receipt, verbatim normalized block,
complete original response, full recomputed vote table, and chosen proof, then
refresh problem and suite reports. Add `--watch` and run detached to handle
subsequent completed problems automatically. The monitor uses no network and
exits after the suite controller exits. It is locked against duplicate monitors.
Repeated collection revalidates original evidence and is idempotent.

Artifacts per problem:
`selection_recovery/unique_final_comparison_v1/` or
`selection_recovery/explicit_comparison_format_v2/`. Native generation failures,
source manifests, raw responses, grades, and original reports remain preserved.
The effective selection and diagnostic order-disagreement rate are linked from
`reports/REPORT.md`; the original manifest intentionally retains native history.

Monitor files: `<suite>/vote_recovery/{status.json,monitor.log,monitor.pid}`.
Stopping only this monitor leaves the solving/grading controller running.
Future pinned suites can use this same monitor; a future frozen release must
explicitly include the parser change rather than modifying an existing release.
