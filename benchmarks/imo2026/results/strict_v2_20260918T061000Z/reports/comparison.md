# IMO 2026: separate strict-v2 audit

The submitted mathematics is unchanged. V2 uses Rules A--F with the agreed
clarifications. The original v1 scores remain in the release matrices.

Evaluator: `gpt-5.6-sol`, `xhigh`; independent calls by submitted proof,
four workers, with retries disclosed below. Each selected response passed
the zero-tool-call isolation audit.
V2 policy SHA-256: `d1c93550ca49f52a35fe4c0eb0b1ccca9534e9112d928002667e404c367de4e4`.

Single grades under each policy do not separate policy effects from grader
variation. These are local strict grades, not official IMO jury scores.

## Core proofs: v1 → v2

| Problem | t07_r01 | t07_r02 | t10_r01 | t10_r02 | Average | Oracle@4 |
|---|---:|---:|---:|---:|---:|---:|
| P1 | 7 → 7 | 7 → 7 | 7 → 7 | 6 → 7 | 6.75 → 7.00 | 7 → 7 |
| P2 | 3 → 3 | 4 → 4 | 3 → 3 | 2 → 3 | 3.00 → 3.25 | 4 → 4 |
| P3 | 1 → 2 | 2 → 2 | 2 → 1 | 2 → 2 | 1.75 → 1.75 | 2 → 2 |
| P4 | 6 → 6 | 6 → 5 | 3 → 2 | 4 → 6 | 4.75 → 4.75 | 6 → 6 |
| P5 | 7 → 7 | 3 → 3 | 6 → 3 | 7 → 7 | 5.75 → 5.00 | 7 → 7 |
| P6 | 2 → 2 | 3 → 3 | 3 → 3 | 3 → 3 | 2.75 → 2.75 | 3 → 3 |
| Total /42 | — | — | — | — | 24.75 → 24.50 | 29 → 29 |

Each per-problem score is out of 7. Average is the mean of the four
fixed submissions; Oracle@4 is their maximum. Totals sum across six problems.

## P2 experimental rewrites

These three rewrites are reported separately from the 24 core proofs.

| Candidate | Same rewrite: v1 → v2 | V2 input → rewrite |
|---|---:|---:|
| t07_r01 | 3 → 5 | 3 → 5 |
| t07_r02 | 6 → 5 | 4 → 5 |
| t10_r01 | 3 → 5 | 3 → 5 |

## Individual assessments

Every v2 score and verdict follows. For scores below 7, the first issue is
the evaluator's recorded assessment, not an additional human adjudication.

### imo2026_p1 · t07_r01 · core

**7 → 7/7; pass.** [Submitted proof](../proofs/imo2026_p1/core_t07_r01.md) · [V2 grade](../grades/imo2026_p1/core_t07_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/72be8eb7d3a16b3e6a8a2ac12ab9ef82058515ec487f7453bd608b1508256153.json)

### imo2026_p1 · t07_r02 · core

**7 → 7/7; pass.** [Submitted proof](../proofs/imo2026_p1/core_t07_r02.md) · [V2 grade](../grades/imo2026_p1/core_t07_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/a87548aa372dd9ea6fa391dfdb7059570172fa04effedb49f7e157f8bfbfd110.json)

### imo2026_p1 · t10_r01 · core

**7 → 7/7; pass.** [Submitted proof](../proofs/imo2026_p1/core_t10_r01.md) · [V2 grade](../grades/imo2026_p1/core_t10_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/2000243833f62c510d7734e5a6140d69387a73f5aa03780efef3515d751fc119.json)

### imo2026_p1 · t10_r02 · core

**6 → 7/7; pass.** [Submitted proof](../proofs/imo2026_p1/core_t10_r02.md) · [V2 grade](../grades/imo2026_p1/core_t10_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/45e53bd96ec745085c9afdcc6c9752468b07c141d7f3c2c85034fe6ce61d3c97.json)

### imo2026_p2 · t07_r01 · core

**3 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p2/core_t07_r01.md) · [V2 grade](../grades/imo2026_p2/core_t07_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/09210773bcd3c5313e9ea23539fc744a2da319258a07619072cde906d3d3ce8e.json)

The first load-bearing error is a sign reversal when expanding P·(b−c). The cross terms should be +kc sin(phi_L)−lc sin(A−theta_K), whereas the submission obtains their negatives. This is a false load-bearing calculation under Rule C. More importantly, the subsequent conclusion PB=PC is only asserted, triggering Rule E and the lower cap of 3.

### imo2026_p2 · t07_r02 · core

**4 → 4/7; substantial_gap.** [Submitted proof](../proofs/imo2026_p2/core_t07_r02.md) · [V2 grade](../grades/imo2026_p2/core_t07_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/8949bbf3cf2be5423b3334d99a0fe19b8bbb085fcae0207d0198a13ac0aef7c9.json)

The proof's final step merely asserts that the displayed expression for bz-cx simplifies to (b^2-c^2)/4 using the remaining angle constraints; it never translates those constraints into equations or performs the required elimination.

### imo2026_p2 · t10_r01 · core

**3 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p2/core_t10_r01.md) · [V2 grade](../grades/imo2026_p2/core_t10_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/7d05db928c9dd1072ab5217cdd76b911cfe0552662542b9777ebca42204e3bd7.json)

After correctly reducing the goal to the displayed trigonometric identity equivalent to O'B=O'C, the submission merely asserts that the remaining angle conditions force this identity. Neither that compatibility claim nor the asserted uniqueness of K and L is proved. This is the decisive central inference and invokes Rule E, capping the score at 3.

### imo2026_p2 · t10_r02 · core

**2 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p2/core_t10_r02.md) · [V2 grade](../grades/imo2026_p2/core_t10_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/0473e2984f4f7bd438958d8dcd42d506965b6e0dacf44a67fe03bab14283ea03.json)

The first decisive error is the reversal of the angles of the medial triangle: since triangle AMN is similar to triangle ABC, ∠ANM=∠C and ∠AMN=∠B, not the other way around. Thus the asserted cyclicity criteria θ_K=γ−B and θ_L=β−C are false. This is a load-bearing false statement under Rule C.

### imo2026_p3 · t07_r01 · core

**1 → 2/7; incorrect.** [Submitted proof](../proofs/imo2026_p3/core_t07_r01.md) · [V2 grade](../grades/imo2026_p3/core_t07_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/ab97ed8995b70dc8d6e891826642f0b33e08b5debbddab59d11f8bc68a617bb0.json)

The proposed lower-bound strategy already fails at n=2: from Liu's pieces (3/5,1/5,1/5), Xiang can bisect the 3/5 piece, leaving lengths (3/10,3/10,1/5,1/5), so Liu receives only 1/2 rather than 3/5. Moreover, the true value at n=2 is 4/7, so the claimed final answer 3/5 is false; Rule A caps the score at 2.

### imo2026_p3 · t07_r02 · core

**2 → 2/7; incorrect.** [Submitted proof](../proofs/imo2026_p3/core_t07_r02.md) · [V2 grade](../grades/imo2026_p3/core_t07_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/2c60c460334f3a9fba7c641b6cbea7e713b8e096b9819af72912c5b4e9c608c2.json)

The first decisive defect is the false central claim that, for Liu's equal intervals, Xiang minimizes the alternating sum by splitting n different intervals in half. For n=1, Xiang may make no mark, leaving two pieces of length 1/2, so Liu receives 1/2<2/3. Thus the proposed lower-bound strategy already fails; this is an unsupported central inference under Rule E.

### imo2026_p3 · t10_r01 · core

**2 → 1/7; incorrect.** [Submitted proof](../proofs/imo2026_p3/core_t10_r01.md) · [V2 grade](../grades/imo2026_p3/core_t10_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/9af286c73d5d5d23a4229a952118225062924afbcebdd7142ebb581a950c2870.json)

The first decisive error is the asserted maximization identity for the alternating discrepancy. Alternating signs in sorted order do not maximize the signed sum among all sign assignments of the prescribed cardinalities. For example, for (2/5,2/5,1/10,1/10,0), the alternating sum is 0, while the stated maximum is 4/5. Thus the entire Val_i argument is invalid.

### imo2026_p3 · t10_r02 · core

**2 → 2/7; incorrect.** [Submitted proof](../proofs/imo2026_p3/core_t10_r02.md) · [V2 grade](../grades/imo2026_p3/core_t10_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/234ba15833bc33143f6b158dad4290655108a1f93395e26ded271148d3de1307.json)

The claimed lower bound is false. For n=2, Liu's proposed partition is (3/5,1/5,1/5). Xiang may use only one cut, splitting 3/5 into two pieces of length 3/10. The final lengths are 3/10,3/10,1/5,1/5, so Liu receives only 1/2, not the claimed 3/5.

### imo2026_p4 · t07_r01 · core

**6 → 6/7; minor_gap.** [Submitted proof](../proofs/imo2026_p4/core_t07_r01.md) · [V2 grade](../grades/imo2026_p4/core_t07_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/6733413f745c78eee6f48d211c27cec679691f76d80bbd3962a817bbe6a0ad1a.json)

In the necessity direction, after proving that every triangle with no angle in S is losing, the submission does not explicitly show that such an initial triangle exists when 180°/θ is nonintegral. This is a minor, directly repairable witness omission rather than a Rule E central gap: the equilateral triangle works, since 60°=kθ would imply 180°/θ=3k∈Z.

### imo2026_p4 · t07_r02 · core

**6 → 5/7; substantial_gap.** [Submitted proof](../proofs/imo2026_p4/core_t07_r02.md) · [V2 grade](../grades/imo2026_p4/core_t07_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/917549bd7433dffdff94dd1968fc1367877bf6b282f46152b9759a7537d2c857.json)

In the sufficiency argument, the assertion that every open interval of length at least θ contains a multiple of θ is false. For k=3 and the equilateral triangle, the relevant interval is (60°,120°), which has length θ but contains no multiple of θ. Thus the proposed cut does not exist in that case. The triangle is already terminal, so separating this boundary case repairs the proof directly, but the submitted construction contains a false load-bearing assertion; Rule C caps the score at 5.

### imo2026_p4 · t10_r01 · core

**3 → 2/7; incorrect.** [Submitted proof](../proofs/imo2026_p4/core_t10_r01.md) · [V2 grade](../grades/imo2026_p4/core_t10_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/3c6cdc7ae843e9bab412c1788c6a1175e72170dcd8d19be8d8e4948503ebd8e4.json)

The necessity proof first fails when it claims that, outside the two proposed families, no s in S can have 180°−s also in S. For θ=36°, which belongs to neither proposed family, s=36° and 180°−s=144°=4θ are both in S. Thus the claimed classification excludes a valid value, so Rule A applies and caps the score at 2.

### imo2026_p4 · t10_r02 · core

**4 → 6/7; minor_gap.** [Submitted proof](../proofs/imo2026_p4/core_t10_r02.md) · [V2 grade](../grades/imo2026_p4/core_t10_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/b178a8e22c126c20fc8d207e8e720d61c1a55ac9338281e1107f67a0a39cfb1e.json)

In the sufficiency proof, the claim that repeated cuts near C force the minimum angle below θ does not explicitly handle Shan-Yu retaining the other child; only one child is shown to have a small angle. This is a minor, directly checkable omission rather than a Rule E central gap: choose a fixed ε<θ (or bisect the chosen vertex angle); one child has angle ε, while in the other the chosen angle decreases by ε, so after finitely many repetitions every response yields an angle below θ.

### imo2026_p5 · t07_r01 · core

**7 → 7/7; pass.** [Submitted proof](../proofs/imo2026_p5/core_t07_r01.md) · [V2 grade](../grades/imo2026_p5/core_t07_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/acdbf40a31f9f2fdfc2dcf28fc3f68a5c32bcd9b54d4f489a31bb17bb5c51375.json)

### imo2026_p5 · t07_r02 · core

**3 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p5/core_t07_r02.md) · [V2 grade](../grades/imo2026_p5/core_t07_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/5627e78d24d19dd279469e769a48335f2eca5216f48a942da37876d6c2b13417.json)

In Case 2, the assertion that the distance from x0 to the forward progression {y+n c(y): n∈N} is at most c(y) is unjustified and generally false when y>x0.

### imo2026_p5 · t10_r01 · core

**6 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p5/core_t10_r01.md) · [V2 grade](../grades/imo2026_p5/core_t10_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/98e6b7e39a4b8f6b3a3f9e8ecd25f4d1742f98ddb373b4c3801bf5623392dec4.json)

In Case 3, the claim that an arithmetic progression tending to infinity must start to the right of the finite forbidden interval is false; it may begin to the left and skip the interval. Moreover, the previously defined y_0 is naturally a zero-defect point, in which case y_n=y_0+n c_1 is not its orbit. Thus the mixed zero/positive-defect case is not validly resolved.

### imo2026_p5 · t10_r02 · core

**7 → 7/7; pass.** [Submitted proof](../proofs/imo2026_p5/core_t10_r02.md) · [V2 grade](../grades/imo2026_p5/core_t10_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/fe31771c5ba1471ab2a0a4bdd72e26c9f3c6c1f948a2f891974a3648393dcec4.json)

### imo2026_p6 · t07_r01 · core

**2 → 2/7; major_gap.** [Submitted proof](../proofs/imo2026_p6/core_t07_r01.md) · [V2 grade](../grades/imo2026_p6/core_t07_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/d62cbe8b429aa5e4d53938f395e7e97c86a75684caf8e765e96075eccd981159.json)

The first decisive defect is the claim that S, the union of all prime divisors of the terms, is finite. This is false: for a_1=2 the greedy sequence is a_n=2n, so S contains every prime. The pigeonhole argument only finds a possibly bounded prime q accompanying p and does not bound p. This false structural claim supports the entire finite-state argument, so Rule E caps the score at 3.

### imo2026_p6 · t07_r02 · core

**3 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p6/core_t07_r02.md) · [V2 grade](../grades/imo2026_p6/core_t07_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/49cde7546efb8a0acc7d875f218e21362c4561006c91b8d895368b99f1b0884d.json)

The first decisive defect is the claim that cases with a_{n+1}=m(H)>m^* can occur only finitely often because \mathcal M_n is finite. This is false: for a_1=2 the sequence is a_n=2n, and whenever n+1=p is prime, H={2,p} achieves a_{n+1}=m(H)=2p>m^*=2. Thus the asserted eventual reduction to a fixed finite family of hitting sets is unsupported, invoking Rule E.

### imo2026_p6 · t10_r01 · core

**3 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p6/core_t10_r01.md) · [V2 grade](../grades/imo2026_p6/core_t10_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/36547a3ca2c7995f34aeaca61ccfb0888d5e6685415e5ae54b0d701296c704f8.json)

The first decisive defect is the inference that, if a witness satisfies H∩P_i={p} and P_i∩P(m)≠∅, then p∈P(m). The prime in P_i∩P(m) may lie outside H; for example, P_i may contain p and q with q∈P(m) but q∉H. Thus H⊆H_N∪P(m) is unsupported, so the claimed finiteness and stabilization of the sets S_n do not follow. This is an unsupported central structural claim under Rule E.

### imo2026_p6 · t10_r02 · core

**3 → 3/7; major_gap.** [Submitted proof](../proofs/imo2026_p6/core_t10_r02.md) · [V2 grade](../grades/imo2026_p6/core_t10_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/fa9699798ad5e4df7b794ca22ec5630b69a64b58d1932b6fb1bfbe746452a99d.json)

The proof that the union P of all prime divisors of the terms is finite is false. For example, if a_1=2, then a_n=2n, so P contains every prime. In particular, infinitude of P does not imply that some new prime divisor p of a_{n+1} satisfies p>a_n+M; the subsequent claim that (a_n+M)/p<2 for large a_n merely from p>M is also false.

### imo2026_p2 · t07_r01 · tool_rewrite

**3 → 5/7; substantial_gap.** [Submitted proof](../proofs/imo2026_p2/tool_rewrite_t07_r01.md) · [V2 grade](../grades/imo2026_p2/tool_rewrite_t07_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/75bb5b00bd7b01c4de9d5ce7712ed5f45a7b1de5628e8425e140d4e980b98332.json)

The first decisive defect is the translation of ∠LBK=∠LNC. Writing D=(L-B)×(K-B), d=L×C, u=(L-B)·(K-B), and v=L·C−|C|²/2, the displayed cotangents imply du−Dv=0. The submission instead writes 2Dv−du=0, which is not equivalent. It then falsely claims that this expands to E2. This is a false load-bearing assertion, so Rule C caps the score at 5.

### imo2026_p2 · t07_r02 · tool_rewrite

**6 → 5/7; substantial_gap.** [Submitted proof](../proofs/imo2026_p2/tool_rewrite_t07_r02.md) · [V2 grade](../grades/imo2026_p2/tool_rewrite_t07_r02.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/3fef3da994eaab0fc6e77f6c3a1268d27090b01a36544439dca658fc2be8dd6c.json)

The conversion of the three unsigned angle equalities into E1, E2, E3 uses the false identity cot(angle(u,v))=(u·v)/(u×v) with a signed determinant; the correct denominator is |u×v|. The proof neither fixes an orientation nor explicitly verifies that the two determinants in each comparison have the same sign.

### imo2026_p2 · t10_r01 · tool_rewrite

**3 → 5/7; substantial_gap.** [Submitted proof](../proofs/imo2026_p2/tool_rewrite_t10_r01.md) · [V2 grade](../grades/imo2026_p2/tool_rewrite_t10_r01.json) · [V1 grade](../../../../../docs/public_release/evidence/grades/653b3305883094bd8906de8a1628171e1be40a752466f1291228354ba6360ad4.json)

The first angle-to-polynomial conversion has a sign error: det(CA,CL)=cy·lx−cx·ly, the negative of the displayed denominator. Moreover, ordinary unsigned cotangent uses the absolute determinant unless compatible orientations are proved. Thus E1 does not follow from the displayed equations as written. This is a false load-bearing assertion, so Rule C caps the score at 5.

## Execution

Published grades: 27. Unrecovered failed cases: 0. Native scorer failures recovered from existing responses: 2.

Automatic extra attempts: 3. Invalid attempts preceding a selected response: 1. Unselected later attempts: 2.

Provider-capacity failures successfully retried: 1.

Responses are selected chronologically, using the first valid isolated
response under the corrected v2 contract. The initial validator rejected
full-credit Rule C exceptions that listed cosmetic issues; these
responses are recovered without another model call. Native artifacts are
preserved, and no response is selected by its numerical score.

Problem, reference, proof, prompt and policy identities are recorded in the
published grades. Runtime logs and machine-local paths are excluded.
