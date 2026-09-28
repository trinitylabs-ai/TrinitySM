# Proof comparison

## Proof A
Established theorem: For $n \geq 2$ cars initially sorted by length, the procedure of swapping adjacent cars $C_i, C_{i+1}$ if $L_i < L_{i+1}$ and $W_i > W_{i+1}$ eventually terminates, and the final state is sorted in increasing order of width.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: In line 6, the proof refers to the pair $(\sigma(i), \sigma(i+1))$ as an inversion; based on the definition in line 4, it is the pair of positions $(i, i+1)$ that constitutes the inversion, while $\sigma(i)$ and $\sigma(i+1)$ are the cars at those positions. This is a minor notation inconsistency that does not affect the mathematical validity.
Decisive checks:
- Termination: The proof uses the number of width inversions $I_W$ as a monovariable. A swap occurs if $L_i < L_{i+1}$ and $W_i > W_{i+1}$. This swap removes the width inversion $(W_i, W_{i+1})$ and does not create any others. Since $I_W$ is a non-negative integer that decreases by 1 each step, the process must terminate. (Verified)
- Final State: The proof uses induction on $n$. For the inductive step, it identifies $C_{minW}$ and proves it must end up at position 1. It correctly argues that $C_{minW}$ can never be the left car in a swap, so it only moves left. It then shows that any car to its left in the final state must have been to its left initially, meaning its length $L < L_{minW}$. This contradicts the stability condition $L_{\sigma(k-1)} > L_{minW}$ for $k > 1$. (Verified)
- Induction: The proof concludes that the remaining $n-1$ cars are sorted by width by the inductive hypothesis. (Verified)

## Proof B
Established theorem: For $n \geq 2$ cars initially sorted by length, the procedure of swapping adjacent cars $S_k, S_{k+1}$ if $l_{S_k} < l_{S_{k+1}}$ and $w_{S_k} > w_{S_{k+1}}$ eventually terminates, and the final state is sorted in increasing order of width.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Termination: The proof uses the number of pairs $(S_i, S_j)$ with $i < j$ and $l_{S_i} < l_{S_j}$ as a monovariable. A swap occurs if $l_{S_k} < l_{S_{k+1}}$ and $w_{S_k} > w_{S_{k+1}}$. After the swap, the pair $(S_{k+1}, S_k)$ no longer satisfies the condition $i < j$ and $l_{S_i} < l_{S_j}$. Since this count is a non-negative integer that decreases by 1 each step, the process must terminate. (Verified)
- Final State: The proof uses induction on $n$. For the inductive step, it identifies $C_{p_1}$ (minimum width) and proves it must end up at position 1. It correctly argues that $C_{p_1}$ can only move left and that any car to its left in the final state must have been to its left initially, implying $l_{S_{j-1}} < l_{p_1}$. This contradicts the stability condition $l_{S_{j-1}} > l_{p_1}$ for $j > 1$. (Verified)
- Induction: The proof explicitly justifies that the presence of $C_{p_1}$ at the first position does not block swaps among the remaining $n-1$ cars, making the process on them equivalent to the original problem. (Verified)

## Decision
Winner: B
Reason: Both proofs are mathematically complete and correct. Proof B is slightly superior due to its more precise notation and its more detailed justification of the inductive step, specifically in line 26, where it explains why the car with minimum width does not interfere with the sorting of the remaining $n-1$ cars.