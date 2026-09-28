# Problem

Adrian is lining up $n \geq 2$ toy cars in a row. Each car has a width and length, and no two cars have the same width or length. Initially, the cars are arranged in increasing order of length from left to right. Adrian repeatedly does the following: he chooses some two adjacent cars where the left car is shorter in length and greater in width than the right car, and he swaps them. He keeps doing this until no further moves are possible. Prove that no matter how Adrian chooses his swaps, the procedure will eventually terminate, and in the end, the cars will be sorted in increasing order of width from left to right.

# Proof A

1: To prove that the procedure terminates and that the cars end up sorted in increasing order of width, we analyze the properties of the swaps and use induction on the number of cars $n$.
2: 
3: ### 1. Proof of Termination
4: Let the cars be denoted by $C_1, C_2, \dots, C_n$ based on their initial positions, such that their lengths are $l_1 < l_2 < \dots < l_n$. Let the current arrangement of cars be $S = (S_1, S_2, \dots, S_n)$.
5: A swap occurs between adjacent cars $S_k$ and $S_{k+1}$ if and only if $l_{S_k} < l_{S_{k+1}}$ and $w_{S_k} > w_{S_{k+1}}$.
6: Consider the number of pairs $(S_i, S_j)$ with $i < j$ such that $l_{S_i} < l_{S_j}$. Initially, since the cars are sorted by length, every pair $(i, j)$ with $i < j$ satisfies $l_i < l_j$, giving a total of $\binom{n}{2}$ such pairs.
7: When a swap is performed on adjacent cars $S_k$ and $S_{k+1}$, the condition $l_{S_k} < l_{S_{k+1}}$ must be met. After the swap, the new order is $S_{k+1}, S_k$, so the length of the car on the left is now greater than the length of the car on the right ($l_{S_{k+1}} > l_{S_k}$). The relative order of all other pairs $(S_i, S_j)$ remains unchanged. Thus, each swap decreases the number of pairs $(S_i, S_j)$ with $i < j$ and $l_{S_i} < l_{S_j}$ by exactly one.
8: Since this count is a non-negative integer, the procedure must terminate in at most $\binom{n}{2}$ steps.
9: 
10: ### 2. Proof of Final Order
11: We prove by induction on $n$ that the final state $S = (S_1, S_2, \dots, S_n)$ is sorted in increasing order of width, i.e., $w_{S_1} < w_{S_2} < \dots < w_{S_n}$.
12: 
13: **Base Case:** For $n=2$, the cars are $(C_1, C_2)$ with $l_1 < l_2$. If $w_1 > w_2$, they are swapped to $(C_2, C_1)$, resulting in $w_{S_1} = w_2 < w_1 = w_{S_2}$. If $w_1 < w_2$, no swap occurs, and $w_{S_1} = w_1 < w_2 = w_{S_2}$. In both cases, the final state is sorted by width.
14: 
15: **Inductive Step:** Assume the statement holds for any $n-1$ cars initially sorted by length. Let $C_{p_1}$ be the car with the minimum width among the $n$ cars.
16: First, we analyze the possible movements of $C_{p_1}$:
17: - $C_{p_1}$ can never move to the right. For $C_{p_1}$ to move to the right, it must be the left car in a swap $(S_k, S_{k+1})$. This requires $w_{S_k} > w_{S_{k+1}}$, but since $w_{p_1}$ is the minimum width, $w_{p_1} > w_{S_{k+1}}$ is impossible.
18: - $C_{p_1}$ can only move to the left. For $C_{p_1}$ to move to the left of $S_k$, $S_k$ must be the left car in a swap. This requires $l_{S_k} < l_{S_{k+1}} = l_{p_1}$.
19: 
20: Let $L(C_{p_1})$ be the set of cars to the left of $C_{p_1}$. Initially, $L(C_{p_1}) = \{C_1, \dots, C_{p_1-1}\}$. Since $C_{p_1}$ can only move left, no car from the right of $C_{p_1}$ can ever move to its left. Thus, at any point in the process, $L(C_{p_1}) \subseteq \{C_1, \dots, C_{p_1-1}\}$.
21: In the final stable state $S$, suppose $S_j = C_{p_1}$ for some $j > 1$. For the state to be stable, the adjacent pair $(S_{j-1}, S_j)$ must not be swappable. This requires:
22: $$\neg (l_{S_{j-1}} < l_{S_j} \text{ and } w_{S_{j-1}} > w_{S_j})$$
23: Since $w_{S_j} = w_{p_1}$ is the minimum width, $w_{S_{j-1}} > w_{S_j}$ is always true. Thus, stability requires $l_{S_{j-1}} > l_{S_j} = l_{p_1}$. However, we established that any car $S_{j-1}$ to the left of $C_{p_1}$ must be from the set $\{C_1, \dots, C_{p_1-1}\}$, all of which have lengths $l_k < l_{p_1}$. This is a contradiction.
24: Therefore, we must have $j=1$, so $S_1 = C_{p_1}$.
25: 
26: Once $C_{p_1}$ is at the first position, it can never be swapped again. The remaining $n-1$ cars $(S_2, \dots, S_n)$ are now subject to the same swap rule. Let $X$ be the set of these $n-1$ cars. The relative order of any two cars in $X$ is only changed when they are adjacent and satisfy the swap condition. Since $C_{p_1}$ only moves to the left, it does not permanently block any two cars in $X$ from becoming adjacent. Furthermore, the relative order of cars in $X$ is unaffected by any swap involving $C_{p_1}$. Because the cars in $X$ were initially sorted by length relative to each other, the process acting on $X$ is equivalent to the original problem with $n-1$ cars. By the inductive hypothesis, the final relative order of these $n-1$ cars will be sorted by width.
27: 
28: Since $S_1$ has the minimum width and $(S_2, \dots, S_n)$ are sorted by width, the entire sequence $S$ is sorted in increasing order of width. $\square$

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
