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
