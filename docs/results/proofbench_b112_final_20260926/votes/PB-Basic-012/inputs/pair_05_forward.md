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
