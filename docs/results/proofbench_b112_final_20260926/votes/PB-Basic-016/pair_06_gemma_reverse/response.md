# Proof comparison

## Proof A
Established theorem: It is impossible to reach the target state $S_f$ from the initial state $S_0$ because the winding number $W = \sum_{i=1}^{101} \text{sgn}(c(i), c(i+1))$ is an invariant under the allowed modifications, and $W(S_0) = -3$ while $W(S_f) = 3$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The invariant $W$ is correctly defined using signed differences in $\mathbb{Z}_3$. The invariance is justified: if $c(j-1) \neq c(j+1)$, the color of stone $j$ is uniquely determined and cannot change; if $c(j-1) = c(j+1)$, the contribution to the sum $\text{sgn}(a, b) + \text{sgn}(b, a)$ is always 0 for any $b \neq a$ (lines 12-16).
- Initial state $S_0$ calculation: $c(101)=2$, $c(2k)=0$, $c(2k-1)=1$. Transitions are $\text{sgn}(1,0)=-1$ for $i \in \{1, 3, \dots, 99\}$ (50 terms), $\text{sgn}(0,1)=1$ for $i \in \{2, 4, \dots, 98\}$ (49 terms), $\text{sgn}(0,2)=-1$ for $i=100$, and $\text{sgn}(2,1)=-1$ for $i=101$. The sum $W_0 = 50(-1) + 49(1) - 1 - 1 = -3$ is correctly computed (lines 19-26).
- Target state $S_f$ calculation: $c(101)=2$, $c(2k)=1$, $c(2k-1)=0$. Transitions are $\text{sgn}(0,1)=1$ for $i \in \{1, 3, \dots, 99\}$ (50 terms), $\text{sgn}(1,0)=-1$ for $i \in \{2, 4, \dots, 98\}$ (49 terms), $\text{sgn}(1,2)=1$ for $i=100$, and $\text{sgn}(2,0)=1$ for $i=101$. The sum $W_f = 50(1) + 49(-1) + 1 + 1 = 3$ is correctly computed (lines 28-35).
- The conclusion $W_0 \neq W_f$ correctly proves the target state is unreachable.

## Proof B
Established theorem: It is impossible to reach the target state $S_f$ from the initial state $S_0$ because the winding number $w = S/3$ is an invariant under the allowed modifications, and $w(S_0) = -1$ while $w(S_f) = 1$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The invariant $S = \sum_{i=1}^{101} \text{step}(C(i), C(i+1))$ is correctly defined. The invariance is justified: if $C(i-1) \neq C(i+1)$, no change is possible; if $C(i-1) = C(i+1)$, the sum of steps is always 0 (lines 11-14).
- Initial state $S_0$ calculation: $C(101)=2$, $C(2k)=0$, $C(2k-1)=1$. Transitions are $\text{step}(1,0)=-1$ (50 terms), $\text{step}(0,1)=1$ (49 terms), $\text{step}(0,2)=-1$, and $\text{step}(2,1)=-1$. The sum $S_0 = -50 + 49 - 2 = -3$, so $w_0 = -1$ (lines 18-27).
- Target state $S_f$ calculation: $C(101)=2$, $C(2k)=1$, $C(2k-1)=0$. Transitions are $\text{step}(0,1)=1$ (50 terms), $\text{step}(1,0)=-1$ (49 terms), $\text{step}(1,2)=1$, and $\text{step}(2,0)=1$. The sum $S_f = 50 - 49 + 2 = 3$, so $w_f = 1$ (lines 29-38).
- The conclusion $w_0 \neq w_f$ correctly proves the target state is unreachable.

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct, utilizing the same invariant and identical calculations. Proof A is slightly preferred for its more concise and structured summation notation in the final calculations.