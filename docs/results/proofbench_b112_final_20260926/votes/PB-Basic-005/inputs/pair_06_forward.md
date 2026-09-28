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
