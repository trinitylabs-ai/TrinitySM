To find $f(n)$, the number of pairs of paths $P_1$ and $P_2$ on an $n \times n$ grid from $(0,0)$ to $(n,n)$ such that the $y$-coordinate of $P_1$ never exceeds the $y$-coordinate of $P_2$ at any timestep $t$, we begin by analyzing the constraints.

Let the paths be defined by the coordinates $(x_{i,t}, y_{i,t})$ for $t = 0, 1, \dots, 2n$. The condition is $y_{1,t} \le y_{2,t}$ for all $t$. Since $x_{i,t} + y_{i,t} = t$ for any path from $(0,0)$ to $(n,n)$ using only right (R) and up (U) moves, the condition $y_{1,t} \le y_{2,t}$ is equivalent to $t - x_{1,t} \le t - x_{2,t}$, which simplifies to $x_{1,t} \ge x_{2,t}$.

This is a problem of counting non-crossing paths. We can use the Lindström-Gessel-Viennot (LGV) Lemma by transforming these non-crossing paths (which are allowed to touch) into strictly non-intersecting paths. We shift the start and end points of the paths as follows:
- Let path $P_1^*$ be the path $P_1$ shifted by $(1, 0)$, starting at $A_1 = (1, 0)$ and ending at $B_1 = (n+1, n)$.
- Let path $P_2^*$ be the path $P_2$ shifted by $(0, 1)$, starting at $A_2 = (0, 1)$ and ending at $B_2 = (n, n+1)$.

We claim that $P_1$ and $P_2$ satisfy $y_{1,t} \le y_{2,t}$ for all $t$ if and only if $P_1^*$ and $P_2^*$ are strictly disjoint.
Suppose $P_1^*$ and $P_2^*$ intersect. Then there exist $t_1, t_2$ such that $(x_{1,t_1}+1, y_{1,t_1}) = (x_{2,t_2}, y_{2,t_2}+1)$. This implies $x_{1,t_1}+1 = x_{2,t_2}$ and $y_{1,t_1} = y_{2,t_2}+1$. Summing these gives $(x_{1,t_1} + y_{1,t_1}) + 1 = (x_{2,t_2} + y_{2,t_2}) + 1$, so $t_1 = t_2 = t$. Then $y_{1,t} = y_{2,t}+1$, which means $y_{1,t} > y_{2,t}$.
Conversely, if $y_{1,t} > y_{2,t}$ for some $t$, since $y_{1,0} = y_{2,0} = 0$, there must be a first $t$ where $y_{1,t} = y_{2,t}+1$. At this $t$, $x_{1,t} = t - y_{1,t} = t - (y_{2,t}+1) = x_{2,t}-1$, so $(x_{1,t}+1, y_{1,t}) = (x_{2,t}, y_{2,t}+1)$, meaning the shifted paths intersect.

According to the LGV Lemma, the number of such disjoint pairs is given by the determinant:
\[ f(n) = \det \begin{pmatrix} N(A_1, B_1) & N(A_1, B_2) \\ N(A_2, B_1) & N(A_2, B_2) \end{pmatrix} \]
where $N(A, B)$ denotes the number of paths from $A$ to $B$. Note that any path from $A_1$ to $B_2$ and any path from $A_2$ to $B_1$ must intersect because $A_1$ is to the right of $A_2$ and $B_2$ is to the left of $B_1$, so the only non-intersecting pairs are those where $P_1^*$ goes from $A_1$ to $B_1$ and $P_2^*$ goes from $A_2$ to $B_2$. We calculate these values:
- $N(A_1, B_1) = \binom{(n+1-1) + (n-0)}{n} = \binom{2n}{n}$
- $N(A_1, B_2) = \binom{(n-1) + (n+1-0)}{n+1} = \binom{2n}{n+1} = \binom{2n}{n-1}$
- $N(A_2, B_1) = \binom{(n+1-0) + (n-1)}{n-1} = \binom{2n}{n-1}$
- $N(A_2, B_2) = \binom{(n-0) + (n+1-1)}{n} = \binom{2n}{n}$

Thus, the formula for $f(n)$ is:
\[ f(n) = \binom{2n}{n}^2 - \binom{2n}{n-1}^2 = \left( \binom{2n}{n} - \binom{2n}{n-1} \right) \left( \binom{2n}{n} + \binom{2n}{n-1} \right) \]
The first term is the $n$-th Catalan number $C_n = \frac{1}{n+1}\binom{2n}{n}$, and the second term is $\binom{2n+1}{n}$ by Pascal's Identity. For $n=10$:
\[ \binom{20}{10} = \frac{20!}{10!10!} = 184,756 \]
\[ \binom{20}{9} = \binom{20}{10} \times \frac{10}{11} = 184,756 \times \frac{10}{11} = 16,796 \times 10 = 167,960 \]
Now we compute the factors for $f(10)$:
- $C_{10} = 184,756 - 167,960 = 16,796$
- $\binom{21}{10} = 184,756 + 167,960 = 352,716$

The final result is the product:
\[ f(10) = 16,796 \times 352,716 \]
Performing the multiplication:
\[ 16,796 \times 352,716 = (16,800 - 4) \times 352,716 = 16,800 \times 352,716 - 4 \times 352,716 \]
\[ 16,800 \times 352,716 = 168 \times 35,271,600 = (100 + 60 + 8) \times 35,271,600 = 3,527,160,000 + 2,116,296,000 + 282,172,800 = 5,925,628,800 \]
\[ 4 \times 352,716 = 1,410,864 \]
\[ f(10) = 5,925,628,800 - 1,410,864 = 5,924,217,936 \]
