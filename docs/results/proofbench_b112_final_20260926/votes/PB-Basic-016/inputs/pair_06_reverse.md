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
