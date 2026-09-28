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
