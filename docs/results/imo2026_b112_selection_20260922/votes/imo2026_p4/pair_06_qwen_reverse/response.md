# Proof comparison

## Proof A
Established theorem: The proof successfully establishes the necessity condition: if $\theta \neq 180^\circ/n$ for any integer $n \ge 2$, Mulan cannot guarantee victory. The argument that Shan-Yu can perpetually avoid the set $W = \{k\theta\}$ is mathematically sound.
Claim gap: The sufficiency condition ($\theta = 180^\circ/n \implies$ Mulan wins) is not established. The proposed strategy relies on a geometrically incorrect calculation of the available range for the cut angle, which breaks the existence argument for a winning move.
Qualifications and supplied repairs: NONE. The geometric error in the interval length is load-bearing and cannot be repaired without changing the stated strategy.
Decisive checks: 
- **Verified Fact (Lines 20-29):** The necessity analysis correctly enumerates the four combinations of angles in the split triangles. It rigorously shows that if $\theta \neq 180^\circ/n$, forcing both children to contain an angle in $W$ implies an original angle was already in $W$, contradicting the hypothesis.
- **Demonstrated Defect (Lines 3-6, 15):** The proof claims that cutting from the vertex with the smallest angle $\alpha$ yields an interval for $\psi = \angle BPA$ of $(\beta, 180^\circ-\alpha)$, which has length $\gamma$. Geometrically, a cut from vertex $\alpha$ to the opposite side produces $\psi \in (\gamma, 180^\circ-\beta)$, which has length $\alpha$. Since $\alpha$ is the smallest angle, $\alpha$ can be strictly less than $\theta$ (e.g., $\theta=60^\circ$, triangle $10^\circ, 100^\circ, 70^\circ$). In such cases, the actual interval $(70^\circ, 80^\circ)$ contains no multiple of $\theta$, so the proposed move fails. The proof incorrectly attributes the interval properties of a cut from the largest angle to a cut from the smallest angle.

## Proof B
Established theorem: The proof correctly establishes the complete characterization: Mulan can guarantee victory if and only if $\theta = 180^\circ/n$ for some integer $n \ge 2$.
Claim gap: NONE. The argument covers all cases, including boundary conditions, with correct geometric and algebraic justification.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Verified Fact (Lines 5-13):** The sufficiency strategy correctly models splitting vertex angle $a$ into $\alpha_1, \alpha_2$ and targets the angles at the cut point $P$ to be $k_1\theta, k_2\theta$. The derivation $\alpha_1 = 180^\circ - b - k_1\theta$ and $\alpha_2 = 180^\circ - c - k_2\theta$ is algebraically sound. The condition $\alpha_1 + \alpha_2 = a$ correctly reduces to $k_1 + k_2 = n$.
- **Verified Fact (Lines 10-14):** The interval for $k_1$ is correctly derived as $(c/\theta, n - b/\theta)$ with length $a/\theta$. The proof correctly notes that if $a > \theta$, the open interval length exceeds 1, guaranteeing an integer. The edge case $n=2$ ($\theta=90^\circ$) is explicitly handled: when $a,b,c < 90^\circ$, the interval $(c/90, 2-b/90)$ strictly contains $k_1=1$, and the constraints $\alpha_1, \alpha_2 \in (0,a)$ are satisfied by the interval bounds ($k_1 > c/\theta \iff \alpha_1 < a$, etc.).
- **Verified Fact (Lines 16-24):** The necessity argument mirrors the correct logic of Proof A, properly concluding that Shan-Yu can avoid $S$ indefinitely if $\theta \neq 180^\circ/n$. The choice of an equilateral starting triangle is valid since $60^\circ \in S \iff \theta = 180^\circ/(3k)$.

## Decision
Winner: B
Reason: Proof B provides a complete and rigorous proof, while Proof A contains a fatal geometric error in its sufficiency argument. Proof A incorrectly claims that cutting from the vertex with the smallest angle $\alpha$ yields a cut-angle interval of length $\gamma$ (the largest angle); the actual length is $\alpha$, which can be smaller than $\theta$, invalidating the existence claim for a winning move. Proof B correctly models the cut geometry, derives the precise interval length $a/\theta$, verifies all boundary constraints ($\alpha_1, \alpha_2 \in (0,a)$), and properly handles the $n=2$ edge case. Both proofs correctly establish necessity, but only Proof B successfully justifies sufficiency.