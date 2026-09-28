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
