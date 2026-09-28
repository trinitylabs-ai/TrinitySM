# Proof comparison

## Proof A
Established theorem: For any valid 3-coloring of the 101-stone cycle, the winding number $W = \sum_{i=1}^{101} x_i$ (where $x_i \in \{1, -1\}$ encodes the signed difference between adjacent colors modulo 3) is invariant under the allowed single-stone repaint operation. The initial state has $W_0 = -3$ and the target state has $W_f = 3$. Since $W_0 \neq W_f$, the target state is unreachable from the initial state.
Claim gap: NONE
Qualifications and supplied repairs: NONE
Decisive checks: 
- Lines 14-22 correctly analyze the local effect of repainting stone $k$. The case split on $c_{k-1} \neq c_{k+1}$ vs $c_{k-1} = c_{k+1}$ covers all valid configurations. The conclusion that the local contribution $x_{k-1}+x_k$ remains $0$ in the changeable case is verified.
- Lines 25-32 compute $W_0$. The pattern $(-1, 1)$ repeats 49 times for indices $1$ to $98$, summing to $0$. The boundary terms $x_{99}, x_{100}, x_{101}$ are correctly evaluated as $-1, -1, -1$, yielding $W_0 = -3$.
- Lines 34-41 compute $W_f$. The pattern $(1, -1)$ repeats 49 times, summing to $0$. Boundary terms $x_{99}, x_{100}, x_{101}$ are correctly evaluated as $1, 1, 1$, yielding $W_f = 3$.
- The parity/modulo observation in line 11 is correct but ancillary; it does not affect the core argument.

## Proof B
Established theorem: For any valid 3-coloring of the 101-stone cycle, the winding number invariant $W = \sum_{i=1}^{101} \text{sgn}(c(i), c(i+1))$ is preserved under all valid single-stone repaint operations. For the initial state, $W_0 = -3$; for the target state, $W_f = 3$. Since $W_0 \neq W_f$, the target state is unreachable from the initial state.
Claim gap: NONE
Qualifications and supplied repairs: NONE
Decisive checks:
- Lines 12-15 correctly establish invariance. The argument that $a \neq c$ forbids any change, and $a = c$ forces the local sum $\text{sgn}(a,b)+\text{sgn}(b,a)=0$ to remain $0$ after repainting, is mathematically sound and covers all cases.
- Lines 19-26 compute $W_0$. The grouping $\sum_{k=1}^{49} (-1+1)$ correctly accounts for indices $1$ through $98$. The remaining three terms are correctly evaluated as $-1, -1, -1$, giving $W_0 = -3$.
- Lines 28-35 compute $W_f$. The grouping $\sum_{k=1}^{49} (1-1)$ correctly accounts for indices $1$ through $98$. The remaining three terms are correctly evaluated as $1, 1, 1$, giving $W_f = 3$.
- Notation is consistent and function-based, making the cyclic indexing $c(102)=c(1)$ explicit.

## Decision
Winner: B
Reason: Both proofs are mathematically complete, correct, and rely on the identical invariant strategy with verified arithmetic. Proof B is marginally stronger in presentation: it uses cleaner function notation $c(i)$, explicitly handles the cyclic boundary condition in the definition, and groups the summation terms more compactly without sacrificing clarity. Proof A's line 11 contains a correct but unnecessary parity observation that slightly dilutes the focus. Since both successfully establish the theorem with no gaps, the preference rests on B's tighter organization and standard notation.