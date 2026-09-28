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

1: To find the number of pairs of paths $f(n)$ on an $n \times n$ grid from $(0,0)$ to $(n,n)$ such that the $y$-coordinate of the first path $P_1$ never exceeds the $y$-coordinate of the second path $P_2$ at any timestep, we analyze the condition $y_1(t) \le y_2(t)$.
2: 
3: ### 1. Theoretical Derivation
4: Let $P_1$ and $P_2$ be paths consisting of $n$ Right (R) and $n$ Up (U) steps. At any timestep $t \in \{0, 1, \dots, 2n\}$, let $(x_1(t), y_1(t))$ and $(x_2(t), y_2(t))$ be the coordinates of the first and second paths, respectively. The condition $y_1(t) \le y_2(t)$ implies that at any step $t$, the number of Up steps taken by $P_1$ is less than or equal to the number of Up steps taken by $P_2$.
5: 
6: We can solve this using the Lindström-Gessel-Viennot (LGV) Lemma. To do so, we transform the problem into one involving non-intersecting paths. We shift the second path $P_2$ to a new path $P'_2$ by redefining its start and end points. Let $P_1$ start at $A_1 = (0,0)$ and end at $B_1 = (n,n)$. Let $P'_2$ start at $A_2 = (-1, 1)$ and end at $B_2 = (n-1, n+1)$. Any path $P'_2$ is a shift of a path $P_2$ from $(0,0)$ to $(n,n)$ by the vector $(-1, 1)$, so $P'_2(t) = (x_2(t)-1, y_2(t)+1)$.
7: 
8: Two paths $P_1$ and $P'_2$ intersect if there exists a $t$ such that $(x_1(t), y_1(t)) = (x'_2(t), y'_2(t))$. This occurs if and only if $x_1(t) = x_2(t)-1$ and $y_1(t) = y_2(t)+1$. Since $x_i(t) + y_i(t) = t$ for both paths, these two conditions are equivalent. Let $d(t) = y_1(t) - y_2(t)$. We have $d(0) = 0$, and since each path moves only Right or Up, $|d(t+1) - d(t)| \le 1$. The condition $y_1(t) \le y_2(t)$ for all $t$ is violated if and only if $d(t)$ becomes positive, which, given $d(0)=0$ and the step constraint, happens if and only if $d(t) = 1$ for some $t$. Thus, the number of valid pairs $(P_1, P_2)$ is equal to the number of non-intersecting paths from $\{A_1, A_2\}$ to $\{B_1, B_2\}$.
9: 
10: By the LGV Lemma, the number of non-intersecting paths is given by the determinant of the matrix of path counts, provided that the only permutation $\sigma$ of $\{1, 2\}$ that allows non-intersecting paths $A_i \to B_{\sigma(i)}$ is the identity. For $\sigma = (2,1)$, any path $P_1$ from $A_1(0,0)$ to $B_2(n-1, n+1)$ and any path $P_2$ from $A_2(-1,1)$ to $B_1(n,n)$ must intersect. This is because the difference in $y$-coordinates $d(t) = y_1(t) - y_2(t)$ starts at $d(0) = 0 - 1 = -1$ and ends at $d(2n) = (n+1) - n = 1$. Since $|d(t+1) - d(t)| \le 1$ for all $t$, there must exist some $t$ such that $d(t) = 0$, implying $y_1(t) = y_2(t)$. Since $x_i(t) = t - y_i(t)$, this implies $x_1(t) = x_2(t)$, so $P_1(t) = P_2(t)$.
11: 
12: Thus, the number of valid pairs is:
13: $$f(n) = \det \begin{pmatrix} e(A_1, B_1) & e(A_1, B_2) \\ e(A_2, B_1) & e(A_2, B_2) \end{pmatrix}$$
14: where $e(A, B)$ is the number of paths from $A$ to $B$:
15: - $e(A_1, B_1) = \binom{n+n}{n} = \binom{2n}{n}$
16: - $e(A_1, B_2) = \binom{(n-1-0)+(n+1-0)}{n-1} = \binom{2n}{n-1}$
17: - $e(A_2, B_1) = \binom{(n-(-1))+(n-1)}{n+1} = \binom{2n}{n+1}$
18: - $e(A_2, B_2) = \binom{(n-1-(-1))+(n+1-1)}{n} = \binom{2n}{n}$
19: 
20: Using the identity $\binom{2n}{n-1} = \binom{2n}{n+1}$, the formula simplifies to:
21: $$f(n) = \binom{2n}{n}^2 - \binom{2n}{n-1}^2$$
22: 
23: ### 2. Calculation for $n=10$
24: We calculate $f(10) = \binom{20}{10}^2 - \binom{20}{9}^2$.
25: First, compute the binomial coefficients:
26: $$\binom{20}{10} = 184,756$$
27: $$\binom{20}{9} = \binom{20}{10} \cdot \frac{10}{11} = \frac{1,847,560}{11} = 167,960$$
28: 
29: Using the difference of squares $a^2 - b^2 = (a-b)(a+b)$:
30: $$f(10) = (184,756 - 167,960)(184,756 + 167,960)$$
31: $$f(10) = 16,796 \cdot 352,716$$
32: 
33: Performing the multiplication:
34: $$16,796 \times 350,000 = 5,878,600,000$$
35: $$16,796 \times 2,000 = 33,592,000$$
36: $$16,796 \times 700 = 11,757,200$$
37: $$16,796 \times 10 = 167,960$$
38: $$16,796 \times 6 = 100,776$$
39: 
40: Summing these results:
41: $$5,878,600,000 + 33,592,000 + 11,757,200 + 167,960 + 100,776 = 5,924,217,936$$
42: 
43: The number of such pairs of paths is $5,924,217,936$.

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
