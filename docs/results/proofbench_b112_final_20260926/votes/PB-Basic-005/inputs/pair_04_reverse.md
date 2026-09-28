# Problem

Let $P$ be a polynomial with real coefficients whose leading coefficient is $1$. Suppose that for all nonzero real numbers $x$, we have $P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2}$. Determine all possibilities for $P$.

# Proof A

1: Let $P(x)$ be a monic polynomial with real coefficients of degree $n$. We write $P(x) = \sum_{k=0}^n a_k x^k$ with $a_n = 1$. The given condition is
2: \[ P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2} \]
3: for all nonzero real numbers $x$. Let $L(P) = P(x) + P(1/x)$ and $R(P) = \frac{P(x + 1/x) + P(x - 1/x)}{2}$.
4: Using the binomial theorem, we evaluate $R(x^k)$:
5: \[ R(x^k) = \frac{(x + x^{-1})^k + (x - x^{-1})^k}{2} = \frac{1}{2} \sum_{j=0}^k \binom{k}{j} x^{k-j} (x^{-1})^j (1 + (-1)^j) = \sum_{m=0}^{\lfloor k/2 \rfloor} \binom{k}{2m} x^{k-4m}. \]
6: The condition $L(P) = R(P)$ becomes:
7: \[ \sum_{k=0}^n a_k (x^k + x^{-k}) = \sum_{k=0}^n a_k \sum_{m=0}^{\lfloor k/2 \rfloor} \binom{k}{2m} x^{k-4m}. \]
8: First, we determine the possible values for $n$. Consider the coefficient of $x^{-n}$ on both sides. On the LHS, the coefficient is $a_n = 1$. On the RHS, a term $x^{-n}$ appears in $R(x^k)$ if $k-4m = -n$ for some $0 \le 2m \le k \le n$. This implies $4m = k+n \le 2n$, so $2m \le n$. Also, $2m \le k = 4m-n$ implies $2m \ge n$. Thus, we must have $2m = n$ and $k = n$. This requires $n$ to be even. If $n$ is odd, the coefficient of $x^{-n}$ on the RHS is 0, which contradicts $a_n = 1$. Thus, $n$ must be even.
9: 
10: Next, we bound $n$. For $n \ge 4$, consider the coefficient of $x^{n-4}$. On the LHS, the coefficient is $a_{n-4}$ if $n-4 > 0$, and $2a_0$ if $n-4 = 0$. On the RHS, $x^{n-4}$ appears in $R(x^k)$ if $k-4m = n-4$. Since $k \le n$, the only possibilities are $k=n$ (with $m=1$) and $k=n-4$ (with $m=0$). Thus, the RHS coefficient is $a_n \binom{n}{2} + a_{n-4} \binom{n-4}{0} = \binom{n}{2} + a_{n-4}$.
11: If $n > 4$, then $n-4 > 0$, and we must have $a_{n-4} = a_{n-4} + \binom{n}{2}$, which implies $\binom{n}{2} = 0$, impossible for $n \ge 2$. Thus, we only need to check $n \le 4$. Since $n$ is even, $n \in \{0, 2, 4\}$.
12: 
13: Case $n=0$: $P(x)=1$. $L(P)=2, R(P)=1$. $2 \neq 1$, so no solution.
14: Case $n=2$: $P(x)=x^2+ax+b$.
15: $L(P) = x^2 + x^{-2} + a(x + x^{-1}) + 2b$.
16: $R(P) = R(x^2) + aR(x) + bR(1) = (x^2 + x^{-2}) + ax + b$.
17: Matching coefficients: $a(x+x^{-1}) + 2b = ax + b \implies ax^{-1} + b = 0$ for all $x \neq 0$, which implies $a=0, b=0$.
18: Thus, $P(x) = x^2$.
19: Case $n=4$: $P(x)=x^4+ax^3+bx^2+cx+d$.
20: $L(P) = (x^4+x^{-4}) + a(x^3+x^{-3}) + b(x^2+x^{-2}) + c(x+x^{-1}) + 2d$.
21: $R(P) = R(x^4) + aR(x^3) + bR(x^2) + cR(x) + dR(1) = (x^4+6+x^{-4}) + a(x^3+3x^{-1}) + b(x^2+x^{-2}) + cx + d$.
22: Matching coefficients:
23: $x^{-3}: a = 0$.
24: $x^{-1}: c = 3a \implies c = 0$.
25: Constant: $2d = 6 + d \implies d = 6$.
26: The coefficient $b$ can be any real number.
27: Thus, $P(x) = x^4 + bx^2 + 6$.
28: 
29: The possible polynomials are $P(x) = x^2$ and $P(x) = x^4 + ax^2 + 6$ for any $a \in \mathbb{R}$.

# Proof B

1: To determine all polynomials $P(x)$ with real coefficients and leading coefficient $1$ that satisfy the equation
2: \[ P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2} \]
3: for all nonzero real numbers $x$, let $P(x) = \sum_{k=0}^n a_k x^k$ where $a_n = 1$. The given identity is linear in $P$. Let $L(P) = P(x) + P(1/x)$ and $R(P) = \frac{P(x + 1/x) + P(x - 1/x)}{2}$. For a monomial $x^k$, we have:
4: \[ L(x^k) = x^k + x^{-k} \]
5: Using the binomial theorem, we compute $R(x^k)$:
6: \[ R(x^k) = \frac{1}{2} \left( \sum_{j=0}^k \binom{k}{j} x^{k-j} (x^{-1})^j + \sum_{j=0}^k \binom{k}{j} x^{k-j} (-x^{-1})^j \right) = \sum_{j \text{ even}, 0 \le j \le k} \binom{k}{j} x^{k-2j} \]
7: The condition $L(P) = R(P)$ becomes:
8: \[ \sum_{k=0}^n a_k (x^k + x^{-k}) = \sum_{k=0}^n a_k \sum_{j \text{ even}, 0 \le j \le k} \binom{k}{j} x^{k-2j} \]
9: Comparing the coefficients of $x^m$ for $m > 0$:
10: The coefficient on the LHS is $a_m$. On the RHS, $x^m$ arises from $k-2j=m$ with $j$ even, so $j = 2p$ and $k = m+4p$. Thus:
11: \[ a_m = \sum_{p=0}^{\lfloor (n-m)/4 \rfloor} a_{m+4p} \binom{m+4p}{2p} \]
12: For $m=0$, the coefficient on the LHS is $2a_0$. On the RHS, $x^0$ arises from $k-2j=0$ with $j$ even, so $k=4p$. Thus:
13: \[ 2a_0 = \sum_{p=0}^{\lfloor n/4 \rfloor} a_{4p} \binom{4p}{2p} \]
14: If $n \ge 5$, consider $m=n-4 > 0$. The formula for $a_m$ gives:
15: \[ a_{n-4} = \sum_{p=0}^{\lfloor 4/4 \rfloor} a_{n-4+4p} \binom{n-4+4p}{2p} = a_{n-4} \binom{n-4}{0} + a_n \binom{n}{2} = a_{n-4} + \binom{n}{2} \]
16: This implies $\binom{n}{2} = 0$, which is impossible for $n \ge 2$. Thus, we only need to check $n \le 4$.
17: - If $n=0$, $P(x)=1 \implies 2=1$ (False).
18: - If $n=1$, $P(x)=x+a_0 \implies x+1/x+2a_0 = x+a_0 \implies 1/x+a_0=0$ (False).
19: - If $n=2$, $P(x)=x^2+a_1x+a_0$.
20:   $L(P) = x^2+1/x^2 + a_1(x+1/x) + 2a_0$.
21:   $R(P) = R(x^2) + a_1 R(x) + R(a_0) = (x^2+1/x^2) + a_1x + a_0$.
22:   Comparing coefficients: $x^{-1} \implies a_1 = 0$; $x^0 \implies 2a_0 = a_0 \implies a_0 = 0$.
23:   $P(x)=x^2$ is a solution.
24: - If $n=3$, $P(x)=x^3+a_2x^2+a_1x+a_0$.
25:   $L(P) = x^3+1/x^3 + a_2(x^2+1/x^2) + a_1(x+1/x) + 2a_0$.
26:   $R(P) = R(x^3) + a_2 R(x^2) + a_1 R(x) + R(a_0) = (x^3+3/x) + a_2(x^2+1/x^2) + a_1x + a_0$.
27:   Comparing the coefficient of $x^{-3}$: LHS is $1$, RHS is $0$. This is impossible.
28: - If $n=4$, $P(x)=x^4+a_3x^3+a_2x^2+a_1x+a_0$.
29:   $L(P) = x^4+1/x^4 + a_3(x^3+1/x^3) + a_2(x^2+1/x^2) + a_1(x+1/x) + 2a_0$.
30:   $R(P) = R(x^4) + a_3 R(x^3) + a_2 R(x^2) + a_1 R(x) + R(a_0) = (x^4+6+1/x^4) + a_3(x^3+3/x) + a_2(x^2+1/x^2) + a_1x + a_0$.
31:   Comparing coefficients:
32:   $x^0 \implies 2a_0 = 6 + a_0 \implies a_0 = 6$.
33:   $x^{-3} \implies a_3 = 0$.
34:   $x^{-1} \implies a_1 = 3a_3 = 0$.
35:   $a_2$ remains arbitrary.
36:   $P(x) = x^4 + a_2x^2 + 6$ is a solution.
37: 
38: The possibilities for $P$ are $P(x) = x^2$ and $P(x) = x^4 + ax^2 + 6$ for any $a \in \mathbb{R}$.
