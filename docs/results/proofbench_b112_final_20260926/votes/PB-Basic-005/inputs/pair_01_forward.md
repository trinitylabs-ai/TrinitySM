# Problem

Let $P$ be a polynomial with real coefficients whose leading coefficient is $1$. Suppose that for all nonzero real numbers $x$, we have $P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2}$. Determine all possibilities for $P$.

# Proof A

1: To find all monic polynomials $P(x)$ with real coefficients such that for all nonzero real numbers $x$,
2: \[ P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2}, \]
3: let $d$ be the degree of $P$. We write $P(x) = \sum_{n=0}^d a_n x^n$ where $a_d = 1$.
4: Let $L(P) = P(x) + P(1/x)$ and $R(P) = \frac{P(x + 1/x) + P(x - 1/x)}{2}$. These are linear operators. For a monomial $x^n$, we have $L(x^n) = x^n + x^{-n}$ and
5: \[ R(x^n) = \frac{1}{2} \left( (x + x^{-1})^n + (x - x^{-1})^n \right). \]
6: Using the binomial theorem, $(x \pm x^{-1})^n = \sum_{k=0}^n \binom{n}{k} x^{n-k} (\pm x^{-1})^k = \sum_{k=0}^n \binom{n}{k} (\pm 1)^k x^{n-2k}$. Thus,
7: \[ R(x^n) = \sum_{k=0, k \text{ even}}^n \binom{n}{k} x^{n-2k} = \sum_{j=0}^{\lfloor n/2 \rfloor} \binom{n}{2j} x^{n-4j}. \]
8: The condition $L(P) = R(P)$ implies:
9: \[ \sum_{n=0}^d a_n (x^n + x^{-n}) = \sum_{n=0}^d a_n \sum_{j=0}^{\lfloor n/2 \rfloor} \binom{n}{2j} x^{n-4j}. \]
10: Comparing the coefficients of $x^k$ for $k > 0$:
11: The coefficient of $x^k$ on the LHS is $a_k$. On the RHS, $x^k$ appears when $n-4j = k$, meaning $n = k+4j$. Thus,
12: \[ a_k = \sum_{j=0}^{\lfloor (d-k)/4 \rfloor} a_{k+4j} \binom{k+4j}{2j} = a_k \binom{k}{0} + \sum_{j=1}^{\lfloor (d-k)/4 \rfloor} a_{k+4j} \binom{k+4j}{2j}. \]
13: This implies $\sum_{j=1}^{\lfloor (d-k)/4 \rfloor} a_{k+4j} \binom{k+4j}{2j} = 0$ for all $k \in \{1, \dots, d\}$.
14: If $d \ge 5$, we can set $k = d-4$. Since $d \ge 5$, $k \ge 1$. The sum contains only the $j=1$ term:
15: \[ a_d \binom{d}{2} = 0. \]
16: Since $a_d = 1$, we must have $\binom{d}{2} = 0$, which implies $d=0$ or $d=1$. This contradicts $d \ge 5$. Thus, $d \le 4$.
17: 
18: We check each possible degree $d \in \{0, 1, 2, 3, 4\}$:
19: 1.  **$d=0$**: $P(x)=1$. $L(P)=2$, $R(P)=1$. No.
20: 2.  **$d=1$**: $P(x)=x+a$. $L(P)=x+1/x+2a$, $R(P)=x+a$. No.
21: 3.  **$d=2$**: $P(x)=x^2+ax+b$.
22:     $L(P) = x^2 + 1/x^2 + a(x+1/x) + 2b$.
23:     $R(P) = \frac{(x+1/x)^2+a(x+1/x)+b + (x-1/x)^2+a(x-1/x)+b}{2} = x^2 + 1/x^2 + ax + b$.
24:     Matching coefficients: $a/x + b = 0 \implies a=0, b=0$. Thus $P(x) = x^2$.
25: 4.  **$d=3$**: $P(x)=x^3+a_2x^2+a_1x+a_0$.
26:     $k=0 \implies 2a_0 = a_0 \implies a_0=0$.
27:     $k=-1 \implies a_1 = a_3 \binom{3}{2} = 3(1) = 3$.
28:     $k=-3 \implies a_3 = a_1 \binom{1}{2} = 0$. This implies $1=0$, a contradiction.
29: 5.  **$d=4$**: $P(x)=x^4+a_3x^3+a_2x^2+a_1x+a_0$.
30:     $k=0 \implies 2a_0 = a_0 \binom{0}{0} + a_4 \binom{4}{2} = a_0 + 6(1) \implies a_0 = 6$.
31:     $k=-1 \implies a_1 = a_3 \binom{3}{2} = 3a_3$.
32:     $k=-2 \implies a_2 = a_2 \binom{2}{2} = a_2$.
33:     $k=-3 \implies a_3 = a_1 \binom{1}{2} = 0 \implies a_3=0, a_1=0$.
34:     $k=-4 \implies a_4 = a_0 \binom{0}{2} + a_4 \binom{4}{4} = a_4$.
35:     Thus $P(x) = x^4 + ax^2 + 6$ for any $a \in \mathbb{R}$.
36: 
37: Verification for $P(x) = x^4 + ax^2 + 6$:
38: $L(P) = (x^4 + ax^2 + 6) + (x^{-4} + ax^{-2} + 6) = x^4 + x^{-4} + a(x^2 + x^{-2}) + 12$.
39: $R(P) = \frac{(x+1/x)^4+a(x+1/x)^2+6 + (x-1/x)^4+a(x-1/x)^2+6}{2}$.
40: Since $(x+1/x)^4 + (x-1/x)^4 = 2(x^4 + 6 + x^{-4})$ and $(x+1/x)^2 + (x-1/x)^2 = 2(x^2 + x^{-2})$, we have:
41: $R(P) = x^4 + 6 + x^{-4} + a(x^2 + x^{-2}) + 6 = x^4 + x^{-4} + a(x^2 + x^{-2}) + 12$.
42: The expressions match.
43: 
44: The possible polynomials are $P(x) = x^2$ and $P(x) = x^4 + ax^2 + 6$ for any $a \in \mathbb{R}$.
45: 
46: \(\square\)

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
