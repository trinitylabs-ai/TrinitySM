# Problem

Adrian is lining up $n \geq 2$ toy cars in a row. Each car has a width and length, and no two cars have the same width or length. Initially, the cars are arranged in increasing order of length from left to right. Adrian repeatedly does the following: he chooses some two adjacent cars where the left car is shorter in length and greater in width than the right car, and he swaps them. He keeps doing this until no further moves are possible. Prove that no matter how Adrian chooses his swaps, the procedure will eventually terminate, and in the end, the cars will be sorted in increasing order of width from left to right.

# Proof A

1: To prove that the procedure eventually terminates and that the cars will be sorted in increasing order of width, we define the cars as $C_1, C_2, \dots, C_n$, where each car $C_i$ has a length $L_i$ and a width $W_i$. The cars are initially arranged such that $L_1 < L_2 < \dots < L_n$.
2: 
3: ### 1. Proof of Termination
4: Let the current sequence of cars be $C'_1, C'_2, \dots, C'_n$. We define a potential function $\text{Inv}(W)$ as the number of inversions in the sequence of widths $W'_1, W'_2, \dots, W'_n$. An inversion is a pair of indices $(i, j)$ such that $i < j$ but $W'_i > W'_j$.
5: 
6: Adrian performs a swap if he finds two adjacent cars $(C'_i, C'_{i+1})$ such that $L'_i < L'_{i+1}$ and $W'_i > W'_{i+1}$. When these two cars are swapped, the new sequence is $C'_1, \dots, C'_{i+1}, C'_i, \dots, C'_n$. 
7: - The relative order of the pair $(C'_i, C'_{i+1})$ changes from $W'_i > W'_{i+1}$ to $W'_{i+1} < W'_i$, removing exactly one inversion.
8: - The relative order of any other pair of cars $(C'_j, C'_k)$ remains unchanged because the swap only affects the two adjacent elements at positions $i$ and $i+1$.
9: 
10: Thus, every swap reduces $\text{Inv}(W)$ by exactly $1$. Since the number of inversions is a non-negative integer, the process must terminate when no further swaps are possible.
11: 
12: ### 2. Proof of Final Order
13: The process terminates when, for all $1 \leq i < n$, it is no longer the case that $(L'_i < L'_{i+1} \text{ and } W'_i > W'_{i+1})$. Since all lengths and widths are distinct, this termination condition is equivalent to:
14: \[ \text{For all } i, \text{ if } W'_i > W'_{i+1}, \text{ then } L'_i > L'_{i+1}. \]
15: We wish to prove that the final sequence is sorted by width, i.e., $W'_1 < W'_2 < \dots < W'_n$. Suppose, for the sake of contradiction, that the final sequence is not sorted by width. Then there must exist some $i$ such that $W'_i > W'_{i+1}$. By the termination condition, this implies $L'_i > L'_{i+1}$.
16: 
17: Let the cars in these positions be $C'_i = C_a$ and $C'_{i+1} = C_b$. We then have:
18: 1. $L_a > L_b$, which implies $a > b$ because the cars were initially sorted by length ($L_1 < L_2 < \dots < L_n$).
19: 2. $W_a > W_b$.
20: 
21: In any sequence of adjacent swaps, the relative order of two elements $C_x$ and $C_y$ changes if and only if they are the two elements being swapped. If a pair of cars can never satisfy the swap condition, their relative order must remain the same as their initial relative order.
22: 
23: Let us check if $C_b$ and $C_a$ could have been swapped:
24: - If they are in the order $(C_b, C_a)$: The swap condition requires the left car to be shorter and wider than the right car. Here, $L_b < L_a$ (True), but $W_b > W_a$ is False because $W_a > W_b$. Thus, they cannot be swapped in this order.
25: - If they are in the order $(C_a, C_b)$: The swap condition requires $L_a < L_b$ and $W_a > W_b$. Here, $W_a > W_b$ is True, but $L_a < L_b$ is False because $L_a > L_b$. Thus, they cannot be swapped in this order.
26: 
27: Because $C_b$ and $C_a$ can never satisfy the swap condition regardless of their positions, their relative order must remain the same as their initial relative order. Since $b < a$, $C_b$ was initially to the left of $C_a$, and therefore $C_b$ must remain to the left of $C_a$ in the final state. This contradicts our finding that $C'_i = C_a$ and $C'_{i+1} = C_b$, which places $C_a$ to the left of $C_b$.
28: 
29: Therefore, no such $i$ exists, and the final sequence of widths must be $W'_1 < W'_2 < \dots < W'_n$.
30: \(\square\)

# Proof B

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
