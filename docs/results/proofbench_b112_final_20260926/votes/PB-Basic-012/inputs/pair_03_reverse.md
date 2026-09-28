# Problem

Consider a positive integer $n$. We define $f(n)$ as the number of pairs of paths on an $n \times n$ grid that:

 (1) Both paths start at $(0, 0)$ (bottom left corner) and end at $(n, n)$ (top right corner).

 (2) Both paths allow only right or up movements (one unit each).

 (3) The $y$ coordinate of the first path never exceeds the y coordinate of the second path at any timestep.

 For example, when $n = 2$, consider the following pair of paths:

 The first path: $(0,0) \rightarrow (1,0) \rightarrow (1,1) \rightarrow (2,1) \rightarrow (2,2)$
 The second path: $(0,0) \rightarrow (1,0) \rightarrow (2,0) \rightarrow (2,1) \rightarrow(2,2)$
 The example is invalid because after 2 steps, the y coordinate of the first path (1) is larger than the y coordinate of the second path (0).

 However, the following example is valid,

 The first path: $(0,0) \rightarrow (1,0) \rightarrow (2,0) \rightarrow (2,1) \rightarrow (2,2)$
 The second path: $(0,0) \rightarrow (1,0) \rightarrow (1,1) \rightarrow (2,1) \rightarrow (2,2)$

 since the y coordinate of the first path is never larger than the second path. Find $f(10)$.

# Proof A

1: To find $f(n)$, the number of pairs of paths $P_1$ and $P_2$ from $(0,0)$ to $(n,n)$ such that the $y$-coordinate of the first path $y_1(t)$ never exceeds the $y$-coordinate of the second path $y_2(t)$ at any timestep $t \in \{0, 1, \dots, 2n\}$, we analyze the condition $y_1(t) \le y_2(t)$.
2: 
3: Since each path consists of $2n$ moves (Right or Up), at timestep $t$, the coordinates $(x, y)$ satisfy $x + y = t$. The condition $y_1(t) \le y_2(t)$ is therefore equivalent to $t - x_1(t) \le t - x_2(t)$, which simplifies to $x_1(t) \ge x_2(t)$.
4: 
5: We can transform this problem into a non-intersecting path problem by shifting the paths. Define:
6: 1. $P_1'$ as $P_1$ shifted by $(1, 0)$, so $P_1'$ starts at $A_1 = (1, 0)$ and ends at $B_1 = (n+1, n)$.
7: 2. $P_2'$ as $P_2$ shifted by $(0, 1)$, so $P_2'$ starts at $A_2 = (0, 1)$ and ends at $B_2 = (n, n+1)$.
8: 
9: Two paths $P_1'$ and $P_2'$ intersect if there exists a timestep $t$ such that $(x_1(t)+1, y_1(t)) = (x_2(t), y_2(t)+1)$. This equality holds if and only if $y_1(t) = y_2(t) + 1$. Since $y_1(0) = y_2(0) = 0$ and $y_1(2n) = y_2(2n) = n$, and the $y$-coordinates increase by at most 1 at each step, the difference $y_1(t) - y_2(t)$ changes by at most 1 at each step. Thus, the condition $y_1(t) \le y_2(t)$ for all $t$ is equivalent to the condition that $y_1(t) - y_2(t)$ never equals 1, which is equivalent to the condition that $P_1'$ and $P_2'$ never intersect.
10: 
11: By the Lindström-Gessel-Viennot (LGV) Lemma, the number of such non-intersecting pairs is given by the determinant:
12: \[ f(n) = \det \begin{pmatrix} N(A_1, B_1) & N(A_1, B_2) \\ N(A_2, B_1) & N(A_2, B_2) \end{pmatrix} \]
13: where $N(A, B)$ is the number of paths from $A$ to $B$. The LGV Lemma states that the determinant is the sum over all permutations $\sigma$ of $\text{sgn}(\sigma) \prod N(A_i, B_{\sigma(i)})$, where only permutations that allow non-intersecting paths contribute. For our points $A_1(1,0), A_2(0,1), B_1(n+1,n), B_2(n,n+1)$, any path from $A_1$ to $B_2$ and any path from $A_2$ to $B_1$ must intersect. Specifically, if $P_1'$ goes from $A_1$ to $B_2$ and $P_2'$ goes from $A_2$ to $B_1$, then $x_1(0) = 1$ and $x_2(0) = 0$, so $x_1(0) > x_2(0)$, while $x_1(2n) = n$ and $x_2(2n) = n+1$, so $x_1(2n) < x_2(2n)$. Since the $x$-coordinates change by at most 1 at each step, there must be some $t$ where $x_1(t) = x_2(t)$, which implies $y_1(t) = y_2(t)$ (since $x+y=t$), and thus the paths intersect. Therefore, only the identity permutation contributes to the sum.
14: 
15: The number of paths are:
16: - $N(A_1, B_1) = \binom{(n+1-1) + (n-0)}{n} = \binom{2n}{n}$
17: - $N(A_2, B_2) = \binom{(n-0) + (n+1-1)}{n} = \binom{2n}{n}$
18: - $N(A_1, B_2) = \binom{(n-1) + (n+1-0)}{n-1} = \binom{2n}{n-1}$
19: - $N(A_2, B_1) = \binom{(n+1-0) + (n-1)}{n+1} = \binom{2n}{n+1}$
20: 
21: Since $\binom{2n}{n-1} = \binom{2n}{n+1}$, the formula is:
22: \[ f(n) = \binom{2n}{n}^2 - \binom{2n}{n-1}^2 = \left(\binom{2n}{n} - \binom{2n}{n-1}\right)\left(\binom{2n}{n} + \binom{2n}{n-1}\right) = C_n \binom{2n+1}{n} \]
23: where $C_n = \frac{1}{n+1}\binom{2n}{n}$ is the $n$-th Catalan number. For $n=10$:
24: 1. $\binom{20}{10} = 184,756$
25: 2. $\binom{20}{9} = \frac{10}{11} \binom{20}{10} = 167,960$
26: 3. $C_{10} = 184,756 - 167,960 = 16,796$
27: 4. $\binom{21}{10} = \binom{20}{10} + \binom{20}{9} = 184,756 + 167,960 = 352,716$
28: 
29: Multiplying these values:
30: \[ f(10) = 16,796 \times 352,716 \]
31: \[ 16,796 \times 300,000 = 5,038,800,000 \]
32: \[ 16,796 \times 50,000 = 839,800,000 \]
33: \[ 16,796 \times 2,000 = 33,592,000 \]
34: \[ 16,796 \times 700 = 11,757,200 \]
35: \[ 16,796 \times 16 = 268,736 \]
36: Summing these gives:
37: \[ 5,038,800,000 + 839,800,000 + 33,592,000 + 11,757,200 + 268,736 = 5,924,217,936 \]
38: 
39: The number of pairs of paths is $5,924,217,936$.

# Proof B

1: To find the number of pairs of paths $f(n)$ on an $n \times n$ grid from $(0,0)$ to $(n,n)$ such that the $y$-coordinate of the first path $P_1$ never exceeds the $y$-coordinate of the second path $P_2$ at any timestep $t \in \{0, 1, \dots, 2n\}$, we define the paths by their sequences of movements.
2: 
3: Each path consists of $n$ Right (R) moves and $n$ Up (U) moves. Let $(x_{1,t}, y_{1,t})$ and $(x_{2,t}, y_{2,t})$ be the coordinates of $P_1$ and $P_2$ after $t$ steps. The condition is $y_{1,t} \le y_{2,t}$ for all $t$. Since $x_{i,t} + y_{i,t} = t$, this is equivalent to $x_{1,t} \ge x_{2,t}$.
4: 
5: We represent the pair of paths as a sequence of $2n$ pairs of moves $(m_{1,t}, m_{2,t})$. There are four possible move pairs at each timestep:
6: 1. Both paths move Right: $(R, R)$
7: 2. $P_1$ moves Right, $P_2$ moves Up: $(R, U)$
8: 3. $P_1$ moves Up, $P_2$ moves Right: $(U, R)$
9: 4. Both paths move Up: $(U, U)$
10: 
11: Let $n_{RR}, n_{RU}, n_{UR}, n_{UU}$ be the total number of times each move pair occurs in the sequence. Since both paths end at $(n,n)$, the total number of Up moves for each path must be $n$:
12: - For $P_1$: $n_{UR} + n_{UU} = n$
13: - For $P_2$: $n_{RU} + n_{UU} = n$
14: This implies $n_{RU} = n_{UR}$. Let $k = n_{RU} = n_{UR}$. Then $n_{UU} = n - k$ and $n_{RR} = 2n - (2k + n - k) = n - k$.
15: 
16: The condition $y_{1,t} \le y_{2,t}$ means that at any timestep $t$, the number of $(R, U)$ moves must be greater than or equal to the number of $(U, R)$ moves. The $(R, R)$ and $(U, U)$ moves do not affect the difference $y_{2,t} - y_{1,t}$. Thus, the subsequence of the $2k$ "differing" moves must form a Dyck path. The number of such sequences is given by the $k$-th Catalan number $C_k = \frac{1}{k+1} \binom{2k}{k}$.
17: 
18: For a fixed $k$, the number of ways to arrange these moves in a sequence of $2n$ steps is:
19: - Choose $2k$ positions for the $(R, U)$ and $(U, R)$ moves: $\binom{2n}{2k}$
20: - Arrange these $2k$ moves as a Dyck path: $C_k$
21: - Arrange the remaining $2n-2k$ positions with $n-k$ $(R, R)$ and $n-k$ $(U, U)$ moves: $\binom{2n-2k}{n-k}$
22: 
23: Summing over all possible values of $k$:
24: $$f(n) = \sum_{k=0}^n \binom{2n}{2k} C_k \binom{2n-2k}{n-k} = \sum_{k=0}^n \frac{(2n)!}{(2k)!(2n-2k)!} \frac{(2k)!}{(k+1)!k!} \frac{(2n-2k)!}{(n-k)!(n-k)!}$$
25: $$f(n) = \sum_{k=0}^n \frac{(2n)!}{(k+1)!k!(n-k)!(n-k)!} = \binom{2n}{n} \sum_{k=0}^n \frac{1}{k+1} \binom{n}{k}^2$$
26: To evaluate the sum $\sum_{k=0}^n \frac{1}{k+1} \binom{n}{k}^2$, we use the identity $\frac{1}{k+1} \binom{n}{k} = \frac{1}{n+1} \binom{n+1}{k+1}$:
27: $$\sum_{k=0}^n \frac{1}{k+1} \binom{n}{k}^2 = \frac{1}{n+1} \sum_{k=0}^n \binom{n+1}{k+1} \binom{n}{n-k}$$
28: By Vandermonde's Identity, $\sum_{j=0}^{n+1} \binom{n+1}{j} \binom{n}{n+1-j} = \binom{2n+1}{n+1}$. Since the $j=0$ term is $\binom{n+1}{0}\binom{n}{n+1} = 0$, the sum from $j=1$ to $n+1$ (where $j=k+1$) is exactly $\binom{2n+1}{n+1}$. Thus:
29: $$\sum_{k=0}^n \frac{1}{k+1} \binom{n}{k}^2 = \frac{1}{n+1} \binom{2n+1}{n+1}$$
30: Substituting this back into the expression for $f(n)$:
31: $$f(n) = \binom{2n}{n} \frac{1}{n+1} \binom{2n+1}{n+1} = \binom{2n}{n} \frac{1}{n+1} \frac{2n+1}{n+1} \binom{2n}{n} = \frac{2n+1}{(n+1)^2} \binom{2n}{n}^2$$
32: Recognizing $C_n = \frac{1}{n+1} \binom{2n}{n}$, we obtain the simplified formula:
33: $$f(n) = (2n+1) C_n^2$$
34: For $n=10$:
35: $$C_{10} = \frac{1}{11} \binom{20}{10} = \frac{184756}{11} = 16796$$
36: $$f(10) = (2 \cdot 10 + 1) \cdot 16796^2 = 21 \cdot 282105616 = 5924217936$$
37: 
38: The number of pairs of paths is $5924217936$.
