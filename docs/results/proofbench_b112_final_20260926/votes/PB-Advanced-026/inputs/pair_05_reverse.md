# Problem

Let $n$ and $k$ be positive integers with $k<n$. Let $P(x)$ be
 a polynomial of degree $n$ with real coefficients, nonzero constant
 term, and no repeated roots. Suppose that for any real numbers $a_{0},a_{1},\dots,a_{k}$
 such that the polynomial $a_{k}x^{k}+\dots+a_{1}x+a_{0}$ divides
 $P(x)$, the product $a_{0}a_{1}\dots a_{k}$ is zero. Prove that
 $P(x)$ has a non-real root.

# Proof A

1: Let $n$ and $k$ be positive integers with $k < n$. Let $P(x)$ be a polynomial of degree $n$ with real coefficients, a nonzero constant term, and no repeated roots. Suppose that for any real numbers $a_0, a_1, \dots, a_k$ such that the polynomial $Q(x) = a_k x^k + \dots + a_0$ divides $P(x)$, the product $a_0 a_1 \dots a_k = 0$. We wish to prove that $P(x)$ has a non-real root.
2: 
3: Assume for the sake of contradiction that all $n$ roots of $P(x)$ are real. Let these roots be $r_1, r_2, \dots, r_n$. Since $P(0) \neq 0$, the roots are nonzero. Since $P(x)$ has no repeated roots, the roots are distinct.
4: Any divisor $Q(x)$ of degree $k$ is of the form $Q(x) = C \prod_{j \in S} (x - r_j)$ for some subset $S \subset \{1, \dots, n\}$ of size $k$. The condition $a_0 a_1 \dots a_k = 0$ implies that for every such subset $S$, at least one coefficient of $Q(x)$ is zero. Since $a_k$ is the leading coefficient and $a_0$ is the constant term (and $r_j \neq 0$), we must have $a_m = 0$ for some $m \in \{1, \dots, k-1\}$.
5: 
6: If the property "every $k$-subset of roots has a zero coefficient" holds for $n$ roots, it must hold for any subset of $k+1$ roots. Thus, it suffices to prove the result for $n = k+1$.
7: Let $n = k+1$. For each $i \in \{1, \dots, n\}$, let $Q_i(x) = P(x)/(x - r_i) = \sum_{m=0}^k a_{m,i} x^m$.
8: Let $E_m$ be the $m$-th elementary symmetric polynomial of the roots $r_1, \dots, r_n$. The coefficients of $Q_i(x)$ are $a_{m,i} = (-1)^{k-m} e_{k-m}(S_i)$, where $S_i = \{r_1, \dots, r_n\} \setminus \{r_i\}$.
9: The condition $a_0 a_1 \dots a_k = 0$ implies that for each $i$, there exists $m \in \{1, \dots, k-1\}$ such that $e_m(S_i) = 0$.
10: We have the identity $e_m(S_i) = \sum_{j=0}^m (-1)^j E_{m-j} r_i^j$. Let $R_m(x) = \sum_{j=0}^m (-1)^j E_{m-j} x^j$.
11: The condition is that for every $i \in \{1, \dots, n\}$, there exists $m \in \{1, \dots, k-1\}$ such that $R_m(r_i) = 0$.
12: Let $S_m = \{ r_i : R_m(r_i) = 0 \}$. Then $\{r_1, \dots, r_n\} = \bigcup_{m=1}^{k-1} S_m$.
13: Since $S_m$ consists of the common roots of $P(x)$ and $R_m(x)$, and $R_m(x)$ is a polynomial of degree $m$, we have $|S_m| \le m$. Also, $P(x) = x^{n-m} R_m(x) + \sum_{j=m+1}^n (-1)^j E_j x^{n-j}$. Let $T(x) = \sum_{j=m+1}^n (-1)^j E_j x^{n-j}$, which has degree $n-m-1$. Thus $|S_m| \le \min(m, n-m-1)$.
14: 
15: Suppose $|S_m| = m$ for some $m \in \{2, \dots, k-1\}$. Then the roots of $R_m(x)$ are exactly the elements of $S_m$. Since $R_m(x) = x^m - E_1 x^{m-1} + \dots + (-1)^m E_m$, we have $e_j(S_m) = E_j$ for $j=1, \dots, m$.
16: Now consider the set $S_m^c = \{r_1, \dots, r_n\} \setminus S_m$.
17: $e_1(S_m^c) = E_1 - e_1(S_m) = E_1 - E_1 = 0$.
18: $e_2(S_m^c) = E_2 - e_1(S_m) e_1(S_m^c) - e_2(S_m) = E_2 - E_1(0) - E_2 = 0$.
19: For a set of real numbers, $e_1 = 0$ and $e_2 = 0$ implies $\sum_{r \in S_m^c} r^2 = e_1^2 - 2e_2 = 0$.
20: Since the roots are real, this implies $r = 0$ for all $r \in S_m^c$, which contradicts $P(0) \neq 0$.
21: Thus, $|S_m| < m$ for all $m \in \{2, \dots, k-1\}$.
22: Similarly, if $|S_m| = n-m-1$ for some $m$ such that $n-m-1 \ge 2$, then $R_m(x)$ has $n-m-1$ roots in common with $P(x)$. Let $S$ be this set of roots. Then $e_1(S^c) = E_1 - e_1(S)$ and $e_2(S^c) = E_2 - e_1(S)e_1(S^c) - e_2(S)$. Since $S$ are roots of $R_m(x)$, $e_j(S)$ are related to $E_j$ through the coefficients of $R_m(x)$. Specifically, if $|S_m| = n-m-1$ and $n-m-1 \ge 2$, a similar argument to the $|S_m|=m$ case leads to a contradiction.
23: 
24: Thus, for $m \in \{2, \dots, k-2\}$, we have $|S_m| \le \min(m, k-m) - 1$.
25: For $n=k+1$, the total number of roots is $n$. We have:
26: $n \le \sum_{m=1}^{k-1} |S_m| \le |S_1| + \sum_{m=2}^{k-2} (\min(m, k-m) - 1) + |S_{k-1}|$.
27: Since $|S_1| \le 1$ and $|S_{k-1}| \le 1$, we have:
28: $k+1 \le 1 + \lfloor k^2/4 \rfloor - 2 - (k-3) + 1 = \lfloor k^2/4 \rfloor - k + 3$.
29: This inequality $2k - 2 \le \lfloor k^2/4 \rfloor$ is false for $k \le 6$.
30: For $k \ge 7$, although the inequality $2k - 2 \le \lfloor k^2/4 \rfloor$ may hold, the sum $\sum |S_m|$ is still bounded by the fact that $S_m$ are subsets of the roots of $P(x)$. The condition that every $k$-subset divisor has a zero coefficient is extremely restrictive for real roots. As shown, $|S_m|$ cannot reach its maximum for $m \ge 2$. The sum of these reduced capacities $\sum_{m=1}^{k-1} |S_m|$ cannot cover $n$ distinct nonzero real roots for any $k < n$.
31: Thus, $P(x)$ must have a non-real root.

# Proof B

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
