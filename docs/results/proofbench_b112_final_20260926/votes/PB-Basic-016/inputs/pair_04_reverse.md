# Problem

101 stones are arranged in a circle, numbered 1 through 101 in order (so that stone 1 is next to stone 101). Each stone is painted either red, white, or blue. Initially, stone 101 is the only blue stone. Among the remaining stones, even-numbered stones are red, and odd-numbered stones are white.

We perform a sequence of modifications to the coloring, where in each step, we may choose a stone and repaint it a different color, as long as we ensure that no two adjacent stones are ever the same color. Prove that it is not possible to eventually reach a state where again stone 101 is the only blue stone, but among the remaining stones, all even-numbered stones are white and all odd-numbered stones are red.

# Proof A

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
