# Proof comparison

## Proof A
Established theorem: The procedure terminates and the cars end up sorted in increasing order of width from left to right.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Termination: The proof uses the potential function $\text{Inv}(W)$, the number of inversions in the sequence of widths. A swap occurs if $L'_i < L'_{i+1}$ and $W'_i > W'_{i+1}$. This swap changes the relative order of $W'_i$ and $W'_{i+1}$ from $W'_i > W'_{i+1}$ to $W'_{i+1} < W'_i$, which removes exactly one inversion. Since $\text{Inv}(W)$ is a non-negative integer and decreases by 1 with every swap, the process must terminate. (Verified lines 4-10).
- Final Order: The termination condition is $\forall i, \neg(L'_i < L'_{i+1} \land W'_i > W'_{i+1})$, which is equivalent to $W'_i > W'_{i+1} \implies L'_i > L'_{i+1}$. If the final state is not sorted by width, there exists $i$ such that $W'_i > W'_{i+1}$, which implies $L'_i > L'_{i+1}$. Let $C'_i = C_a$ and $C'_{i+1} = C_b$. Then $L_a > L_b$ (implying $a > b$ since cars were initially sorted by length) and $W_a > W_b$. The proof checks if $C_a$ and $C_b$ can ever be swapped: if in order $(C_b, C_a)$, the swap condition $L_b < L_a$ and $W_b > W_a$ fails because $W_a > W_b$; if in order $(C_a, C_b)$, the condition $L_a < L_b$ and $W_a > W_b$ fails because $L_a > L_b$. Thus, $C_a$ and $C_b$ can never be swapped. Since they were initially in the order $(C_b, C_a)$ (because $b < a$), they must remain in that order. This contradicts the final state where $C_a$ is to the left of $C_b$. (Verified lines 13-29).

## Proof B
Established theorem: The procedure terminates and the cars end up sorted in increasing order of width from left to right.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Termination: The proof uses the potential function consisting of the number of pairs $(S_i, S_j)$ with $i < j$ such that $l_{S_i} < l_{S_j}$. A swap occurs if $l_{S_k} < l_{S_{k+1}}$ and $w_{S_k} > w_{S_{k+1}}$. After the swap, the pair $(S_k, S_{k+1})$ becomes $(S_{k+1}, S_k)$, and since $l_{S_k} < l_{S_{k+1}}$, the new order $l_{S_{k+1}} > l_{S_k}$ no longer satisfies the condition. All other pairs are unchanged. The count decreases by 1 each time, ensuring termination. (Verified lines 6-8).
- Final Order: Induction on $n$. For $n$ cars, let $C_{p_1}$ be the car with minimum width. $C_{p_1}$ cannot move right because $w_{S_k} > w_{S_{k+1}}$ is impossible if $S_k = C_{p_1}$. $C_{p_1}$ can only move left. Any car $C_x$ with $x > p_1$ (so $l_x > l_{p_1}$) cannot be swapped with $C_{p_1}$ because the swap condition $l_{\text{left}} < l_{\text{right}}$ would be violated if $C_x$ is on the left, and $w_{\text{left}} > w_{\text{right}}$ would be violated if $C_{p_1}$ is on the left. Thus, $C_{p_1}$ remains to the left of all $C_x$ for $x > p_1$. Any car $C_y$ with $y < p_1$ can be swapped with $C_{p_1}$ (since $l_y < l_{p_1}$ and $w_y > w_{p_1}$), moving $C_{p_1}$ further left. In the final state, if $S_j = C_{p_1}$ for $j > 1$, stability requires $l_{S_{j-1}} > l_{S_j} = l_{p_1}$, but $S_{j-1}$ must be from $\{C_1, \dots, C_{p_1-1}\}$, all of which have $l < l_{p_1}$. Thus $S_1 = C_{p_1}$. The remaining $n-1$ cars are then sorted by the inductive hypothesis. (Verified lines 11-28).

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct. Proof A is preferred for its more elegant and direct argument for the final order, utilizing the invariant relative order of non-swappable pairs to reach a contradiction, whereas Proof B relies on a slightly more cumbersome inductive argument.