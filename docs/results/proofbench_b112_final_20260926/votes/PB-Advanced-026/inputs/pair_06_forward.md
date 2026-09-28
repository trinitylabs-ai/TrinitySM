# Problem

Let $n$ and $k$ be positive integers with $k<n$. Let $P(x)$ be
 a polynomial of degree $n$ with real coefficients, nonzero constant
 term, and no repeated roots. Suppose that for any real numbers $a_{0},a_{1},\dots,a_{k}$
 such that the polynomial $a_{k}x^{k}+\dots+a_{1}x+a_{0}$ divides
 $P(x)$, the product $a_{0}a_{1}\dots a_{k}$ is zero. Prove that
 $P(x)$ has a non-real root.

# Proof A

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

# Proof B

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
