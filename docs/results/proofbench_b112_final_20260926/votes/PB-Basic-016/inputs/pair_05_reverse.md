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

1: To prove that the target coloring cannot be reached from the initial coloring, we define an invariant of the coloring states known as the winding number.
2: 
3: ### 1. Definition of the Winding Number
4: Let the three colors be $R, W,$ and $B$. We fix a cyclic order of these colors: $R \to W \to B \to R$. For any two distinct colors $x, y \in \{R, W, B\}$, we define the signed distance $\text{dist}(x, y)$ as follows:
5: - $\text{dist}(x, y) = 1$ if the transition from $x$ to $y$ follows the cyclic order (i.e., $(x, y) \in \{(R, W), (W, B), (B, R)\}$).
6: - $\text{dist}(x, y) = -1$ if the transition from $x$ to $y$ goes against the cyclic order (i.e., $(x, y) \in \{(W, R), (B, W), (R, B)\}$).
7: 
8: Given a proper 3-coloring $f$ of the 101 stones arranged in a circle, the total sum $S(f)$ is:
9: \[ S(f) = \sum_{i=1}^{100} \text{dist}(f(i), f(i+1)) + \text{dist}(f(101), f(1)) \]
10: Since $\text{dist}(x, y) \equiv f(y) - f(x) \pmod 3$ (assigning $R=0, W=1, B=2$), the sum $S(f)$ is always a multiple of 3. The winding number is defined as $w(f) = \frac{1}{3} S(f)$.
11: 
12: ### 2. Invariance under the Modification Rule
13: We examine the change in $S(f)$ when a stone $k$ is repainted from color $c$ to $c'$. For the coloring to remain proper, we must have $c' \neq f(k-1)$ and $c' \neq f(k+1)$.
14: - If $f(k-1) \neq f(k+1)$, let $f(k-1) = a$ and $f(k+1) = b$. Since $a, b, c$ must be distinct for the coloring to be proper, $c$ is the only color in $\{R, W, B\}$ that is not $a$ or $b$. Thus, any change to $c'$ would result in $c' = a$ or $c' = b$, which is forbidden. In this case, the color of stone $k$ cannot be changed.
15: - If $f(k-1) = f(k+1) = a$, the stone $k$ can be any color in $\{R, W, B\} \setminus \{a\}$. Let these colors be $b$ and $c$. Changing the color of stone $k$ from $b$ to $c$ modifies two terms in the sum $S(f)$: $\text{dist}(f(k-1), f(k))$ and $\text{dist}(f(k), f(k+1))$. The change in the sum is:
16: \[ \Delta S = [\text{dist}(a, c) + \text{dist}(c, a)] - [\text{dist}(a, b) + \text{dist}(b, a)] \]
17: Since $\text{dist}(x, y) = -\text{dist}(y, x)$, we have $\text{dist}(a, c) + \text{dist}(c, a) = 0$ and $\text{dist}(a, b) + \text{dist}(b, a) = 0$. Thus, $\Delta S = 0$.
18: 
19: Consequently, the winding number $w(f)$ is an invariant of the process.
20: 
21: ### 3. Comparison of Initial and Target States
22: **Initial State $C_0$:**
23: Stone 101 is $B$, and for $i \in \{1, \dots, 100\}$, stone $i$ is $W$ if $i$ is odd and $R$ if $i$ is even.
24: - For $i=1, 3, \dots, 99$, $\text{dist}(f(i), f(i+1)) = \text{dist}(W, R) = -1$ (50 terms).
25: - For $i=2, 4, \dots, 98$, $\text{dist}(f(i), f(i+1)) = \text{dist}(R, W) = 1$ (49 terms).
26: - For $i=100$, $\text{dist}(f(100), f(101)) = \text{dist}(R, B) = -1$.
27: - For $i=101$, $\text{dist}(f(101), f(1)) = \text{dist}(B, W) = -1$.
28: Sum $S(C_0) = 50(-1) + 49(1) - 1 - 1 = -3$, so $w(C_0) = -1$.
29: 
30: **Target State $C_{final}$:**
31: Stone 101 is $B$, and for $i \in \{1, \dots, 100\}$, stone $i$ is $R$ if $i$ is odd and $W$ if $i$ is even.
32: - For $i=1, 3, \dots, 99$, $\text{dist}(f(i), f(i+1)) = \text{dist}(R, W) = 1$ (50 terms).
33: - For $i=2, 4, \dots, 98$, $\text{dist}(f(i), f(i+1)) = \text{dist}(W, R) = -1$ (49 terms).
34: - For $i=100$, $\text{dist}(f(100), f(101)) = \text{dist}(W, B) = 1$.
35: - For $i=101$, $\text{dist}(f(101), f(1)) = \text{dist}(B, R) = 1$.
36: Sum $S(C_{final}) = 50(1) + 49(-1) + 1 + 1 = 3$, so $w(C_{final}) = 1$.
37: 
38: Since $w(C_0) = -1$ and $w(C_{final}) = 1$, and the winding number is invariant under the allowed modifications, it is impossible to reach the target state from the initial state.
39: 
40: \(\square\)
