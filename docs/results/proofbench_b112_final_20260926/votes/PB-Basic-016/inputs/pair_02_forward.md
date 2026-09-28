# Problem

101 stones are arranged in a circle, numbered 1 through 101 in order (so that stone 1 is next to stone 101). Each stone is painted either red, white, or blue. Initially, stone 101 is the only blue stone. Among the remaining stones, even-numbered stones are red, and odd-numbered stones are white.

We perform a sequence of modifications to the coloring, where in each step, we may choose a stone and repaint it a different color, as long as we ensure that no two adjacent stones are ever the same color. Prove that it is not possible to eventually reach a state where again stone 101 is the only blue stone, but among the remaining stones, all even-numbered stones are white and all odd-numbered stones are red.

# Proof A

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

# Proof B

1: To prove that the final state $S_f$ cannot be reached from the initial state $S_0$, we use the concept of the winding number, which is an invariant for 3-colorings of a cycle graph.
2: 
3: **1. Definition of the Winding Number**
4: Let the three colors be represented by the elements of $\mathbb{Z}_3 = \{0, 1, 2\}$. We define the transition between two adjacent colors $a, b \in \mathbb{Z}_3$ as a signed value:
5: \[ \text{step}(a, b) = \begin{cases} 1 & \text{if } b - a \equiv 1 \pmod 3 \\ -1 & \text{if } b - a \equiv 2 \pmod 3 \end{cases} \]
6: Since the stones are arranged in a circle, we consider the sequence of colors $C(1), C(2), \dots, C(101), C(102)=C(1)$. The total sum of steps around the circle is:
7: \[ S = \sum_{i=1}^{101} \text{step}(C(i), C(i+1)) \]
8: Since the path returns to the starting color, the total displacement in $\mathbb{Z}_3$ must be a multiple of 3. Thus, $S = 3w$ for some integer $w$, which is defined as the winding number of the coloring.
9: 
10: **2. Invariance of the Winding Number**
11: A modification consists of repainting a stone $i$ from color $C(i)$ to $C'(i)$, provided that no two adjacent stones have the same color. The only terms in the sum $S$ that change are $\text{step}(C(i-1), C(i))$ and $\text{step}(C(i), C(i+1))$.
12: - If $C(i-1) = C(i+1) = a$, the stone $i$ must have a color $b \neq a$. There are only two such colors in $\mathbb{Z}_3$. If $b = a+1 \pmod 3$, then $\text{step}(a, b) = 1$ and $\text{step}(b, a) = -1$, summing to 0. If $b = a-1 \pmod 3$, then $\text{step}(a, b) = -1$ and $\text{step}(b, a) = 1$, also summing to 0. Thus, changing $C(i)$ between the two available colors does not change the sum $S$.
13: - If $C(i-1) \neq C(i+1)$, let $C(i-1) = a$ and $C(i+1) = b$. The color $C(i)$ must be the unique third color $c \in \mathbb{Z}_3 \setminus \{a, b\}$. In this case, $C(i)$ cannot be changed to any other color without violating the adjacency constraint (since any other color would be either $a$ or $b$).
14: Since the sum $S$ remains unchanged under any valid operation, the winding number $w$ is an invariant of the process.
15: 
16: **3. Calculation for the Initial and Final States**
17: Let the colors be Red (0), White (1), and Blue (2).
18: In the initial state $S_0$:
19: - Stone 101 is Blue (2).
20: - Even stones $2, 4, \dots, 100$ are Red (0).
21: - Odd stones $1, 3, \dots, 99$ are White (1).
22: The transitions are:
23: - For $i \in \{1, 3, \dots, 99\}$, $C(i)=1$ and $C(i+1)=0$, so $\text{step}(1, 0) = -1$. (50 such transitions).
24: - For $i \in \{2, 4, \dots, 98\}$, $C(i)=0$ and $C(i+1)=1$, so $\text{step}(0, 1) = 1$. (49 such transitions).
25: - For $i=100$, $C(100)=0$ and $C(101)=2$, so $\text{step}(0, 2) = -1$.
26: - For $i=101$, $C(101)=2$ and $C(1)=1$, so $\text{step}(2, 1) = -1$.
27: The sum is $S_0 = 50(-1) + 49(1) - 1 - 1 = -50 + 49 - 2 = -3$. Thus, $w_0 = -1$.
28: 
29: In the final state $S_f$:
30: - Stone 101 is Blue (2).
31: - Even stones $2, 4, \dots, 100$ are White (1).
32: - Odd stones $1, 3, \dots, 99$ are Red (0).
33: The transitions are:
34: - For $i \in \{1, 3, \dots, 99\}$, $C(i)=0$ and $C(i+1)=1$, so $\text{step}(0, 1) = 1$. (50 such transitions).
35: - For $i \in \{2, 4, \dots, 98\}$, $C(i)=1$ and $C(i+1)=0$, so $\text{step}(1, 0) = -1$. (49 such transitions).
36: - For $i=100$, $C(100)=1$ and $C(101)=2$, so $\text{step}(1, 2) = 1$.
37: - For $i=101$, $C(101)=2$ and $C(1)=0$, so $\text{step}(2, 0) = 1$.
38: The sum is $S_f = 50(1) + 49(-1) + 1 + 1 = 50 - 49 + 2 = 3$. Thus, $w_f = 1$.
39: 
40: Since $w_0 = -1$ and $w_f = 1$, and the winding number is invariant under the allowed modifications, it is impossible to reach state $S_f$ from state $S_0$.
41: 
42: \(\square\)
