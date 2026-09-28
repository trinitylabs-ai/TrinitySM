# IMO 2026 P2 — t07_r02, v349

Final strict score: **6/7 — minor_gap**. Original source: 4/7; previous harness rewrite: 6/7.

The coordinate reduction, circumcenter computation, target polynomial T, and explicit algebraic certificate form a correct and essentially complete proof. The appendix supplies a finite verifiable certificate showing that the three angle polynomials and two nonvanishing guards imply T=0. The sole material omission is the short but necessary orientation/branch verification behind the angle-polynomial encoding; this is directly repairable from the convexity hypotheses.

First issue: The unsigned-angle equalities are converted to signed cross–dot equations without explicitly proving, for each pair, that the two oriented cross products have the same sign. Interiority gives the required ray orders, but Step 4 only asserts this generically.

Drafts compiled: 8/11; semantic audits accepted: 7; exact certificates: 1; new real-branch certificates: 0. Both synthesis and the final-revision stage ran; the published proof is the harness's accepted final output.

Length: 3,357 whitespace-separated words including mathematical notation; 272 lines.

Model: gpt-5.6-sol; effort: xhigh; failed grading calls: 0. Each isolated grader received only the problem, reference, and submitted proof. Policy SHA-256: `1a8c5d02a7bd84a53ad011cf889ceaaca7ff94166536565bda49082649781ecf`.

[Final proof](../proofs/imo2026_p2/t07_r02/tool_rewrite.md) · [Strict grade](strict_score.json) · [Run summary](run_summary.json)
