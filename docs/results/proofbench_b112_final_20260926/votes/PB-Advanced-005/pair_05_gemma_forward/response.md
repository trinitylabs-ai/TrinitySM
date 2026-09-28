# Proof comparison

## Proof A
Established theorem: For $\theta = \alpha$ (where $\alpha = \angle XYZ$), the only points $D$ such that $\angle BDC = \theta$ whenever $\angle BAC = \alpha$ are $D=A$ and $D=Y$.
Claim gap: The proof fails to identify a point $D \neq A$ inside the angle $\angle XYZ$ and a corresponding $\theta \in (0, 2\pi)$. The final claim that the reflection of $A$ across the angle bisector satisfies the condition is not supported by the preceding derivation and is mathematically incorrect.
Qualifications and supplied repairs: None.
Decisive checks: The derivation of the concyclic condition $c = mb + n$ (line 4) is verified. The expressions for the numerator $N$ and denominator $D_{en}$ of $\tan \angle BDC$ (lines 8-9) are verified. The proportionality conditions $N = \tan \alpha D_{en}$ (lines 14-17) are verified to lead to the constraints $\frac{x}{y} = \frac{x_A}{y_A}$ and $x^2 + y^2 = \frac{ny}{\sin \alpha}$, which correctly imply $D=A$ or $D=Y$ (line 18).

## Proof B
Established theorem: None.
Claim gap: The proof fails to provide any mathematical derivation. The proposed construction $D=2A$ and the claim that $\angle BDC = \pi - \alpha$ are unsupported and mathematically false.
Qualifications and supplied repairs: None.
Decisive checks: The central claim in line 21 is falsified by a counterexample: for $\alpha = 90^\circ$, $A=(1,1)$, $B=(b,0)$, and $C=(2-b,0)$, the dot product $\vec{DB} \cdot \vec{DC}$ for $D=2A=(2,2)$ is $4$, while $|\vec{DB}||\vec{DC}| = \sqrt{b^2-4b+8}\sqrt{b^2+4}$, meaning $\cos \angle BDC$ is not constant.

## Decision
Winner: A
Reason: Proof A provides a detailed and mathematically sound derivation of the conditions required for $\angle BDC$ to be constant, correctly identifying that for $\theta = \alpha$, only $D=A$ and $D=Y$ are solutions. Although it fails to find the correct $D$ and ends with an incorrect guess, its work is substantive and verified. Proof B provides no derivation and relies on a false "known property" to make a claim that is easily falsified.