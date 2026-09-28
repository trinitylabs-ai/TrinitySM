# Problem

101 stones are arranged in a circle, numbered 1 through 101 in order (so that stone 1 is next to stone 101). Each stone is painted either red, white, or blue. Initially, stone 101 is the only blue stone. Among the remaining stones, even-numbered stones are red, and odd-numbered stones are white.

We perform a sequence of modifications to the coloring, where in each step, we may choose a stone and repaint it a different color, as long as we ensure that no two adjacent stones are ever the same color. Prove that it is not possible to eventually reach a state where again stone 101 is the only blue stone, but among the remaining stones, all even-numbered stones are white and all odd-numbered stones are red.

# Proof A

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
