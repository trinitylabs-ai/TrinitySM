# Problem

101 stones are arranged in a circle, numbered 1 through 101 in order (so that stone 1 is next to stone 101). Each stone is painted either red, white, or blue. Initially, stone 101 is the only blue stone. Among the remaining stones, even-numbered stones are red, and odd-numbered stones are white.

We perform a sequence of modifications to the coloring, where in each step, we may choose a stone and repaint it a different color, as long as we ensure that no two adjacent stones are ever the same color. Prove that it is not possible to eventually reach a state where again stone 101 is the only blue stone, but among the remaining stones, all even-numbered stones are white and all odd-numbered stones are red.

# Proof A

1: To prove that the target state cannot be reached from the initial state, we introduce an invariant based on the 3-coloring of a cycle graph, often referred to as the winding number or index.
2: 
3: **1. Definition of the Invariant**
4: Let the colors be represented by the elements of $\mathbb{Z}_3 = \{0, 1, 2\}$, where $0$ corresponds to Red, $1$ to White, and $2$ to Blue. A coloring of the 101 stones is a function $c: \{1, 2, \dots, 101\} \to \{0, 1, 2\}$. The problem states that no two adjacent stones can have the same color, which means $c(i) \neq c(i+1)$ for all $i \in \{1, \dots, 101\}$, where indices are taken modulo 101 (so $c(102) = c(1)$).
5: 
6: For any two adjacent stones with colors $a$ and $b$, we define the signed difference $\text{sgn}(a, b)$ as follows:
7: $$\text{sgn}(a, b) = \begin{cases} 1 & \text{if } b - a \equiv 1 \pmod 3 \\ -1 & \text{if } b - a \equiv 2 \pmod 3 \end{cases}$$
8: Since $a \neq b$, the difference $b-a \pmod 3$ is always either $1$ or $2$. The winding number $W$ of a coloring $c$ is the sum of these signed differences around the circle:
9: $$W = \sum_{i=1}^{101} \text{sgn}(c(i), c(i+1)), \quad \text{where } c(102) = c(1)$$
10: 
11: **2. Invariance Under the Modification Operation**
12: A modification consists of choosing a stone $j$ and repainting it from color $b$ to $b'$, provided that the coloring remains valid. Let $a = c(j-1)$ and $c = c(j+1)$ be the colors of the neighbors of stone $j$. For the coloring to be valid, both $b$ and $b'$ must be different from $a$ and $c$.
13: - If $a \neq c$, there is only one color in $\{0, 1, 2\}$ that is different from both $a$ and $c$. Thus, $b$ and $b'$ must be the same color, meaning no change is possible.
14: - If $a = c$, then $b$ and $b'$ must be the two colors other than $a$. The contribution of stone $j$ to the sum $W$ is $\text{sgn}(a, b) + \text{sgn}(b, a)$. Since $\text{sgn}(b, a) = -\text{sgn}(a, b)$, this sum is $0$. Similarly, the contribution after repainting is $\text{sgn}(a, b') + \text{sgn}(b', a) = 0$.
15: 
16: Consequently, the winding number $W$ is invariant under any sequence of valid modifications.
17: 
18: **3. Calculation for Initial and Target States**
19: In the initial state $S_0$, stone 101 is blue ($c(101)=2$), even stones are red ($c(2k)=0$), and odd stones are white ($c(2k-1)=1$ for $k=1, \dots, 50$).
20: The differences are:
21: - For $i=1, 3, \dots, 99$: $\text{sgn}(c(i), c(i+1)) = \text{sgn}(1, 0) = -1$ (since $0-1 \equiv 2 \pmod 3$).
22: - For $i=2, 4, \dots, 98$: $\text{sgn}(c(i), c(i+1)) = \text{sgn}(0, 1) = 1$ (since $1-0 \equiv 1 \pmod 3$).
23: - For $i=100$: $\text{sgn}(c(100), c(101)) = \text{sgn}(0, 2) = -1$ (since $2-0 \equiv 2 \pmod 3$).
24: - For $i=101$: $\text{sgn}(c(101), c(1)) = \text{sgn}(2, 1) = -1$ (since $1-2 \equiv 2 \pmod 3$).
25: Summing these, we get:
26: $$W_0 = \sum_{k=1}^{49} (-1 + 1) + \text{sgn}(c(99), c(100)) + \text{sgn}(c(100), c(101)) + \text{sgn}(c(101), c(1)) = 0 + (-1) + (-1) + (-1) = -3$$
27: 
28: In the target state $S_f$, stone 101 is blue ($c(101)=2$), even stones are white ($c(2k)=1$), and odd stones are red ($c(2k-1)=0$ for $k=1, \dots, 50$).
29: The differences are:
30: - For $i=1, 3, \dots, 99$: $\text{sgn}(c(i), c(i+1)) = \text{sgn}(0, 1) = 1$.
31: - For $i=2, 4, \dots, 98$: $\text{sgn}(c(i), c(i+1)) = \text{sgn}(1, 0) = -1$.
32: - For $i=100$: $\text{sgn}(c(100), c(101)) = \text{sgn}(1, 2) = 1$ (since $2-1 \equiv 1 \pmod 3$).
33: - For $i=101$: $\text{sgn}(c(101), c(1)) = \text{sgn}(2, 0) = 1$ (since $0-2 \equiv 1 \pmod 3$).
34: Summing these, we get:
35: $$W_f = \sum_{k=1}^{49} (1 - 1) + \text{sgn}(c(99), c(100)) + \text{sgn}(c(100), c(101)) + \text{sgn}(c(101), c(1)) = 0 + 1 + 1 + 1 = 3$$
36: 
37: Since $W_0 = -3$ and $W_f = 3$, and $W$ is an invariant, it is impossible to reach the target state from the initial state. $\square$

# Proof B

1: To prove that it is impossible to reach the target state from the initial state, we utilize an invariant associated with 3-colorings of a cycle graph, known as the winding number.
2: 
3: ### 1. Definition of the Winding Number
4: Let the three colors be represented by the elements of the cyclic group $\mathbb{Z}_3$: Red ($R$) $\to 0$, White ($W$) $\to 1$, and Blue ($B$) $\to 2$. A coloring of the 101 stones is a sequence $c_1, c_2, \dots, c_{101}$ where $c_i \in \{0, 1, 2\}$. The adjacency constraint ensures that $c_i \neq c_{i+1}$ for all $i$ (where $c_{102} = c_1$).
5: 
6: For each pair of adjacent stones $i$ and $i+1$, we define the difference $x_i$ as the unique value in $\{1, -1\}$ such that:
7: \[ c_{i+1} - c_i \equiv x_i \pmod{3} \]
8: Specifically, $x_i = 1$ if $c_{i+1} - c_i \equiv 1 \pmod{3}$ and $x_i = -1$ if $c_{i+1} - c_i \equiv 2 \pmod{3}$.
9: The winding number $W$ of the coloring is the sum of these differences:
10: \[ W = \sum_{i=1}^{101} x_i \]
11: Note that $W \equiv \sum_{i=1}^{101} (c_{i+1} - c_i) \equiv 0 \pmod{3}$. Since $W$ is the sum of 101 values of $\pm 1$, $W$ must be an odd multiple of 3.
12: 
13: ### 2. Invariance under Modifications
14: A modification consists of changing the color of a single stone $k$ from $c_k$ to $c_k'$, provided the adjacency constraint is maintained. The only terms in the sum $W$ that change are $x_{k-1}$ and $x_k$. The colors of the neighbors $c_{k-1}$ and $c_{k+1}$ remain fixed.
15: 
16: For a modification to be possible, both the current color $c_k$ and the new color $c_k'$ must be different from $c_{k-1}$ and $c_{k+1}$. In a 3-coloring, if $c_{k-1} \neq c_{k+1}$, there is only one color available in $\{0, 1, 2\} \setminus \{c_{k-1}, c_{k+1}\}$. Thus, $c_k$ cannot be changed to a different color $c_k'$.
17: 
18: If $c_{k-1} = c_{k+1} = a$, then there are two available colors for stone $k$ in $\{0, 1, 2\} \setminus \{a\}$. Let these colors be $b$ and $c$.
19: - If $c_k = b$, then $x_{k-1} \equiv b-a \pmod{3}$ and $x_k \equiv a-b \pmod{3}$. Since $b-a$ and $a-b$ are additive inverses in $\mathbb{Z}_3$, one must be $1 \pmod 3$ and the other $-1 \pmod 3$. Thus, $x_{k-1} + x_k = 1 + (-1) = 0$.
20: - If $c_k' = c$, then $x_{k-1}' \equiv c-a \pmod{3}$ and $x_k' \equiv a-c \pmod{3}$. Similarly, $x_{k-1}' + x_k' = 0$.
21: 
22: In every valid modification, the local sum $x_{k-1} + x_k$ remains 0. Consequently, the total sum $W$ is invariant under any sequence of modifications.
23: 
24: ### 3. Calculation for the Given States
25: **Initial State ($S_0$):** Stone 101 is Blue (2), stones $1, 3, \dots, 99$ are White (1), and stones $2, 4, \dots, 100$ are Red (0).
26: - For $i \in \{1, 3, \dots, 97\}$, $x_i = c_{i+1} - c_i = 0 - 1 = -1 \equiv 2 \pmod{3} \implies x_i = -1$.
27: - For $i \in \{2, 4, \dots, 98\}$, $x_i = c_{i+1} - c_i = 1 - 0 = 1 \equiv 1 \pmod{3} \implies x_i = 1$.
28: - These 98 terms sum to $\sum_{i=1}^{98} x_i = 49(-1) + 49(1) = 0$.
29: - $x_{99} = c_{100} - c_{99} = 0 - 1 = -1 \equiv 2 \pmod{3} \implies x_{99} = -1$.
30: - $x_{100} = c_{101} - c_{100} = 2 - 0 = 2 \equiv 2 \pmod{3} \implies x_{100} = -1$.
31: - $x_{101} = c_1 - c_{101} = 1 - 2 = -1 \equiv 2 \pmod{3} \implies x_{101} = -1$.
32: The sum is $W_0 = 0 + (-1) + (-1) + (-1) = -3$.
33: 
34: **Target State ($S_f$):** Stone 101 is Blue (2), stones $1, 3, \dots, 99$ are Red (0), and stones $2, 4, \dots, 100$ are White (1).
35: - For $i \in \{1, 3, \dots, 97\}$, $x_i = c_{i+1} - c_i = 1 - 0 = 1 \equiv 1 \pmod{3} \implies x_i = 1$.
36: - For $i \in \{2, 4, \dots, 98\}$, $x_i = c_{i+1} - c_i = 0 - 1 = -1 \equiv 2 \pmod{3} \implies x_i = -1$.
37: - These 98 terms sum to $\sum_{i=1}^{98} x_i = 49(1) + 49(-1) = 0$.
38: - $x_{99} = c_{100} - c_{99} = 1 - 0 = 1 \equiv 1 \pmod{3} \implies x_{99} = 1$.
39: - $x_{100} = c_{101} - c_{100} = 2 - 1 = 1 \equiv 1 \pmod{3} \implies x_{100} = 1$.
40: - $x_{101} = c_1 - c_{101} = 0 - 2 = -2 \equiv 1 \pmod{3} \implies x_{101} = 1$.
41: The sum is $W_f = 0 + 1 + 1 + 1 = 3$.
42: 
43: Since $W_0 = -3$ and $W_f = 3$, and $W$ is invariant under the allowed operations, it is impossible to reach the target state from the initial state.
