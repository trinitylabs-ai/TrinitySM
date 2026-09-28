# Proof comparison

## Proof A
Established theorem: The proof correctly establishes that $P$ is surjective, $P(0)=0$, $P$ is a bijection, and $P(-P(a)) = -a$ for all $a \in \mathbb{Q}$. It correctly derives that $P(x) = x$ and $P(x) = -x$ satisfy the equation and yield the set $\{0\}$.
Claim gap: The proof contains a gap in Case 2 (Lines 28–30). It asserts that the condition $P(b+y) - P(y) \in \{C_1, C_2\}$ for a bijection $P$ on $\mathbb{Q}$ "forces $P$ to be linear" without providing a rigorous derivation. While this assertion is mathematically true (a bijection on $\mathbb{Q}$ with a finite difference set must be linear), the step relies on an unproven lemma.
Qualifications and supplied repairs: The audit verified the derivations of surjectivity, $P(0)=0$, bijectivity, and $P(-P(a)) = -a$ independently. No repairs were supplied for the Case 2 gap; it is noted as a missing justification for a plausible claim rather than a logical error.
Decisive checks:
- **Verified:** Lines 5–12 correctly prove $P(0)=0$ by contradiction. The substitution $w = z + P(b)$ correctly covers $\mathbb{Q}$ due to surjectivity, and the deduction $P(z+b)=P(b) \implies z=0$ holds.
- **Verified:** Lines 15–19 correctly derive $P(-P(a)) = -a$ and bijectivity using the kernel property $P(w)=0 \iff w=0$.
- **Unresolved:** Line 30 asserts linearity from the difference condition $P(b+y) - P(y) \in \{C_1, C_2\}$ without proof. This is a gap in rigor, not a demonstrated defect.

## Proof B
Established theorem: The proof fails to establish any substantive properties of $P$ due to fatal logical errors in the foundational steps.
Claim gap: The proof contains two critical defects. First, Line 5 claims $P(x) = P(y) \implies P(x-P(a)) = P(y-P(a))$, which is false for general functions. Second, Lines 38–39 contain a logical non-sequitur: it argues that because $Y(a, b_0) \neq 0$ when $X(a, b_0) = 0$, then $X(a, b_0)$ must be 0 for all $a$. This misinterprets the condition $XY=0$, which allows $X=0$ (with $Y \neq 0$) or $Y=0$ (with $X \neq 0$), and incorrectly forces $X$ to vanish globally.
Qualifications and supplied repairs: No repairs were supplied. The errors are foundational and invalidate the injectivity proof and the subsequent derivation of $P(P(b))=b$.
Decisive checks:
- **Demonstrated Defect:** Line 5 is false. Counterexample: $P(t)=t^2$, $x=1, y=-1, a=2$. $P(1)=P(-1)=1$, but $P(1-2)=1 \neq 9=P(-1-2)$. The equality $P(x-P(a)) = P(y-P(a))$ does not follow from $P(x)=P(y)$.
- **Demonstrated Defect:** Lines 38–39. The premise $X(a, b_0)Y(a, b_0)=0$ combined with $X=0 \implies Y \neq 0$ is consistent with $X=0$ for some $a$ and $X \neq 0$ for others (provided $Y=0$ there). The conclusion that $X(a, b_0)=0$ for all $a$ does not follow.

## Decision
Winner: A
Reason: Proof A provides a mathematically sound derivation of the core properties of $P$ (surjectivity, $P(0)=0$, bijectivity, and $P(-P(a))=-a$). Its only deficiency is a heuristic assertion in the final classification step (Case 2), which is a gap in rigor but not a logical error. Proof B, conversely, contains fatal logical errors: it assumes $P(x)=P(y) \implies P(x-k)=P(y-k)$ (Line 5) and uses invalid implication logic to force $X(a,b)=0$ (Lines 38–39). Proof A is the only submission that establishes the necessary conditions for the solution correctly.