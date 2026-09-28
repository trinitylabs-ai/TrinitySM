To find $f(n)$, the number of pairs of paths $(P_1, P_2)$ from $(0, 0)$ to $(n, n)$ such that the $y$-coordinate of $P_1$ never exceeds the $y$-coordinate of $P_2$ at any time step $t \in \{0, 1, \dots, 2n\}$, we first analyze the condition $y_1(t) \le y_2(t)$.

Since each path consists of $2n$ steps (Right or Up), at any time $t$, the position $(x, y)$ satisfies $x+y=t$. Thus, $y_1(t) \le y_2(t)$ is equivalent to $x_1(t) \ge x_2(t)$. Geometrically, this means path $P_1$ always stays "below" or "to the right" of path $P_2$.
Paths from $(0,0)$ to $(n,n)$ are in one-to-one correspondence with partitions $\lambda$ that fit inside an $n \times n$ box. Specifically, if $P$ is a path, the region between the path and the $x$-axis (within the box) defines a partition $\lambda = (\lambda_1, \lambda_2, \dots, \lambda_n)$ where $n \ge \lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_n \ge 0$. The condition $y_1(t) \le y_2(t)$ for all $t$ is exactly the condition that the partition $\lambda_1$ corresponding to $P_1$ is contained within the partition $\lambda_2$ corresponding to $P_2$ (i.e., $\lambda_1 \subseteq \lambda_2$).

Thus, $f(n)$ is the number of pairs of partitions $(\lambda_1, \lambda_2)$ such that $\lambda_1 \subseteq \lambda_2 \subseteq (n^n)$, where $(n^n)$ denotes the $n \times n$ square. This is equivalent to counting plane partitions with shape $(n, n)$ (two rows of length $n$) and entries bounded by $n$. The general formula for the number of plane partitions $N(r, c, M)$ fitting in a box of dimensions $r \times c \times M$ is given by MacMahon's formula:
\[ N(r, c, M) = \prod_{i=1}^r \prod_{j=1}^c \frac{M+i+j-1}{i+j-1} \]
For $r=2, c=n, M=n$, we have:
\[ f(n) = \prod_{j=1}^n \frac{n+1+j-1}{1+j-1} \cdot \prod_{j=1}^n \frac{n+2+j-1}{2+j-1} = \prod_{j=1}^n \frac{n+j}{j} \cdot \prod_{j=1}^n \frac{n+j+1}{j+1} \]
The first product is the central binomial coefficient $\binom{2n}{n}$. The second product is:
\[ \prod_{j=1}^n \frac{n+j+1}{j+1} = \frac{(n+2)(n+3)\dots(2n+1)}{2 \cdot 3 \dots (n+1)} = \frac{(2n+1)!}{(n+1)! (n+1)!} = \frac{1}{n+1} \binom{2n+1}{n} \]
Therefore, $f(n) = \binom{2n}{n} \cdot \frac{1}{n+1} \binom{2n+1}{n}$. For $n=10$:
\[ f(10) = \binom{20}{10} \cdot \frac{1}{11} \binom{21}{10} \]
We calculate $\binom{20}{10}$:
\[ \binom{20}{10} = \frac{20 \cdot 19 \cdot 18 \cdot 17 \cdot 16 \cdot 15 \cdot 14 \cdot 13 \cdot 12 \cdot 11}{10 \cdot 9 \cdot 8 \cdot 7 \cdot 6 \cdot 5 \cdot 4 \cdot 3 \cdot 2 \cdot 1} = 184756 \]
Then $\binom{21}{10} = \frac{21}{11} \binom{20}{10} = \frac{21}{11} \cdot 184756 = 21 \cdot 16796 = 352716$.
Finally:
\[ f(10) = 184756 \cdot \frac{1}{11} \cdot 352716 = 16796 \cdot 352716 = 5924217936 \]

\(\square\)
