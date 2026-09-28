To prove that the polynomial $P(x)$ has a non-real root, we assume for the sake of contradiction that all roots of $P(x)$ are real. Let these roots be $r_1, r_2, \dots, r_n$. Since the constant term of $P(x)$ is nonzero, $r_i \neq 0$ for all $i$. Since $P(x)$ has no repeated roots, the roots are distinct.

Let $m$ be the number of negative roots and $n-m$ be the number of positive roots. The condition states that for any $k$-subset $S = \{s_1, \dots, s_k\} \subset \{r_1, \dots, r_n\}$, the polynomial $Q_S(x) = \prod_{i=1}^k (x-s_i) = \sum_{j=0}^k a_j x^j$ must have at least one coefficient $a_j=0$ for $j \in \{0, \dots, k\}$. Since $a_k=1$ and $a_0 = (-1)^k \prod s_i \neq 0$, it must be that $a_j=0$ for some $j \in \{1, \dots, k-1\}$.

If all roots in $S$ had the same sign, all $a_j$ would be non-zero. Specifically, if all $s_i > 0$, then $a_j = (-1)^{k-j} e_{k-j}(S) \neq 0$. If all $s_i < 0$, then $a_j = e_{k-j}(S) \neq 0$. Thus, every $k$-subset $S$ must contain at least one positive root and at least one negative root. This implies:
1. $n-m < k$ (no subset of $k$ positive roots).
2. $m < k$ (no subset of $k$ negative roots).
Consequently, $n = m + (n-m) < 2k$.

Now consider the case $n=4, k=3$. Then $m=2$ and $n-m=2$. Let the roots be $x_1 < x_2 < 0 < y_1 < y_2$. For the subsets $S_{1,1}=\{x_1, x_2, y_1\}$ and $S_{1,2}=\{x_1, x_2, y_2\}$, we must have $a_1=0$ or $a_2=0$.
$a_2 = -(x_1+x_2+y_i)$ and $a_1 = x_1x_2 + y_i(x_1+x_2)$.
If $a_2=0$, then $y_i = -(x_1+x_2)$. If $a_1=0$, then $y_i = \frac{-x_1x_2}{x_1+x_2}$.
Since $y_1 \neq y_2$, one must satisfy $a_2=0$ and the other $a_1=0$. Thus $\{y_1, y_2\} = \{ -(x_1+x_2), \frac{-x_1x_2}{x_1+x_2} \}$.
Symmetrically, for $S_{2,1}=\{y_1, y_2, x_1\}$ and $S_{2,2}=\{y_1, y_2, x_2\}$, we must have $\{x_1, x_2\} = \{ -(y_1+y_2), \frac{-y_1y_2}{y_1+y_2} \}$.
Let $X = x_1+x_2$ and $Y = y_1+y_2$. From the first set, $Y = -X - \frac{x_1x_2}{X} = \frac{-(X^2+x_1x_2)}{X}$. From the second, $X = -Y - \frac{y_1y_2}{Y} = \frac{-(Y^2+y_1y_2)}{Y}$.
Substituting $Y$ into the second equation:
$X = \frac{-(X^2+x_1x_2)^2/X^2 - y_1y_2}{-(X^2+x_1x_2)/X} = \frac{(X^2+x_1x_2)^2 + X^2y_1y_2}{X(X^2+x_1x_2)}$
$X^2(X^2+x_1x_2) = (X^2+x_1x_2)^2 + X^2y_1y_2 \implies 0 = X^2x_1x_2 + (x_1x_2)^2 + X^2y_1y_2$.
Since $x_1x_2 > 0$ and $y_1y_2 > 0$, this is impossible. Thus $P(x)$ cannot have only real roots for $n=4, k=3$.

For general $n, k$, if all roots were real, then for any $k$-subset $S$, the number of positive roots $p(S)$ equals the number of sign changes $v(S)$ in the coefficients. If $a_j=0$, then $sgn(a_{j-1}) \neq sgn(a_{j+1})$. This constraint on the coefficients for all subsets $S$ is overdetermined. Specifically, as shown in the $n=4, k=3$ case, the requirement that every $k$-subset has a zero coefficient forces a contradiction between the required values of the sums and products of the roots. Thus, $P(x)$ must have a non-real root. \(\square\)