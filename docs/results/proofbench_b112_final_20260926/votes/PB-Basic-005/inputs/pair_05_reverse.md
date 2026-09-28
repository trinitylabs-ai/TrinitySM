# Problem

Let $P$ be a polynomial with real coefficients whose leading coefficient is $1$. Suppose that for all nonzero real numbers $x$, we have $P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2}$. Determine all possibilities for $P$.

# Proof A

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
