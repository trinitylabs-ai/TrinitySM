# Grading policy provenance

Both schemes use `gpt-5.6-sol` with `xhigh` reasoning. They remain separate policies.

In these policies, "gold reference" means the MechMath team's third-party IMO
2026 solution, or the DeepMind dataset's `Solution` entry for IMO-ProofBench.
It is an evaluation input, not an assertion of official IMO jury authorship.
The [source inventory](imo2026_reference_sources.json), [source notes](../../sources.md)
and [NOTICE §3b](../../../NOTICE) identify the external IMO references and their rights.

## External IMO reference setup

The release file set contains source metadata and hashes, not MechMath solution
PDFs or extracted reference bodies. No license or redistribution permission was
located at the pinned upstream revision. The associated paper's license is not
assumed to cover the repository's PDFs. Our project license does not apply to
them, and a download command grants no additional rights. Before using them,
the operator must determine the applicable permissions or other lawful basis
for downloading, processing and transmitting them to a chosen external service.
This project does not establish that noncommercial use or local acquisition
alone permits those acts.

After that determination, install Poppler's `pdftotext` (for example,
`sudo apt-get install poppler-utils` on Ubuntu) and explicitly run:

```bash
python3 scripts/prepare_imo_references.py download
python3 scripts/prepare_imo_references.py verify
```

The first command fetches six PDFs directly from the pinned upstream commit,
checks their SHA-256 hashes, extracts text with `pdftotext -layout`, checks the
exact extracted and normalized hashes, and restores ignored local input paths
for the recorded grading manifests. It never starts a grader or changes a
submitted proof. `prepare` repeats extraction from the local cache without
network access. Extraction differences fail the hash check rather than silently
changing the evaluator inputs; the inventory records the verified Poppler version.

The cache is under `.workshop/external-references/`; the extracted inputs are
also Git-ignored. Do not include either, or grader request logs, in releases.
Git ignore rules do not remove older Git objects: before publishing a repository
history, run `python3 scripts/audit_release.py --history` and resolve any
historical reference copies. Reading saved score matrices and generating proofs
do not require these downloads. Verifying or rerunning a complete grading
prompt requires the local reference text.

The current [two-pass v2 study](../../../benchmarks/reports/strict_v2_consistency_20260918T064715Z/README.md)
uses the same reference hashes. Its instructions apply after this setup.
Attribution and download instructions live here, outside the frozen policy
strings, so the policies' recorded hashes and mathematical grading criteria stay intact.

## IMOBench

[proof_autograder_prompt](imobench_b5_prompt.txt) preserves the published wording
and placeholders from Thang Luong et al., *Towards Robust Mathematical Reasoning*,
[arXiv:2511.01846v1, Appendix B.5](https://arxiv.org/html/2511.01846v1#A2.SS5).
The prompt's HTML markup, rendered list artifacts and spacing were normalized
when retrieved on 12 September 2026. The paper is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The official per-problem grading guidelines and reference solutions come from
the [IMOBench ProofBench dataset](https://github.com/google-deepmind/superhuman/blob/main/imobench/proofbench_v2.csv),
also licensed CC BY 4.0. Specific guidelines override the general prompt.
The dataset is identified by SHA-256
`aa8b813dbd4068137e3d165e5da228f6e0e1cc85a91c37883e1791b954e43af0`.

Allowed autograder scores are 0, 1, 6 and 7. This report uses a different grader
from the paper's Gemini 2.5 Pro autograder and does not assert agreement with the
paper's human scores.

Exact prompt-file SHA-256:
`e71ec3a05b6fa906e27fa7f95dabe5f950786eafa921ba526afe7596af809b4c`.

## Strict Olympiad v1 — historical evidence

[strict_olympiad_policy.txt](strict_olympiad_policy.txt) is the exact local strict
policy string used for the historical single-grade IMO 2026 evidence, exported from the scorer's
`STRICT_POLICY` constant. It allows scores 0 through 7 and includes explicit
caps for load-bearing omissions and invalid central inferences.

Exact policy SHA-256:
`1a8c5d02a7bd84a53ad011cf889ceaaca7ff94166536565bda49082649781ecf`.

This is the project's strict gold-informed evaluation policy, not an official
IMO jury rubric. It must not be substituted for the IMOBench rubric.

## Strict Olympiad v2 — current IMO reporting

[Version 2](strict_olympiad_policy_v2.txt) applies the six proposed rules with
the agreed clarifications: distinguish a false answer from a failed construction;
require a correct reduction, an explicit remaining equality, and verification of
its truth for the substantial-gap score of 4; distinguish false statements from
omissions; respect quantifiers; and apply the lowest applicable score ceiling.
The exception for an incorrect inline justification requires the needed fact to
be established independently elsewhere in the submitted proof.

Rules A and C change scoring severity. Current IMO core, ablation and tool
matrices use the two retained v2 grading passes. The core portfolio selects
the complete pass with the lower total Average; ties select pass 1. Every
problem row and Oracle@4 value comes from that same pass, so the problem rows
add to the portfolio totals. The IMO ablation uses **pass 1 for all three
configurations**, for both Average and Oracle@4. Captions identify the selected
pass and the other pass's totals.
Tool rows use the minimum score for each input and rewrite separately.
The [portable evidence](../imo2026_v2_lowest.json) preserves both grades and
the historical v1 evidence remains available. ProofBench and its ablations
continue to use IMOBench B.5; strict-v2 ProofBench results were deleted.
The v2 policy SHA-256, over UTF-8 text with surrounding
whitespace stripped, is
`d1c93550ca49f52a35fe4c0eb0b1ccca9534e9112d928002667e404c367de4e4`.

The earlier single-pass [audit inputs](../../../benchmarks/imo2026/results/strict_v2_20260918T061000Z/manifest.json)
freeze 24 selected core proofs and three P2 experimental rewrites. Every proof,
statement and reference matches its v1 input. The task manifest sent to the
scorer contains only these mathematical inputs and their hashes; the comparison
manifest containing previous scores is not sent to the evaluator.

Run the separate external audit from the repository root with an authenticated
Codex CLI and access to `gpt-5.6-sol`:

```bash
python3 scripts/score_imo_v2.py \
  --generic-task-manifest benchmarks/imo2026/results/strict_v2_20260918T061000Z/grading/tasks.json \
  --output-dir benchmarks/imo2026/results/strict_v2_20260918T061000Z/grading/work/repeat_001 \
  --workers 4 --reasoning-effort xhigh
```

Choose a new output directory for every repeat. The adapter reuses the archived
strict scorer's prompt, schema, and hash binding; its dependencies are verified
by hash. The v2 contract permits a score of 5 with `routine_direct` repair under
Rule C. Tools, skills, external resources and prior agent context are disabled,
and each successful evaluator transcript is checked for zero tool calls and
one completed grading turn. Runtime transcripts stay in the ignored `work/`
directory. Model grades can still vary; one selected grade per proof under each policy
does not isolate policy effects from evaluator variation.

The v2 contract also allows a full-credit response to record a cosmetic issue
that satisfies Rule C's deletion-test exception. The initial audit adapter was
too restrictive here; affected responses are recovered from the preserved
transcripts without another call. Publication always selects the first valid
isolated response chronologically, never the highest score, and records any
automatic extra attempt.

After the original batch finishes, publish its portable results and comparison:

```bash
python3 scripts/report_strict_v2.py --publish
```

Verify the published audit offline with `python3 scripts/report_strict_v2.py`.
For another experiment, `--run` selects its directory and frozen manifests;
`--work-results` selects its completed private grading output. Keep each
experiment's published results in its own directory.
