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

1: To find the number of pairs of paths $f(n)$ on an $n \times n$ grid such that both paths start at $(0,0)$ and end at $(n,n)$, using only right (R) and up (U) movements, and the $y$-coordinate of the first path $P_1$ never exceeds the $y$-coordinate of the second path $P_2$ at any timestep $t$, we can use the Lindström-Gessel-Viennot (LGV) Lemma.
2: 
3: ### 1. Application of the LGV Lemma
4: Let $P_1 = (x_{1,t}, y_{1,t})$ and $P_2 = (x_{2,t}, y_{2,t})$ for $t = 0, 1, \dots, 2n$. The condition is $y_{1,t} \le y_{2,t}$ for all $t$. Since $x_{i,t} + y_{i,t} = t$, this is equivalent to $x_{1,t} \ge x_{2,t}$ for all $t$.
5: To transform this into a problem of non-intersecting paths, we shift the start and end points of the paths. Define:
6: - $A_1 = (1, 0), B_1 = (n+1, n)$
7: - $A_2 = (0, 1), B_2 = (n, n+1)$
8: 
9: We establish a correspondence between the pair of paths $(P_1, P_2)$ and a pair of paths $(P_1', P_2')$ where $P_1': A_1 \to B_1$ and $P_2': A_2 \to B_2$. Define $P_1'$ as the path $P_1$ shifted by $(1, 0)$, so its coordinates at time $t$ are $(x_{1,t}+1, y_{1,t})$. Define $P_2'$ as the path $P_2$ shifted by $(0, 1)$, so its coordinates at time $t$ are $(x_{2,t}, y_{2,t}+1)$.
10: At any timestep $t \in \{0, \dots, 2n\}$, the sum of coordinates for $P_1'$ is $(x_{1,t}+1) + y_{1,t} = t+1$, and the sum of coordinates for $P_2'$ is $x_{2,t} + (y_{2,t}+1) = t+1$. Thus, $P_1'$ and $P_2'$ can only intersect at the same timestep $t$.
11: An intersection occurs if and only if $(x_{1,t}+1, y_{1,t}) = (x_{2,t}, y_{2,t}+1)$, which implies $y_{1,t} = y_{2,t}+1$. Since $y_{1,0} = y_{2,0} = 0$ and the coordinates change by at most 1 each step, the condition $y_{1,t} > y_{2,t}$ for some $t$ is equivalent to the existence of some $t$ such that $y_{1,t} = y_{2,t}+1$. Therefore, $P_1'$ and $P_2'$ are non-intersecting if and only if $y_{1,t} \le y_{2,t}$ for all $t$.
12: 
13: According to the LGV Lemma, the number of such non-intersecting pairs is given by the determinant:
14: \[ f(n) = \det \begin{pmatrix} N(A_1, B_1) & N(A_1, B_2) \\ N(A_2, B_1) & N(A_2, B_2) \end{pmatrix} \]
15: provided that the only permutation $\sigma$ of $\{1, 2\}$ allowing non-intersecting paths $P_i': A_i \to B_{\sigma(i)}$ is the identity. If $\sigma$ is the transposition $(1, 2)$, then $P_1': A_1 \to B_2$ and $P_2': A_2 \to B_1$. Let $x_{1,t}'$ and $x_{2,t}'$ be the x-coordinates of these paths at time $t$. Then $x_{1,0}' - x_{2,0}' = 1 - 0 = 1$ and $x_{1,2n+1}' - x_{2,2n+1}' = n - (n+1) = -1$. Since the x-coordinates change by at most 1 each step, there must be some $t$ where $x_{1,t}' = x_{2,t}'$. Since $x_{i,t}' + y_{i,t}' = t+1$ for both paths, this implies $y_{1,t}' = y_{2,t}'$, so the paths must intersect. Thus, only the identity permutation contributes.
16: 
17: The path counts are:
18: - $N(A_1, B_1) = \binom{(n+1-1) + (n-0)}{n} = \binom{2n}{n}$
19: - $N(A_2, B_2) = \binom{(n-0) + (n+1-1)}{n} = \binom{2n}{n}$
20: - $N(A_1, B_2) = \binom{(n-1) + (n+1-0)}{n-1} = \binom{2n}{n-1}$
21: - $N(A_2, B_1) = \binom{(n+1-0) + (n-1)}{n+1} = \binom{2n}{n+1}$
22: 
23: Since $\binom{2n}{n-1} = \binom{2n}{n+1}$, the formula for $f(n)$ is:
24: \[ f(n) = \binom{2n}{n}^2 - \binom{2n}{n-1}^2 \]
25: 
26: ### 2. Calculation for $n=10$
27: For $n=10$, we have:
28: \[ f(10) = \binom{20}{10}^2 - \binom{20}{9}^2 \]
29: First, calculate the binomial coefficients:
30: \[ \binom{20}{10} = \frac{20 \cdot 19 \cdot 18 \cdot 17 \cdot 16 \cdot 15 \cdot 14 \cdot 13 \cdot 12 \cdot 11}{10 \cdot 9 \cdot 8 \cdot 7 \cdot 6 \cdot 5 \cdot 4 \cdot 3 \cdot 2 \cdot 1} = 184,756 \]
31: \[ \binom{20}{9} = \frac{10}{11} \binom{20}{10} = \frac{1,847,560}{11} = 167,960 \]
32: 
33: Now, use the difference of squares $a^2 - b^2 = (a-b)(a+b)$:
34: \[ a-b = 184,756 - 167,960 = 16,796 \]
35: \[ a+b = 184,756 + 167,960 = 352,716 \]
36: \[ f(10) = 16,796 \times 352,716 \]
37: 
38: Performing the multiplication:
39: \[ 16,796 \times 300,000 = 5,038,800,000 \]
40: \[ 16,796 \times 50,000 = 839,800,000 \]
41: \[ 16,796 \times 2,000 = 33,592,000 \]
42: \[ 16,796 \times 700 = 11,757,200 \]
43: \[ 16,796 \times 10 = 167,960 \]
44: \[ 16,796 \times 6 = 100,776 \]
45: Summing these:
46: \[ 5,038,800,000 + 839,800,000 + 33,592,000 + 11,757,200 + 167,960 + 100,776 = 5,924,217,936 \]
47: 
48: Thus, $f(10) = 5,924,217,936$.

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
