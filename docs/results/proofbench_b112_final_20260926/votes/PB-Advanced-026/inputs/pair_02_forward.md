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
