# Harsh gold-informed rubric

## Isolation and provenance

- Use one isolated, ephemeral, read-only Codex call per proof.
- Use grader `gpt-5.6-sol`; default to `xhigh` reasoning.
- Supply only the problem, the gold reference, and the submitted proof.
- Record the policy hash emitted by the scorer. Treat it as the authoritative
  identity of the exact rubric used in a run.

Gold-informed means the reference helps detect mistakes and recognize equivalent
solutions. It does not authorize filling omissions in the submitted proof.

## Score scale

- **7:** Complete and correct as submitted by normal Olympiad jury standards.
- **6:** Correct proof with only a genuinely minor, directly checkable omission.
- **5:** Mostly complete proof with one localized nontrivial but bounded repair.
- **4:** Meaningful coherent strategy, but a load-bearing derivation is missing or
  unverified.
- **3:** Major central gap, unsupported decisive claim, or serious invalid step,
  despite meaningful progress.
- **1--2:** Limited correct progress.
- **0:** No meaningful progress.

## Mandatory strict caps

- Cap at **4** when the proof merely asserts a decisive identity or simplification
  whose verification requires a substantial multi-step calculation or elimination.
- Cap at **3** when a false or unjustified decisive inference replaces the central
  argument.
- Do not award **5** merely because the same strategy might be repairable. The
  localized nontrivial lemma or calculation must already be substantially present.

Accept routine one-line algebra, standard named results, and genuinely equivalent
approaches. Be exacting about load-bearing steps, not stylistic completeness.

## Reporting discipline

Identify the first decisive defect rather than listing cosmetic weaknesses. Keep
dependency impact distinct from repair length: a short missing argument can still
be load-bearing, while a routine uniquely determined expansion can remain minor.
Use the harsh score as a separate audit result; do not overwrite earlier calibrated
scores.
