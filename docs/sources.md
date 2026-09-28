# Problem sources and references

## IMO 2026

The six problems come from the **67th International Mathematical Olympiad**:

- [Official 2026 problem page](https://www.imo-official.org/problems/2026/)
- [Official English problem paper](https://www.imo-official.org/assets/documents/problems/2026/2026_eng.pdf)
- [Bundled statement-only inputs](../benchmarks/imo2026/problems) and
  [input hashes](../benchmarks/imo2026/catalog.json)

Local IDs `imo2026_p1` through `imo2026_p6` correspond to official Problems 1–6.
The stored JSON is the input used by the experiments. The project's strict
grading policy is separate from the official IMO jury. The official problem
page/PDF does not state an express redistribution license; [NOTICE](../NOTICE)
records this unresolved publication term rather than assigning the statements
the project's CC BY-NC 4.0 license.

The **reference solutions used by the external graders** come from the
[MechMath Agent Team's IMO2026 repository](https://github.com/MechMath/IMO2026/tree/47ff510110dd400c98aee2ead3be0f53f7b8ba04),
specifically `IMO2026/Q1/solution.pdf` through `IMO2026/Q6/solution.pdf`.
They are the team's reader-facing proofs, not official IMO jury solutions.
The associated project paper is Yichuan Cao et al.,
[*MechMath Agent Team: LLM Driven Agents for Mathematical Research*,
arXiv:2607.04394v1](https://arxiv.org/abs/2607.04394v1).
"Gold reference" names their role as evaluation inputs; it does not certify
their provenance as official solutions or imply an independent formal audit here.

The [reference source inventory](public_release/grading/imo2026_reference_sources.json)
pins each PDF URL and records both PDF and extracted-text hashes. All six PDFs
at the pinned revision reproduce the historical references using
`pdftotext -layout`, with surrounding whitespace stripped for grading.
The original retrieval revision was not recorded; the pinned revision was
verified on 18 September 2026 to contain the same PDF bytes.

**The reference PDFs and extracted text are external dependencies and are not
part of the release file set.** No license or redistribution grant was located
for these files at the checked revision. The paper's license is not assumed to
apply to them. Operators download them directly from upstream before grading;
local acquisition does not itself grant permission to redistribute them or send
them to a hosted evaluator. See [NOTICE §3b](../NOTICE) for the rights boundary
and [external-reference setup](public_release/grading/README.md#external-imo-reference-setup)
for the command and hash checks. Solver generation never downloads or reads them.

## IMO-Bench / IMO-ProofBench

The 30 Basic and 30 Advanced problems use Google DeepMind's **IMO-ProofBench**,
part of IMO-Bench:

- [Official project page](https://imobench.github.io/)
- [Official repository](https://github.com/google-deepmind/superhuman/tree/main/imobench)
- [Source CSV: proofbench_v2.csv](https://github.com/google-deepmind/superhuman/blob/main/imobench/proofbench_v2.csv)
- [Upstream license statement](https://github.com/google-deepmind/superhuman#license-and-disclaimer)

The recorded CSV SHA-256 is
`aa8b813dbd4068137e3d165e5da228f6e0e1cc85a91c37883e1791b954e43af0`.
All 60 stored statement strings match the CSV after removing surrounding
whitespace. 58 match exactly; PB-Advanced-002 and PB-Advanced-009 have surrounding
whitespace trimmed. The mathematical text is preserved.
Local IDs preserve the source `Problem ID` column. The
[Basic](../benchmarks/imo-proofbench/basic/catalog.json) and
[Advanced](../benchmarks/imo-proofbench/advanced/catalog.json) catalogs record
the JSON file hashes. Inputs contain statements only; reference solutions and
grading guidelines remain in separate evaluation directories.

Reference proofs come from the CSV's **`Solution`** column; the published B.5
evaluation additionally uses **`Grading guidelines`**. All 60 references in the
strict-v2 study match `Solution` after stripping surrounding whitespace.
The [verified source revision](https://github.com/google-deepmind/superhuman/blob/80b2527a0b4e4bfc6a8b28825fadbdcfdd6048a1/imobench/proofbench_v2.csv)
has the CSV hash recorded above. These CC BY 4.0 materials remain bundled with
their attribution; the MechMath exclusion does not apply to them.

The upstream repository licenses non-software materials under **CC BY 4.0**.
The project converts rows to per-problem JSON, retains source attribution and
uses the paper's Appendix B.5 rubric with a different recorded grader.

## Papers and method references

| Reference | Role in this project |
|---|---|
| Thang Luong et al., **Towards Robust Mathematical Reasoning** (2025), [arXiv:2511.01846](https://arxiv.org/abs/2511.01846) | IMO-Bench dataset and grading methodology. The copied ProofAutoGrader prompt comes from [v1, Appendix B.5](https://arxiv.org/html/2511.01846v1#A2.SS5). |
| Xingyu Dang, Rohit Agarwal, Rodrigo Porto, Anirudh Goyal, Liam H Fowl and Sanjeev Arora, **Escaping the Cognitive Well: Efficient Competition Math with Off-the-Shelf Models** (2026), [arXiv:2602.16793v2](https://arxiv.org/abs/2602.16793v2), 12 June 2026 | Workshop Draft adapts v2, Appendix F.2's multi-persona dialectic prompting: distinct planning, skeptical, deductive-checking and coordinating roles, critique-and-revision rounds, and explicit expansion of omitted steps. The implementation mapping below identifies the active code. |
| Niklas Muennighoff et al., **s1: Simple test-time scaling** (2025), [arXiv:2501.19393](https://arxiv.org/abs/2501.19393) | Extended reasoning background. The repository's continuation and recovery policies are its own recorded implementation, not a reproduction of s1 training or benchmark scores. |
| Gemma Team, **Gemma 4 Technical Report** (2026), [arXiv:2607.02770](https://arxiv.org/abs/2607.02770) | Model-family reference for the Gemma model and MTP assistant. |

The [Qwen3.6-27B model card](https://huggingface.co/Qwen/Qwen3.6-27B) is the
provider reference for Qwen's checkpoint. Exact model revisions, download links
and licenses are listed in [models.md](models.md). BibTeX entries for the papers
are provided in [references.bib](references.bib).

These citations identify datasets, rubrics and methodological background.
They do not imply that the authors endorse this implementation or that this
release reproduces their reported results.

### Cognitive Well ideas used in Workshop Draft

The direct connection is the paper's dialectic solver design in
[v2, Section 2 and Appendix F.2](https://arxiv.org/html/2602.16793v2).
These are roles within the model's drafting prompt; the separate Gemma/Qwen
review calls are a different part of Workshop Pipeline.

| Idea used | Current implementation |
|---|---|
| Divide proof construction among planning, criticism, deduction checking and synthesis roles. | The [frozen drafting prompt](../harnesses/imo_proof_pipeline/releases/1.7.0/engine/source/cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827/run.py#L66) names Classicist, Visionary, Experimenter, Momus, Veritas and Chief Architect. `build_frozen_raw_prompts` supplies it to the active drafting calls. |
| Challenge a strategy, revise its proof, and change strategy when a fatal flaw survives. | The same prompt specifies ideation, skeptical critique, deductive checking and synthesis, with at most three internal rounds. These internal rounds are distinct from the pipeline's three later refinement passes. |
| Replace hand-waved or skipped deductions with explicit reasoning. | The drafting prompt asks for missing steps to be expanded. The [lazy-check call](../harnesses/imo_proof_pipeline/releases/1.7.0/engine/source/cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823/run_six_candidate_lazy_test.py#L85) uses the inherited `lazy_phrasing` prompt and routes flagged proofs to conditional expansion. |

The current core workflow does not run the paper's separate conjecture-and-negation
solver branches or global lemma-memory loop. The mixed Gemma/Qwen reviewers,
fusion and acceptance/repair audits are this project's refinement design; the
paper citation above specifically credits the dialectic prompting used by Draft.

## Acknowledgments

We thank the [International Mathematical Olympiad Association](https://www.imo-official.org/organisation/),
host organizers and problem setters for the IMO competition and its problems,
and [Google DeepMind and the IMO-Bench contributors](https://github.com/google-deepmind/superhuman/tree/main/imobench)
for making the benchmark and grading methodology available. We also acknowledge
the authors of the methodological and model papers cited above.
