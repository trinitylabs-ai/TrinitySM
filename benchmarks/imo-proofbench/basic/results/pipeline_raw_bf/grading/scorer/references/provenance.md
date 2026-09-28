# Published prompt

Thang Luong et al., *Towards Robust Mathematical Reasoning*, arXiv:2511.01846v1,
Appendix B.5: https://arxiv.org/html/2511.01846v1#A2.SS5

`proof_autograder_prompt.txt` preserves the published wording and placeholders.
HTML markup, rendered list counters/artifacts and whitespace were normalized.
Hashes and retrieval provenance are in `source.json`. The paper is CC BY 4.0:
https://creativecommons.org/licenses/by/4.0/

Official dataset (also CC BY 4.0):
https://github.com/google-deepmind/superhuman/blob/main/imobench/proofbench_v2.csv

Its Problem, Solution and Grading guidelines fields are supplied verbatim except
for surrounding whitespace. Specific criteria override the general rubric.
Do not add the generic strict scorer's numeric caps or convert its old scores.

The published autograder permits 0 (Incorrect), 1 (Partial), 6 (Almost), 7 (Correct).
Human graders in the paper may award every integer 0–7. The paper's autograder
uses Gemini 2.5 Pro; this skill defaults to gpt-5.6-sol/xhigh. Rubric alignment
does not establish empirical agreement with human scores.

`evaluator_instructions.txt` is a local delivery wrapper, not part of the paper.
It replaces Codex's coding-agent instructions and restricts evaluation to the
supplied inputs. It adds no mathematical scoring criteria. Its hash, tool/skill
disablement settings, and the published prompt hash are part of result identity.
