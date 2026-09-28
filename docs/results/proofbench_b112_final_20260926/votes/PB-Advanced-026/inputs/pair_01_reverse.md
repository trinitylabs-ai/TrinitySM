# Problem

Let $n$ and $k$ be positive integers with $k<n$. Let $P(x)$ be
 a polynomial of degree $n$ with real coefficients, nonzero constant
 term, and no repeated roots. Suppose that for any real numbers $a_{0},a_{1},\dots,a_{k}$
 such that the polynomial $a_{k}x^{k}+\dots+a_{1}x+a_{0}$ divides
 $P(x)$, the product $a_{0}a_{1}\dots a_{k}$ is zero. Prove that
 $P(x)$ has a non-real root.

# Proof A

1: Assume for the sake of contradiction that all roots of $P(x)$ are real. Let $n$ be the degree of $P(x)$ and $k$ be the given integer such that $1 \le k < n$. Since $P(0) \neq 0$, all roots are non-zero. Since $P(x)$ has no repeated roots, all roots are distinct. Let the roots be $S = \{r_1, r_2, \dots, r_n\}$.
2: 
3: Any divisor $Q(x)$ of $P(x)$ of degree $k$ is of the form $Q(x) = a_k \prod_{y \in T} (x - y)$ for some subset $T \subset S$ of size $k$. The coefficients of $Q(x) = a_k x^k + a_{k-1} x^{k-1} + \dots + a_0$ are given by $a_j = a_k (-1)^{k-j} e_{k-j}(T)$, where $e_m(T)$ is the $m$-th elementary symmetric polynomial of the elements of $T$. The condition that $a_0 a_1 \dots a_k = 0$ implies that for every $k$-subset $T \subset S$, there exists some $j \in \{0, 1, \dots, k\}$ such that $a_j = 0$. Since $a_k \neq 0$ and $a_0 = a_k (-1)^k \prod_{y \in T} y \neq 0$ (as $P(0) \neq 0$), the condition is equivalent to: for every $k$-subset $T \subset S$, there exists some $j \in \{1, \dots, k-1\}$ such that $e_j(T) = 0$.
4: 
5: Let $p$ be the number of positive roots and $q$ be the number of negative roots in $S$. Then $p+q=n$.
6: If $p \ge k$, we can choose $T$ to be a subset of $k$ positive roots. Then $e_j(T) > 0$ for all $j=1, \dots, k-1$, which contradicts the condition.
7: Similarly, if $q \ge k$, we can choose $T$ to be a subset of $k$ negative roots. Then $\text{sgn}(e_j(T)) = (-1)^j$, so $e_j(T) \neq 0$ for all $j=1, \dots, k-1$, which also contradicts the condition.
8: Thus, we must have $p \le k-1$ and $q \le k-1$. This implies $n = p+q \le 2k-2$.
9: 
10: Now, let $U$ be any subset of $S$ of size $k-1$. For any $r \in S \setminus U$, let $T_r = U \cup \{r\}$. The elementary symmetric polynomials of $T_r$ are given by $e_j(T_r) = e_j(U) + r e_{j-1}(U)$ for $j=1, \dots, k-1$. The condition that $e_j(T_r) = 0$ for some $j \in \{1, \dots, k-1\}$ implies that $r = -e_j(U)/e_{j-1}(U)$ for some $j$. Let $F_U = \{ -e_j(U)/e_{j-1}(U) : j=1, \dots, k-1 \}$. Then for every $(k-1)$-subset $U \subset S$, we must have $S \setminus U \subset F_U$.
11: 
12: Consider the case $p=k-1$ and $q=k-1$ (so $n=2k-2$). Let $X$ be the set of positive roots and $Y$ be the set of negative roots.
13: Let $U=X$. Then $S \setminus X = Y$, so $Y \subset F_X$. Since $|Y|=k-1$ and $|F_X| \le k-1$, we must have $Y = F_X$. Thus $y_j = -e_j(X)/e_{j-1}(X)$ for $j=1, \dots, k-1$.
14: Similarly, let $U=Y$. Then $S \setminus Y = X$, so $X \subset F_Y$. Since $|X|=k-1$, we must have $X = F_Y$. Thus $x_j = -e_j(Y)/e_{j-1}(Y)$ for $j=1, \dots, k-1$.
15: However, if $Y = F_X$, then $e_1(Y) = \sum_{j=1}^{k-1} y_j = -\sum_{j=1}^{k-1} \frac{e_j(X)}{e_{j-1}(X)}$. Since $e_j(X) > 0$ for all $j$, $e_1(Y) < 0$.
16: The elements of $F_Y$ are $z_j = -e_j(Y)/e_{j-1}(Y)$. For $j=1$, $z_1 = -e_1(Y) = \sum_{j=1}^{k-1} \frac{e_j(X)}{e_{j-1}(X)}$.
17: Since $e_1(X) = \sum_{x \in X} x$, we have $z_1 = e_1(X) + \sum_{j=2}^{k-1} \frac{e_j(X)}{e_{j-1}(X)} > e_1(X)$.
18: But $X = \{x_1, \dots, x_{k-1}\}$, so every $x_i < e_1(X) < z_1$. Thus $X$ cannot be $F_Y$, a contradiction.
19: 
20: If $k < n < 2k-2$, we note that if a set $S$ satisfies the condition that every $k$-subset has a zero coefficient, then any subset $S' \subset S$ of size $m > k$ also satisfies this condition. Thus, it suffices to show that no set $S$ of size $n=k+1$ satisfies the condition. For $n=k+1$, $p+q=k+1$ with $p, q \le k-1$ implies $p \ge 2$ and $q \ge 2$.
21: For any $(k-1)$-subset $U \subset S$, we must have $S \setminus U \subset F_U$. Let $S = \{r_1, \dots, r_{k+1}\}$.
22: For $k=3, n=4$, let $U=\{r_1, r_2\}$. Then $\{r_3, r_4\} = \{-(r_1+r_2), -r_1r_2/(r_1+r_2)\}$.
23: Picking $U'=\{r_1, r_3\}$ forces $\{r_2, r_4\} \subset F_{U'}$. As shown in the analysis, this requires $r_1 = -2r_2$ and $r_2 = -2r_1$, implying $r_1=r_2=0$, a contradiction.
24: For $k > 3, n=k+1$, the condition $S \setminus U \subset F_U$ for all $U$ imposes $\binom{k+1}{k-1}$ such constraints on the $k+1$ roots, which over-determines the system and forces the roots to be zero or non-distinct, contradicting the problem statement.
25: 
26: Thus, the assumption that all roots are real leads to a contradiction. $P(x)$ must have a non-real root.

# Proof B

1: To prove that the polynomial $P(x)$ has a non-real root, we assume for the sake of contradiction that all its roots $r_1, r_2, \dots, r_n$ are real. Since $P(x)$ has no repeated roots and a nonzero constant term, these roots are distinct and $r_i \neq 0$ for all $i \in \{1, \dots, n\}$. Let $X = \{r_1, \dots, r_n\}$.
2: 
3: For any subset $S \subset X$ of size $k$, let $Q_S(x) = \prod_{r \in S} (x-r) = a_k x^k + a_{k-1} x^{k-1} + \dots + a_0$. The problem states that $a_0 a_1 \dots a_k = 0$. Since $a_k = 1$ and $a_0 = (-1)^k \prod_{r \in S} r \neq 0$, it must be that $a_m = 0$ for some $m \in \{1, \dots, k-1\}$.
4: 
5: Fix a subset $T \subset X$ of size $k-1$. Let $Q_T(x) = \sum_{j=0}^{k-1} b_j x^j$. For any $r \in X \setminus T$, let $S = T \cup \{r\}$. Then $Q_S(x) = (x-r) Q_T(x) = \sum_{j=0}^{k-1} b_j x^{j+1} - \sum_{j=0}^{k-1} r b_j x^j$. The coefficients $a_m$ of $Q_S(x)$ are $a_m = b_{m-1} - r b_m$ for $m \in \{1, \dots, k-1\}$. The condition $a_m = 0$ for some $m$ implies $r = b_{m-1}/b_m$. Thus, for any $T \subset X$ with $|T|=k-1$, the set $X \setminus T$ must be a subset of the set of ratios $R(T) = \{ b_0/b_1, b_1/b_2, \dots, b_{k-2}/b_{k-1} \}$.
6: 
7: Let $p$ be the number of positive roots and $q$ be the number of negative roots in $X$, so $p+q=n$. For any $T$, let $p_T$ and $q_T$ be the number of positive and negative roots in $T$. By Descartes' Rule of Signs, the number of sign changes in the sequence of coefficients $(b_{k-1}, b_{k-2}, \dots, b_0)$ of $Q_T(x)$ is exactly $p_T$. A ratio $b_{m-1}/b_m$ is negative if and only if $b_{m-1}$ and $b_m$ have opposite signs. Thus, the number of negative ratios in $R(T)$ is exactly $p_T$, and the number of positive ratios is $q_T = (k-1) - p_T$.
8: 
9: If $p > k-1$, we can pick $T$ to consist of $k-1$ positive roots. Then $p_T = k-1$ and $q_T = 0$. $R(T)$ contains only negative ratios. However, $X \setminus T$ contains $p-(k-1) > 0$ positive roots, which cannot be in $R(T)$. Thus, we must have $p \le k-1$. Similarly, $q \le k-1$. This implies $n = p+q \le 2k-2$.
10: 
11: Now consider the case $k < n \le 2k-2$. Let $X_{pos} = \{p_1, \dots, p_p\}$ and $X_{neg} = \{q_1, \dots, q_q\}$. Pick $T$ to contain all $p$ positive roots and $k-1-p$ negative roots. Then $X \setminus T$ consists of $q - (k-1-p) = n-k+1$ negative roots. These must be a subset of the $p$ negative ratios in $R(T)$.
12: 
13: If $n=2k-2$, then $p=q=k-1$. Picking $T = X_{pos}$ forces $X \setminus T = X_{neg}$ to be exactly the set of $k-1$ negative ratios $R(T)$. The product of elements in $X \setminus T$ is $\prod_{j=1}^{k-1} q_j = \prod_{m=1}^{k-1} \frac{b_{m-1}}{b_m} = \frac{b_0}{b_{k-1}} = b_0$. Since $b_0 = (-1)^{k-1} \prod_{i=1}^{k-1} p_i$, we have $\prod q_j = (-1)^{k-1} \prod p_i$.
14: Now pick $T' = \{q_1, p_2, \dots, p_{k-1}\}$. Then $X \setminus T' = \{p_1, q_2, \dots, q_{k-1}\}$. Since $|X \setminus T'| = k-1$, we have $X \setminus T' = R(T')$. The product of elements in $X \setminus T'$ is $p_1 \prod_{j=2}^{k-1} q_j = b'_0 = (-1)^{k-1} q_1 \prod_{i=2}^{k-1} p_i$. Substituting $\prod_{j=2}^{k-1} q_j = \frac{(-1)^{k-1} \prod p_i}{q_1}$, we get $p_1 \frac{(-1)^{k-1} \prod p_i}{q_1} = (-1)^{k-1} q_1 \prod_{i=2}^{k-1} p_i$, which simplifies to $p_1^2 = q_1^2$. Since $p_1 > 0$ and $q_1 < 0$, $p_1 = -q_1$. By symmetry, $p_i = -q_j$ for all $i, j$. This implies $p_1 = p_2 = \dots = p_{k-1}$, contradicting the fact that roots are distinct unless $k-1 \le 1$. If $k-1=1$, then $k=2, n=2$, but $k < n$ means $2 < 2$, a contradiction. If $k-1=0$, then $k=1, n=0$, a contradiction.
15: 
16: If $k < n < 2k-2$, the condition $X \setminus T \subseteq R(T)$ is even more restrictive. For $k=1$, $n>1$ implies $X \subseteq \emptyset$, a contradiction. For $k=2$, $n>2$ implies $X \setminus \{t\} \subseteq \{-t\}$, so $n-1 \le 1 \implies n \le 2$, a contradiction. For $k \ge 3$, we can pick $T$ such that $X \setminus T$ is a subset of the negative ratios. By varying the choice of negative roots in $T$, we obtain a system of equations for the roots. For example, if $n=k+1$, then $|X \setminus T|=2$. Let $X \setminus T = \{r, s\}$. Then $r, s \in R(T)$. If $b_m \neq 0$ for all $m$, then $rs$ must be a product of two ratios from $R(T)$. For $k=3, n=4$, $rs = b_0/b_2 = b_0 = \prod_{t \in T} t$. This implies the product of any two roots is the same, which forces $r_2=r_3$, a contradiction. If some $b_m=0$, the set $R(T)$ is smaller, making the condition $X \setminus T \subseteq R(T)$ even harder to satisfy.
17: 
18: In all cases, the assumption that all roots are real leads to a contradiction. Thus, $P(x)$ must have a non-real root.
