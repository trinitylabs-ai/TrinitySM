# Problem

Adrian is lining up $n \geq 2$ toy cars in a row. Each car has a width and length, and no two cars have the same width or length. Initially, the cars are arranged in increasing order of length from left to right. Adrian repeatedly does the following: he chooses some two adjacent cars where the left car is shorter in length and greater in width than the right car, and he swaps them. He keeps doing this until no further moves are possible. Prove that no matter how Adrian chooses his swaps, the procedure will eventually terminate, and in the end, the cars will be sorted in increasing order of width from left to right.

# Proof A

1: To prove that the procedure terminates and that the cars end up sorted by width, we proceed by proving termination, analyzing the final position of the widest car, and using induction on the number of cars $n$.
2: 
3: ### 1. Termination of the Procedure
4: Let the cars be represented by pairs $(l_i, w_i)$ for $i=1, \dots, n$, where $l_i$ is the length and $w_i$ is the width. Initially, the cars are arranged such that $l_1 < l_2 < \dots < l_n$.
5: A swap occurs between adjacent cars $C_{left}$ and $C_{right}$ if and only if $l_{left} < l_{right}$ and $w_{left} > w_{right}$. 
6: Each such swap changes the sequence of lengths from $(\dots, l_{left}, l_{right}, \dots)$ to $(\dots, l_{right}, l_{left}, \dots)$. Because $l_{left} < l_{right}$, this operation strictly increases the number of inversions in the sequence of lengths. 
7: The total number of inversions in a sequence of $n$ elements is at most $\frac{n(n-1)}{2}$. Since each swap increases this finite integer value, the procedure must eventually terminate.
8: 
9: ### 2. Position of the Widest Car
10: Let $C_W$ be the car with the maximum width $w_{\max}$. We claim that in any terminal state, $C_W$ must be at the last position (position $n$).
11: First, $C_W$ can never move to the left. A swap between adjacent cars $(C_{left}, C_{right})$ requires $w_{left} > w_{right}$. If $C_W$ were the right car ($C_{right}$), the swap would require $w_{left} > w_{\max}$, which is impossible as $w_{\max}$ is the unique maximum.
12: 
13: Second, we establish an invariant: at any point in the process, any car to the right of $C_W$ must have a length greater than $l_W$.
14: - **Initial State:** Initially, $C_W$ is at some position $p$. All cars $C_j$ with $j > p$ were placed there because their lengths are greater than $l_p = l_W$ (since the cars are initially sorted by length).
15: - **Swaps:** 
16:     - If two cars other than $C_W$ swap, the set of cars to the right of $C_W$ remains the same, preserving the invariant.
17:     - If $C_W$ swaps with its right neighbor $C_r$, the swap is only possible if $l_W < l_r$ and $w_W > w_r$. After the swap, $C_W$ moves to the right, and the new set of cars to its right is the previous set minus $\{C_r\}$. Since all cars in the previous set had lengths $> l_W$, the invariant is preserved.
18: 
19: In a terminal state, no adjacent cars $(C_k, C_{k+1})$ can satisfy $l_k < l_{k+1}$ and $w_k > w_{k+1}$. If $C_W$ were at position $k < n$, then for the pair $(C_W, C_{k+1})$, the swap condition must be false. This implies $l_W \geq l_{k+1}$ or $w_W \leq w_{k+1}$.
20: However, $w_W$ is the unique maximum width, so $w_W \leq w_{k+1}$ is impossible. Furthermore, our invariant ensures that any car to the right of $C_W$ must have $l > l_W$, so $l_W \geq l_{k+1}$ is also impossible. Therefore, $C_W$ cannot be at any position $k < n$ in a terminal state; it must be at position $n$.
21: 
22: ### 3. Induction on $n$
23: We prove that the final state is sorted by width by induction on $n$.
24: - **Base Case ($n=2$):** Initially $l_1 < l_2$. If $w_1 < w_2$, no swap occurs and the cars remain in the order $(C_1, C_2)$, which is sorted by width. If $w_1 > w_2$, the cars swap, resulting in the order $(C_2, C_1)$, which is sorted by width since $w_2 < w_1$.
25: - **Inductive Step:** Assume the statement holds for $n-1$ cars. For $n$ cars, we have shown the process terminates and $C_W$ ends at position $n$. Let the final sequence be $S_n = (C'_{1}, C'_{2}, \dots, C'_{n-1}, C_W)$. 
26: Consider the subsequence $S_{n-1} = (C'_{1}, \dots, C'_{n-1})$. This subsequence must be a terminal state for the process involving only these $n-1$ cars. Indeed, if $S_{n-1}$ were not terminal, there would exist some $i < n-1$ such that $l'_i < l'_{i+1}$ and $w'_i > w'_{i+1}$. Since $C'_i$ and $C'_{i+1}$ are adjacent in $S_n$, this would imply that $S_n$ is not a terminal state, a contradiction.
27: The relative initial order of these $n-1$ cars was sorted by length. By the inductive hypothesis, any terminal state reached from a length-sorted state for $n-1$ cars is sorted by width. Thus, $S_{n-1}$ is sorted by width: $w'_1 < w'_2 < \dots < w'_{n-1}$.
28: Because $C_W$ is the widest car and is at the last position, the entire sequence $S_n$ is sorted in increasing order of width from left to right: $w'_1 < w'_2 < \dots < w'_{n-1} < w_W$.
29: 
30: We have proven that the procedure terminates and that the final arrangement of cars is sorted by width. $\square$

# Proof B

1: To prove that the procedure eventually terminates and that the cars will be sorted in increasing order of width, we proceed in two parts: proving termination and proving the final sorted state.
2: 
3: ### 1. Proof of Termination
4: Let the sequence of widths of the cars in their current order from left to right be $W = (W_{\sigma(1)}, W_{\sigma(2)}, \dots, W_{\sigma(n)})$. We define an inversion in $W$ as a pair of indices $(i, j)$ such that $i < j$ but $W_{\sigma(i)} > W_{\sigma(j)}$. Let $I_W$ be the total number of such inversions.
5: 
6: A swap is performed between adjacent cars $C_{\sigma(i)}$ and $C_{\sigma(i+1)}$ if and only if $L_{\sigma(i)} < L_{\sigma(i+1)}$ and $W_{\sigma(i)} > W_{\sigma(i+1)}$. When such a swap occurs, the widths $W_{\sigma(i)}$ and $W_{\sigma(i+1)}$ are interchanged. Because $W_{\sigma(i)} > W_{\sigma(i+1)}$, the pair $(\sigma(i), \sigma(i+1))$ was an inversion before the swap and is no longer an inversion after the swap. This operation does not change the relative order of any other pairs of cars. Therefore, each swap reduces the total number of width inversions $I_W$ by exactly 1.
7: 
8: Since $I_W$ is a non-negative integer and is initially bounded by $\frac{n(n-1)}{2}$, the procedure must terminate after a finite number of moves.
9: 
10: ### 2. Proof of the Final State
11: We prove by induction on $n$ that in the final state, the cars are sorted in increasing order of width.
12: 
13: **Base Case:** For $n=2$, the cars are initially $L$-sorted ($L_1 < L_2$). If $W_1 < W_2$, no swap occurs, and the cars are $W$-sorted. If $W_1 > W_2$, they are swapped to the order $(C_2, C_1)$, resulting in widths $(W_2, W_1)$. Since $W_2 < W_1$, they are now $W$-sorted.
14: 
15: **Inductive Step:** Assume that for any set of $n-1$ cars, the procedure results in them being sorted by width. Consider $n$ cars. Let $C_{minW}$ be the car with the minimum width among the $n$ cars.
16: 
17: Observe that $C_{minW}$ can never be the left car in a swap. A swap requires the left car to have a width greater than the right car ($W_{left} > W_{right}$). Since $W_{minW}$ is the minimum width of all cars, this condition can never be satisfied if $C_{minW}$ is the left car. Consequently, $C_{minW}$ can only move to the left during the procedure.
18: 
19: In the final state, let $C_{minW}$ be at position $k$. Suppose $k > 1$. Let $C_{\sigma(k-1)}$ be the car immediately to the left of $C_{minW}$. Because $W_{\sigma(k-1)} > W_{minW}$ is always true, the pair $(C_{\sigma(k-1)}, C_{minW})$ is a width inversion. The procedure terminates only when no adjacent cars $C_i, C_{i+1}$ satisfy both $L_i < L_{i+1}$ and $W_i > W_{i+1}$. Thus, for the final state to be stable, we must have $L_{\sigma(k-1)} > L_{\sigma(k)} = L_{minW}$.
20: 
21: However, since $C_{minW}$ only moves to the left, any car that is to the left of $C_{minW}$ in the final state must have been to its left in the initial state. In the initial state, the cars were arranged in increasing order of length. Therefore, any car to the left of $C_{minW}$ must have had a length $L < L_{minW}$. This implies $L_{\sigma(k-1)} < L_{minW}$, which contradicts the requirement $L_{\sigma(k-1)} > L_{minW}$.
22: 
23: Thus, we must have $k=1$. The car with the minimum width $C_{minW}$ must occupy the first position in the final state.
24: 
25: Now consider the remaining $n-1$ cars to the right of $C_{minW}$. The swaps performed among these cars depend only on their relative lengths and widths. By the inductive hypothesis, these $n-1$ cars must be sorted in increasing order of width. Since $C_{minW}$ is the car with the overall minimum width and is located at the far left, the entire sequence of $n$ cars is sorted in increasing order of width.
26: 
27: By induction, the procedure always results in the cars being sorted by width. \(\square\)
