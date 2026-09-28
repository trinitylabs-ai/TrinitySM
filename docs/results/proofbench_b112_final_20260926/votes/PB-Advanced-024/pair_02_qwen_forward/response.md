# Proof comparison

## Proof A
Established theorem: None. The proof fails to establish injectivity, which is the foundational step for all subsequent claims.
Claim gap: Lines 5–17 rely on a false implication, invalidating the proof of injectivity. All later steps (surjectivity, $P(0)=0$, involution, linearity) depend on this unestablished property.
Qualifications and supplied repairs: NONE. The logical error in Line 5 is fundamental and cannot be repaired without discarding the argument.
Decisive checks: 
- **Demonstrated Defect (Line 5):** The proof claims "Since $P(x) = P(y)$, we have $P(x-P(a)) = P(y-P(a))$." This is false; $P(u) = P(v)$ does not imply $P(u-k) = P(v-k)$. A simple counterexample on $\mathbb{Q}$: let $P(t) = t^2$ for $t \in \{0,1\}$ and $P(t)=0$ otherwise. $P(1)=P(0)=0$ is false, but consider $P(t) = 1$ if $t \in \{1,2\}$, $0$ otherwise. $P(1)=P(2)=1$, but $P(1-1)=P(0)=0 \neq P(2-1)=P(1)=1$. 
- **Consequence:** The deduction $X(a, x) = X(a, y)$ (Line 7) is unjustified, collapsing the injectivity proof. Subsequent use of $P^{-1}$ and bijectivity (Lines 39, 47) is unsupported.

## Proof B
Established theorem: $P$ is surjective; $P(0)=0$; $P(x)=0 \iff x=0$; $P(-P(a)) = -a$ for all $a \in \mathbb{Q}$; $P$ is a bijection.
Claim gap: Line 11 contains a substitution error in deriving $P(0)=0$, and Line 30 relies on a heuristic argument to rule out non-linear solutions.
Qualifications and supplied repairs: 
- **Repair for Line 11:** The proof claims $P(z+b) = P(b)$, but substituting $b \mapsto z+P(b)$ into $P(z+P(b))=b$ correctly yields $P(z+b) = z+P(b)$. However, $P(0)=0$ is provable from established premises: setting $b=z$ in $P(z+P(b))=b$ gives $P(z+P(z))=z \implies P(z)=z$. Since $P(z)=0$, we get $z=0$.
- **Gap in Line 30:** The assertion that $P(b+y)-P(y) \in \{C_1, C_2\}$ "forces $P$ to be linear" is heuristic. While standard for $\mathbb{Q}$-bijections, it lacks a rigorous algebraic derivation in the text.
Decisive checks: 
- **Verified Fact (Line 5):** Surjectivity proof is correct. If $b$ is not in the range, $Y(a,b) \neq 0$, forcing $X(a,b)=0 \implies P(b-P(a)) = P(b)-a$. As $a$ varies, the RHS covers $\mathbb{Q}$, proving surjectivity.
- **Verified Fact (Line 18):** Derivation of $P(-P(a))=-a$ follows correctly from $P(0)=0$ and the kernel property $P(w)=0 \iff w=0$.
- **Demonstrated Defect (Line 11):** The substitution yields $P(z+b)=z+P(b)$, not $P(b)$. The conclusion $z=0$ remains true but the written derivation is flawed.

## Decision
Winner: B
Reason: Proof A contains a fatal logical error in Line 5 ($P(x)=P(y) \not\implies P(x-P(a))=P(y-P(a))$), which invalidates the entire argument for injectivity and all dependent steps. Proof B correctly establishes the core structural properties of $P$ (surjectivity, $P(0)=0$, and the involution $P(-P(a))=-a$). While B has a substitution slip in Line 11 and a heuristic gap in Line 30, these do not undermine the validity of the established lemmas, and the conclusion $P(0)=0$ is independently provable from B's premises. B's derivation is substantially sounder and mathematically justified compared to A's foundational collapse.