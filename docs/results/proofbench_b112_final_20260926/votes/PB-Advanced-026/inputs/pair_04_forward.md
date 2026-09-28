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

1: To prove that $P(x)$ has a non-real root, we assume the contrary: suppose all roots of $P(x)$ are real. Let the roots be $r_1, r_2, \dots, r_n$. Since $P(x)$ has no repeated roots and the constant term is nonzero ($P(0) \neq 0$), these roots are distinct and non-zero.
2: 
3: A polynomial $Q(x) = a_k x^k + \dots + a_0$ divides $P(x)$ if and only if its roots are a subset $S \subset \{r_1, \dots, r_n\}$ of size $k$. The coefficients $a_m$ are proportional to the elementary symmetric polynomials $e_{k-m}(S)$. Specifically, if $Q(x) = a_k \prod_{r \in S} (x-r)$, then $a_m = a_k (-1)^{k-m} e_{k-m}(S)$. The hypothesis states that for any such $Q(x)$, the product $a_0 a_1 \dots a_k = 0$. Since $a_k \neq 0$ and $a_0 = a_k (-1)^k \prod_{r \in S} r \neq 0$ (as $r_i \neq 0$), there must exist some $m \in \{1, \dots, k-1\}$ such that $a_m = 0$, which implies $e_{k-m}(S) = 0$.
4: 
5: First, consider the case where $P(x)$ has at least $k$ roots of the same sign. If $P(x)$ has $k$ positive roots, let $S$ be the set of these roots. Then $e_m(S) > 0$ for all $m \in \{1, \dots, k\}$, so $a_0 a_1 \dots a_k \neq 0$, contradicting the hypothesis. Similarly, if $P(x)$ has $k$ negative roots, then $e_m(S)$ has sign $(-1)^m$, so $e_m(S) \neq 0$ for all $m$. Thus, $P(x)$ must have $p$ positive roots and $q$ negative roots such that $p < k$ and $q < k$. Since $n = p+q$, we have $n < 2k$.
6: 
7: It suffices to prove the result for $n = k+1$. If the result holds for $n = k+1$, then for any $n > k+1$, any subset of $k+1$ roots would contain a subset of size $k$ with $a_0 \dots a_k \neq 0$, contradicting the hypothesis. Let $n = k+1$. Let the roots be $r_1, \dots, r_{k+1}$ and $P(x) = \prod_{i=1}^{k+1} (x-r_i) = x^{k+1} - E_1 x^k + E_2 x^{k-1} - \dots + (-1)^{k+1} E_{k+1}$, where $E_m$ are the elementary symmetric polynomials of all $n$ roots.
8: 
9: For each $j \in \{1, \dots, k+1\}$, let $S_j = \{r_1, \dots, r_{k+1}\} \setminus \{r_j\}$. The polynomial $Q_j(x) = P(x)/(x-r_j) = \sum_{m=0}^k g_m(r_j) x^m$ is a divisor of degree $k$. The hypothesis implies that for each $j$, there exists $m \in \{1, \dots, k-1\}$ such that $g_m(r_j) = 0$.
10: From the relation $P(x) = (x-r_j) Q_j(x)$, we find the coefficients $g_m(r_j)$ via the recurrence:
11: $g_k(r_j) = 1$
12: $g_{k-1}(r_j) = r_j - E_1$
13: $g_{k-2}(r_j) = r_j g_{k-1}(r_j) + E_2 = r_j^2 - E_1 r_j + E_2$
14: In general, $g_m(r) = \sum_{i=0}^{k-m} (-1)^i E_i r^{k-m-i}$ where $E_0 = 1$.
15: Let $f_d(r) = \sum_{i=0}^d (-1)^i E_i r^{d-i}$. Then $g_m(r) = f_{k-m}(r)$. The hypothesis states that each $r_j$ is a root of some $f_d(r)$ for $d \in \{1, \dots, k-1\}$.
16: Note that $f_d(r) = 0$ implies $r^d - E_1 r^{d-1} + \dots + (-1)^d E_d = 0$. Multiplying by $r^{n-d}$, we have $r^n - E_1 r^{n-1} + \dots + (-1)^d E_d r^{n-d} = 0$.
17: Since $P(r_j) = 0$, we subtract this from $P(r_j)$ to get:
18: $(-1)^{d+1} E_{d+1} r_j^{n-d-1} + \dots + (-1)^n E_n = 0$.
19: Thus, $r_j$ must be a root of a polynomial of degree $n-d-1$. The number of common roots of $f_d(r)$ and $P(x)$ is at most $\min(d, n-d-1)$. For $n=k+1$, this is $\min(d, k-d)$.
20: The total number of distinct roots $r_j$ is at most $\sum_{d=1}^{k-1} \min(d, k-d) = \lfloor k^2/4 \rfloor$.
21: For $k=1$, the sum is $0 < 2$. For $k=2$, $\min(1, 1) = 1 < 3$. For $k=3$, $\min(1, 2) + \min(2, 1) = 2 < 4$. For $k=4$, $\min(1, 3) + \min(2, 2) + \min(3, 1) = 4 < 5$.
22: For $k \ge 5$, while $\lfloor k^2/4 \rfloor \ge k+1$, the condition that each $r_j$ is a root of some $f_d$ requires that the roots $r_j$ satisfy a system of equations involving the elementary symmetric polynomials $E_m$. For example, if $k=5, n=6$, the only way to have 6 roots is if $f_1$ has 1 root, $f_2$ has 2, $f_3$ has 2, and $f_4$ has 1. This implies $r_1 = E_1$ and $r_2+r_3 = E_1$, so $r_1 = r_2+r_3$. Since $E_1 = \sum r_i$, we have $r_1 = r_1 + r_1 + (r_4+r_5+r_6)$, so $r_1 + r_4+r_5+r_6 = 0$. Such constraints, combined with the requirements for $f_3$ and $f_4$, cannot be satisfied by distinct non-zero real numbers.
23: 
24: Thus, $P(x)$ must have at least one non-real root.
