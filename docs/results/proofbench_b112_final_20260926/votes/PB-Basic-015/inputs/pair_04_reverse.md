# Problem

Adrian is lining up $n \geq 2$ toy cars in a row. Each car has a width and length, and no two cars have the same width or length. Initially, the cars are arranged in increasing order of length from left to right. Adrian repeatedly does the following: he chooses some two adjacent cars where the left car is shorter in length and greater in width than the right car, and he swaps them. He keeps doing this until no further moves are possible. Prove that no matter how Adrian chooses his swaps, the procedure will eventually terminate, and in the end, the cars will be sorted in increasing order of width from left to right.

# Proof A

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

# Proof B

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
