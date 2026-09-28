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
