# Proof comparison

## Proof A
Established theorem: The set $\{P(a)+P(-a):a\in\mathbb{Q}\}$ is exactly $\{0\}$, containing 1 element. The proof rigorously establishes that $P$ is a bijection, $P(0)=0$, $P(P(x))=x$ for all $x$, and $P$ satisfies Cauchy's additive equation, yielding $P(x)=\pm x$.
Claim gap: NONE. The argument is complete and logically sound.
Qualifications and supplied repairs: NONE. Lines 19-20 contain superfluous hand-waving about linearity, but the core derivation in lines 15-18 independently and rigorously establishes $P(P(x))=x$ without needing those lines. No repair was necessary.
Decisive checks: 
- Surjectivity (lines 5-6) and injectivity (lines 7-8) are correctly derived. The periodicity contradiction in line 8 correctly uses rational commensurability ($nh=mT$) to force $na=0$, contradicting arbitrary $a \neq 0$.
- The derivation of $P(P(x))=x$ (lines 14-18) is verified: assuming $P(P(b_0)) \neq b_0$ forces $Y(a,b_0)=0$ for all $a$, which after substituting $z=P(a)$ and applying $P^{-1}$ yields $P^{-1}(z) + P(b_0-z) = P^{-1}(b_0)$. Setting $z=0$ gives $P(b_0) = P^{-1}(b_0)$, directly contradicting the assumption. This step is airtight.
- Cauchy's equation derivation (lines 48-50) correctly uses $P(P(x))=x$ to substitute $b = P(z)+P(a)$, yielding additivity. Over $\mathbb{Q}$, this implies $P(x)=mx$, and $m^2=1$ gives the final solutions.

## Proof B
Established theorem: Claims the same result as A, but the proof contains a fatal logical error that invalidates the injectivity claim and all subsequent steps that depend on it.
Claim gap: FATAL FLAW at line 5. The proof incorrectly asserts that $P(x)=P(y)$ implies $P(x-P(a)) = P(y-P(a))$. This is false for general functions; equality of outputs at two points does not imply equality of outputs at shifted points. This breaks the injectivity proof entirely.
Qualifications and supplied repairs: NONE supplied. The defect is foundational and cannot be repaired without rewriting the injectivity argument (e.g., adopting Proof A's correct approach).
Decisive checks:
- Line 5 is a demonstrated defect. Counterexample: Let $P(1)=P(2)=0$ but $P(0)=1, P(-1)=2$. Take $x=1, y=2$. Then $P(x)=P(y)=0$. Let $a$ be such that $P(a)=1$. Then $x-P(a)=0$ and $y-P(a)=1$. We have $P(x-P(a))=P(0)=1 \neq P(1)=0=P(y-P(a))$. The claimed implication fails.
- Because injectivity is not established, the subsequent derivations of $P(0)=0$, $P(-P(a))=-a$, and $P(P(b))=b$ lack their required premises. The rest of the proof, while structurally similar to A, rests on an unproven foundation.

## Decision
Winner: A
Reason: Proof A provides a complete, rigorous derivation with no logical gaps. Its injectivity proof correctly handles the periodicity case, and its derivation of $P(P(x))=x$ via contradiction is mathematically sound. Proof B contains a fatal logical error at line 5, falsely assuming that $P(x)=P(y)$ implies translation invariance of the function's values ($P(x-P(a))=P(y-P(a))$). This defect invalidates the injectivity claim and collapses the entire argument. Proof A is strictly superior due to its verified correctness and rigorous handling of all functional equation constraints.