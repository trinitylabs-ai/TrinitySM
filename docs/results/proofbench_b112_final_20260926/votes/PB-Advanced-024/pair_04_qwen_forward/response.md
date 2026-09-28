# Proof comparison

## Proof A
Established theorem: For any $P:\mathbb{Q}\to\mathbb{Q}$ satisfying the given equation, $P(x)=x$ or $P(x)=-x$ for all $x\in\mathbb{Q}$. Consequently, $\{P(a)+P(-a):a\in\mathbb{Q}\}=\{0\}$, which is finite with exactly 1 element.
Claim gap: NONE supported by checks. The argument is complete and logically sound.
Qualifications and supplied repairs: NONE. Line 16 contains a minor attribution imprecision: it states the argument $a+P(b-P(a))$ must lie in $S$ because $P(b)\in S$, whereas the contradiction actually arises from $b\in S$. This does not affect the validity of the conclusion that the argument lies in $S$, as verified by direct substitution.
Decisive checks: 
- Line 9: Verified. Fixing $b$, if $P(P(b))\neq b$, then $X(a,b)=0 \implies Y(a,b)=P(P(b))-b\neq 0$. Since $XY=0$ for all $a$, $X(a,b)$ cannot vanish, forcing $Y(a,b)=0$ for all $a$. Quantifier order and domain ($\forall a,b\in\mathbb{Q}$) are correctly handled.
- Line 13: Verified. $a=0$ in $Y(a,b)=0$ gives $P(P(b-\delta))=b$. If $b-\delta\notin S$, then $P(P(b-\delta))=b-\delta \implies \delta=0$, contradicting $b\in S$. Thus $b-\delta\in S$ and $P(P(x))=x+\delta$ on $S$. Induction on $n\in\mathbb{Z}$ correctly extends this.
- Line 19: Verified. $P(P(x))=x$ globally implies $X(a,b)=0 \iff Y(a,b)=0$. Since $XY=0$, the equivalence forces $X(a,b)=0$ (and $Y(a,b)=0$) for all $a,b$. No hidden assumptions.
- Line 22-23: Verified. $P(b-P(a))=P(b)-a$ with $P(0)=0$ and bijectivity yields $P(b-z)=P(b)-P(z)$ for all $b,z\in\mathbb{Q}$. This is Cauchy's equation on $\mathbb{Q}$, yielding $P(x)=kx$. $P(P(x))=x \implies k^2=1 \implies k=\pm 1$. All steps are routine and correctly justified.

## Proof B
Established theorem: $P$ is a bijection, $P(0)=0$, $P(x)=0 \iff x=0$, and $P(-P(a))=-a$ for all $a$. The proof correctly reduces the condition to $P(b-x)+P^{-1}(x) \in \{P(b), P^{-1}(b)\}$ for all $b,x\in\mathbb{Q}$.
Claim gap: Line 30 contains a load-bearing gap. The assertion that $P(b+y)-P(y) \in \{C_1, C_2\}$ for all $y\in\mathbb{Q}$ forces $P$ to be linear is stated without proof. While plausible, this requires a non-trivial structural lemma (e.g., analyzing the partition of $\mathbb{Q}$ induced by the difference set or using the original equation recursively) that is not supplied. Without it, the case $P(b) \neq P^{-1}(b)$ is not resolved, leaving the classification incomplete.
Qualifications and supplied repairs: To close the gap, one would need to independently prove that a bijection on $\mathbb{Q}$ with a two-valued difference function must be additive, or derive a contradiction by substituting the difference condition back into the original functional equation. This substantive work is absent from the submission.
Decisive checks:
- Lines 5-12: Verified. Surjectivity, existence of $z$ with $P(z)=0$, and deduction $z=0$ are correct. Quantifiers are properly managed.
- Lines 14-19: Verified. $P(x)=0 \iff x=0$, bijection, and $P(-P(a))=-a$ are correctly derived using the $XY=0$ condition and injectivity.
- Lines 24-25: Verified. Correctly translates $XY=0$ into $P(b-x)+P^{-1}(x) \in \{P(b), P^{-1}(b)\}$ via substitution $P(a)=x$.
- Line 30: Demonstrated defect. The claim that the two-value difference condition forces linearity is unsupported. No algebraic derivation, group-theoretic argument, or reference to the original equation is provided. This step is essential to rule out non-linear solutions and constitutes a load-bearing gap.

## Decision
Winner: A
Reason: Proof A provides a complete, rigorous derivation. It correctly handles the $X=0 \lor Y=0$ dichotomy by analyzing the set $S=\{b:P(P(b))\neq b\}$, deriving a contradiction via the shift parameter $\delta$, and thereby forcing $P(P(x))=x$ globally. This cleanly reduces the problem to Cauchy's equation on $\mathbb{Q}$. Proof B makes strong initial progress but fails at line 30, where it asserts without proof that a bounded difference condition on $\mathbb{Q}$ forces linearity. This is a load-bearing gap that leaves the classification of solutions incomplete. Proof A's central chain of implications is fully verified and requires no external lemmas.