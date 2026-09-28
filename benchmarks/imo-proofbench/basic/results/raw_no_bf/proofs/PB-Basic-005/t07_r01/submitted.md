To find all polynomials $P(x)$ with real coefficients and leading coefficient $1$ such that for all nonzero real numbers $x$,
\[ P(x) + P(1/x) = \frac{P(x + 1/x) + P(x - 1/x)}{2}, \]
let $n = \deg(P)$. We express $P$ as $P(x) = \sum_{k=0}^n a_k x^k$ with $a_n = 1$.
The given equation can be written as a linear operator equality $L(P) = R(P)$, where $L(P) = P(x) + P(1/x)$ and $R(P) = \frac{P(x+1/x) + P(x-1/x)}{2}$.
Using the binomial expansion, we have
\[ R(x^k) = \frac{1}{2} \left( \sum_{j=0}^k \binom{k}{j} x^{k-j} x^{-j} + \sum_{j=0}^k \binom{k}{j} x^{k-j} (-x^{-1})^j \right) = \sum_{j \text{ even}} \binom{k}{j} x^{k-2j}. \]
Let $j = 2m$, then $R(x^k) = \sum_{m=0}^{\lfloor k/2 \rfloor} \binom{k}{2m} x^{k-4m}$.
The equation $L(P) = R(P)$ becomes:
\[ \sum_{k=0}^n a_k (x^k + x^{-k}) = \sum_{k=0}^n a_k \sum_{m=0}^{\lfloor k/2 \rfloor} \binom{k}{2m} x^{k-4m}. \]
We compare the coefficients of $x^p$ for $p > 0$.
For $p=n$, the LHS coefficient is $a_n = 1$. On the RHS, the only term $x^{k-4m}$ that can equal $x^n$ is when $k=n$ and $m=0$, giving $a_n \binom{n}{0} = 1$.
For $p=n-1$, the LHS coefficient is $a_{n-1}$. On the RHS, $k-4m = n-1$ implies $k=n-1$ and $m=0$ (since $k \le n$), giving $a_{n-1} \binom{n-1}{0} = a_{n-1}$.
For $p=n-2$, the LHS coefficient is $a_{n-2}$. On the RHS, $k-4m = n-2$ implies $k=n-2$ and $m=0$, giving $a_{n-2} \binom{n-2}{0} = a_{n-2}$.
For $p=n-4$, if $n > 4$, the LHS coefficient is $a_{n-4}$. On the RHS, $k-4m = n-4$ is satisfied by $(k,m) = (n-4, 0)$ and $(k,m) = (n, 1)$. Thus,
\[ a_{n-4} = a_{n-4} \binom{n-4}{0} + a_n \binom{n}{2} = a_{n-4} + 1 \cdot \binom{n}{2}. \]
This implies $\binom{n}{2} = 0$, which means $n < 2$. This contradicts $n > 4$.
Thus, we must have $n \le 4$. We check the cases $n=0, 1, 2, 3, 4$:
1. $n=0$: $P(x)=1$. $L(P)=2, R(P)=1$. No.
2. $n=1$: $P(x)=x+a$. $L(P)=x+x^{-1}+2a, R(P)=x+a$. No.
3. $n=2$: $P(x)=x^2+ax+b$. $L(P)=x^2+x^{-2}+a(x+x^{-1})+2b$. $R(P)=R(x^2)+aR(x)+R(b) = (x^2+x^{-2})+ax+b$.
Equating these gives $ax^{-1}+b=0$, so $a=b=0$. $P(x)=x^2$.
4. $n=3$: $P(x)=x^3+a_2x^2+a_1x+a_0$. $L(P)$ contains $x^{-3}$ and $x^3$. $R(P)$ contains $x^3$ and $3a_3x^{-1}$.
Matching $x^{-3}$ coefficients: $a_3=0$, but $a_3=1$. No.
5. $n=4$: $P(x)=x^4+a_3x^3+a_2x^2+a_1x+a_0$.
$L(P) = (x^4+x^{-4}) + a_3(x^3+x^{-3}) + a_2(x^2+x^{-2}) + a_1(x+x^{-1}) + 2a_0$.
$R(P) = (x^4+6+x^{-4}) + a_3(x^3+3x^{-1}) + a_2(x^2+x^{-2}) + a_1x + a_0$.
Comparing coefficients:
- $x^3: a_3 = a_3$.
- $x^1: a_1 = a_1$.
- $x^0: 2a_0 = 6 + a_0 \implies a_0 = 6$.
- $x^{-1}: a_1 = 3a_3$.
- $x^{-3}: a_3 = 0 \implies a_1 = 0$.
- $x^2, x^4$: match for any $a_2$.
Thus $P(x) = x^4 + ax^2 + 6$ for any $a \in \mathbb{R}$.

The possible polynomials are $P(x) = x^2$ and $P(x) = x^4 + ax^2 + 6$ for any $a \in \mathbb{R}$.

\(\square\)
