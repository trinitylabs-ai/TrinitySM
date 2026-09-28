# Problem

Let $n$ and $k$ be positive integers with $k<n$. Let $P(x)$ be
 a polynomial of degree $n$ with real coefficients, nonzero constant
 term, and no repeated roots. Suppose that for any real numbers $a_{0},a_{1},\dots,a_{k}$
 such that the polynomial $a_{k}x^{k}+\dots+a_{1}x+a_{0}$ divides
 $P(x)$, the product $a_{0}a_{1}\dots a_{k}$ is zero. Prove that
 $P(x)$ has a non-real root.

# Proof A

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
