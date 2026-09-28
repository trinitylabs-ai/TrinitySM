# Generation and evaluation boundary audit

Checked on 17 September 2026 against the public copy of implementation 1.7.0:
frontend `0.3.263`, backend `0.3.290+goldfree.1`, and the public Workshop Pipeline
controller. This audit concerns the core solver. It does not certify every
historical harness or the experimental tool extension.

## Current data flow

The experiment launcher supplies the statement-only problem directory. The
backend uses candidate proofs and internal reviewer records. Its loaded
`stage` is the bundled generic enhanced-review implementation; `stage.fusion`
resolves to the Python fusion protocol and `stage.resolver` to the revision
protocols bundled in the current engine source.

The current fusion builder accepts the problem, proof and three final reviewer
records. It has no grading-rubric argument. Its system prompt requires qualitative
verdicts: acceptance as written, acceptance with routine completion, repair
needed, or inconclusive. It explicitly excludes scores from its output.
The revision builder accepts the problem, proof and advisory fusion record.

An older Markdown fusion template with a rubric slot and numeric score format
remains inside the bundled dependency tree. The obsolete root copy was deleted. It is not the current fusion protocol. Some legacy prompt
files are read during dependency imports, so calling the whole directory dead
code would overstate the finding.

The internal instructions apply an Olympiad proof standard. This is disclosed
inference-time mathematical guidance. Similarity to an external correctness
standard does not establish that an external rubric, reference solution or
external grade was supplied to the solver. The current fusion path does not
perform numeric 0–7 self-grading.

## Executed checks

The bundled `test_generation_input_boundary.py` passes all **5 tests**. These
cover blocking an evaluator import during recovery-module import, limiting
input-binding reads to the submitted problem and proof, mutation rejection and
recovery preparation without reading a reference solution.

The additional [public boundary test](../../tests/test_release_prompt_boundary.py)
runs the bundled backend in a fresh interpreter. It blocks the named external
scorer import and reads of the two external grading-policy files, exercises the
actual fusion task builder, and constructs the actual fusion and revision
prompts. It injects both complete external policies and a synthetic reference
into extra case fields and verifies that the task allowlist excludes them. It
also checks that neither policy's content nor SHA-256 enters the constructed
prompts. **1 test passes.** No model call is made.

To reproduce these checks without writing a cache into the verified release:

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_release_prompt_boundary.py
cd harnesses/imo_proof_pipeline/releases/1.7.0/engine/source
python -B -m pytest -q -p no:cacheprovider \
  cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906/test_generation_input_boundary.py
```

These checks establish the tested import and prompt-construction boundaries.
They do not constitute a universal noninterference proof, an audit of every
model request, or evidence that a model has never seen a benchmark in training.
Policy files must be loaded by the test before its read guard is installed;
those reads are test fixtures, not generation reads.

## Remaining concerns

The bundled backend still contains `score_when_ready.py`, an independently
invoked evaluation watcher with a top-level gold-informed scorer import. The
normal generation import path does not load it in the executed tests. Its
co-location with solver code remains a packaging and auditability concern;
it is not evidence of an observed generation-time reference read. The dependency cleanup preserves the current engine bytes and does not
silently rewrite this recorded implementation. Dependency tracing also finds
an older evaluation helper imported by the shared terminal-composition module.
That inactive helper is another packaging concern. The negative import test
blocks one named evaluator; it does not prove that no evaluation helper is ever
imported. No external reference or policy reached the tested fusion prompts.

The strict external policy's instruction to compare with a reference belongs
to evaluation and is intentional. The relevant boundary is whether that policy
is passed to generation; the new test covers the current fusion/revision builders.
The submitted proof omits workflow commentary. External graders receive proof
text, while provenance and internal review records are stored separately.

The historical statement that a larger suite passed must not be treated as a
fresh result. Running the entire bundled backend suite here produced **64 passed,
22 failed** (86 collected). The failing tests rely on saved historical run
fixtures absent from this dependency bundle and fail at input binding or when
reading the consequently absent manifests. The full-suite result is not green.
The public statement-input preflight succeeds independently; a fresh GPU proof
run was not performed for this audit.

## Pipeline regression after dependency removal

The complete pipeline replay tests exercise actual draft orchestration, handoff,
three refinement passes and final exports with scripted model responses. Both
certified and rejected repair briefs pass for four lanes. The resulting proof
and system/user prompt hashes match the pre-cleanup fixtures. These tests make
no model calls and are separate from the historical fixture-dependent suite.
