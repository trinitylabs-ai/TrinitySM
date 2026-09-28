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

1: Let $P(x)$ be a polynomial with real coefficients and leading coefficient $1$. Let $n = \deg P$. We write $P(x) = \sum_{k=0}^n a_k x^k$ with $a_n = 1$. The given equation is
2: \[ P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2} \]
3: for all nonzero real numbers $x$. The left-hand side (LHS) of the equation is
4: \[ P(x) + P(1/x) = \sum_{k=1}^n a_k (x^k + x^{-k}) + 2a_0. \]
5: For the right-hand side (RHS), let $u = x + 1/x$ and $v = x - 1/x$. Using the binomial theorem:
6: \[ u^k = \sum_{j=0}^k \binom{k}{j} x^{k-j} (1/x)^j = \sum_{j=0}^k \binom{k}{j} x^{k-2j}, \quad v^k = \sum_{j=0}^k \binom{k}{j} x^{k-j} (-1/x)^j = \sum_{j=0}^k \binom{k}{j} (-1)^j x^{k-2j}. \]
7: Summing these, we obtain
8: \[ u^k + v^k = \sum_{j=0}^k \binom{k}{j} (1 + (-1)^j) x^{k-2j} = 2 \sum_{m=0}^{\lfloor k/2 \rfloor} \binom{k}{2m} x^{k-4m}. \]
9: Substituting this into the RHS of the original equation:
10: \[ \frac{P(u) + P(v)}{2} = \frac{1}{2} \sum_{k=0}^n a_k (u^k + v^k) = \sum_{k=0}^n a_k \sum_{m=0}^{\lfloor k/2 \rfloor} \binom{k}{2m} x^{k-4m}. \]
11: We compare the coefficients of $x^j$ for $j \in \{1, \dots, n\}$ on both sides. The coefficient of $x^j$ on the LHS is $a_j$. On the RHS, $x^j$ occurs when $k-4m = j$, so $k = j+4m$. Thus:
12: \[ a_j = \sum_{m=0}^{\lfloor (n-j)/4 \rfloor} a_{j+4m} \binom{j+4m}{2m} = a_j \binom{j}{0} + \sum_{m=1}^{\lfloor (n-j)/4 \rfloor} a_{j+4m} \binom{j+4m}{2m}. \]
13: This implies that for all $j \in \{1, \dots, n\}$, we must have $\sum_{m=1}^{\lfloor (n-j)/4 \rfloor} \binom{j+4m}{2m} a_{j+4m} = 0$.
14: If $n \ge 5$, we can set $j = n-4$, giving $\binom{n}{2} a_n = 0$. Since $a_n = 1$, this is impossible for $n \ge 5$. Thus $n \le 4$.
15: 
16: Case $n=4$: $P(x) = x^4 + a_3 x^3 + a_2 x^2 + a_1 x + a_0$.
17: For $j \in \{1, 2, 3, 4\}$, the sums $\sum_{m=1}^{\lfloor (4-j)/4 \rfloor} \dots$ are empty, so the conditions on $x^j$ are trivially satisfied.
18: Now we compare the coefficients of $x^{-j}$ for $j \in \{1, 2, 3, 4\}$. The LHS coefficient of $x^{-j}$ is $a_j$. On the RHS, $x^{-j}$ occurs when $k-4m = -j$, so $k = 4m-j$.
19: - For $j=3$: $k=4m-3$. For $k \le 4$, $m=1 \implies k=1$. The RHS coefficient is $a_1 \binom{1}{2} = 0$. Thus $a_3 = 0$.
20: - For $j=1$: $k=4m-1$. For $k \le 4$, $m=1 \implies k=3$. The RHS coefficient is $a_3 \binom{3}{2} = 3a_3$. Thus $a_1 = 3a_3$. Since $a_3=0$, we have $a_1=0$.
21: - For $j=2$: $k=4m-2$. For $k \le 4$, $m=1 \implies k=2$. The RHS coefficient is $a_2 \binom{2}{2} = a_2$. Thus $a_2 = a_2$, which is always true.
22: - For $j=4$: $k=4m-4$. For $k \le 4$, $m=1 \implies k=0$ and $m=2 \implies k=4$. The RHS coefficient is $a_0 \binom{0}{2} + a_4 \binom{4}{4} = 0 + 1 = 1$. Thus $a_4 = 1$, which is given.
23: Finally, consider the constant term $x^0$. The LHS constant is $2a_0$. The RHS constant occurs when $k-4m=0$, so $k=0, m=0$ or $k=4, m=1$. The RHS constant is $a_0 \binom{0}{0} + a_4 \binom{4}{2} = a_0 + 6(1) = a_0 + 6$.
24: Thus $2a_0 = a_0 + 6 \implies a_0 = 6$.
25: The polynomials are $P(x) = x^4 + bx^2 + 6$ for any $b \in \mathbb{R}$.
26: 
27: Case $n=3$: $P(x) = x^3 + a_2 x^2 + a_1 x + a_0$.
28: The coefficient of $x^{-3}$ on the LHS is $a_3 = 1$. On the RHS, $k-4m = -3 \implies k=1, m=1$. The RHS coefficient is $a_1 \binom{1}{2} = 0$. This implies $1=0$, which is impossible.
29: 
30: Case $n=2$: $P(x) = x^2 + a_1 x + a_0$.
31: The coefficient of $x^{-1}$ on the LHS is $a_1$. On the RHS, $k-4m = -1 \implies k=3, m=1$, but $k \le 2$. Thus the RHS coefficient is $0$, implying $a_1 = 0$.
32: For the constant term, the LHS is $2a_0$. The RHS constant occurs when $k-4m=0 \implies k=0, m=0$. The RHS constant is $a_0 \binom{0}{0} = a_0$.
33: Thus $2a_0 = a_0 \implies a_0 = 0$.
34: The polynomial is $P(x) = x^2$.
35: 
36: Case $n=1$: $P(x) = x + a_0$.
37: The coefficient of $x^{-1}$ on the LHS is $a_1 = 1$. On the RHS, $k-4m = -1$ has no solutions for $k \le 1$. Thus the RHS coefficient is $0$, implying $1=0$, which is impossible.
38: 
39: Case $n=0$: $P(x) = 1$.
40: The equation becomes $1 + 1 = \frac{1+1}{2} \implies 2=1$, which is impossible.
41: 
42: The possibilities for $P$ are $P(x) = x^2$ and $P(x) = x^4 + bx^2 + 6$ for any $b \in \mathbb{R}$.
