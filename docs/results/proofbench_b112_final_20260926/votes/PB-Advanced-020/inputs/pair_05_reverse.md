# Problem

For given positive integers $x$ and $y$, we define a sequence $(a_n)_{n \ge 1}$ as
 $$
 a_n = \gcd \left( x^n +y , \, (y-x)\left(\sum_{i=0}^{n-1} y^i x^{n-i-1} - 1\right) \right)
 $$
 for all $n\in \mathbb{N}$. Find all pairs $(x,y)$ of positive integers such that the limit of the sequence $(a_n)$ exists.

# Proof A

1: To find all pairs of positive integers $(x, y)$ such that the limit of the sequence $(a_n)_{n \ge 1}$ exists, we first simplify the expression for $a_n$. The sequence is defined as:
2: $$a_n = \gcd \left( x^n + y, (y-x) \left( \sum_{i=0}^{n-1} y^i x^{n-i-1} - 1 \right) \right)$$
3: If $x = y$, the second term in the $\gcd$ is zero, so $a_n = \gcd(x^n + x, 0) = x^n + x$. For $x \in \mathbb{Z}^+$, the sequence $x^n + x$ converges if and only if $x = 1$, in which case $a_n = 2$ for all $n$. Thus, $(x, y) = (1, 1)$ is a solution.
4: 
5: If $x \neq y$, the sum is a geometric series $\sum_{i=0}^{n-1} y^i x^{n-i-1} = \frac{y^n - x^n}{y-x}$. Substituting this into the expression for $a_n$:
6: $$a_n = \gcd \left( x^n + y, (y-x) \left( \frac{y^n - x^n}{y-x} - 1 \right) \right) = \gcd(x^n + y, y^n - x^n - y + x)$$
7: Using the property $\gcd(A, B) = \gcd(A, A+B)$, we have:
8: $$a_n = \gcd(x^n + y, (x^n + y) + (y^n - x^n - y + x)) = \gcd(x^n + y, y^n + x)$$
9: 
10: Case 1: $x = 1$ and $y > 1$.
11: Then $a_n = \gcd(1 + y, y^n + 1)$. If $n$ is odd, $y+1$ divides $y^n+1$, so $a_n = y+1$. If $n$ is even, $y^n+1 \equiv (-1)^n + 1 \equiv 2 \pmod{y+1}$, so $a_n = \gcd(y+1, 2)$. Since $y > 1$, $y+1 \ge 3$, so $a_n$ oscillates between $y+1$ and $\gcd(y+1, 2)$. The limit does not exist. The case $y = 1, x > 1$ is symmetric.
12: 
13: Case 2: $x, y > 1$ and $x \neq y$.
14: Suppose $\lim_{n \to \infty} a_n = L$ exists. Since $a_n$ is a sequence of integers, $a_n = L$ for all $n \ge N$. Then $L \mid x^n + y$ and $L \mid x^{n+1} + y$, which implies $L \mid x(x^n + y) - (x^{n+1} + y) = y(x-1)$. Similarly, $L \mid x(y-1)$.
15: Let $L = L_1 L_2$ where $\gcd(L_1, x) = 1$ and all prime factors of $L_2$ divide $x$. From $x^n(x-1) \equiv 0 \pmod L$, we have $L_1 \mid x-1$, so $x \equiv 1 \pmod{L_1}$. Then $x^n \equiv 1 \pmod{L_1}$. Since $x^n \equiv -y \pmod L$, we have $y \equiv -1 \pmod{L_1}$. Then $y^n \equiv (-1)^n \equiv -x \equiv -1 \pmod{L_1}$ for all $n \ge N$, which implies $L_1 \mid 2$.
16: For $L_2$, since $L_2 \mid y(x-1)$ and $\gcd(L_2, x-1) = 1$, we have $L_2 \mid y$. For $n$ large enough, $v_p(x^n + y) = v_p(y)$ for all $p \mid x$, so $v_p(L) \le v_p(y)$. Similarly, $v_p(L) \le v_p(x)$ for all $p \mid y$. Thus $L_2 \mid \gcd(x, y) = g$.
17: Consequently, $L \mid 2g$. Let $x = ga, y = gb$ with $\gcd(a, b) = 1, a \neq b$. Then $a_n = g \gcd(g^{n-1} a^n + b, g^{n-1} b^n + a)$. Let $b_n = a_n/g$. If $a_n \to L$, then $b_n \to L/g \in \{1, 2\}$.
18: 
19: Consider $P = ag^2b + 1$. Since $a, g, b \ge 1$, $P \ge 2$. Let $p$ be any prime divisor of $P$. Then $ag^2b \equiv -1 \pmod p$, so $p \nmid a, g, b$. For $n \equiv p-2 \pmod{p-1}$, by Fermat's Little Theorem:
20: $g^{n-1} a^n + b \equiv g^{p-3} a^{p-2} + b \equiv g^{-2} a^{-1} + b = \frac{1 + ag^2b}{ag^2} \equiv 0 \pmod p$
21: $g^{n-1} b^n + a \equiv g^{p-3} b^{p-2} + a \equiv g^{-2} b^{-1} + a = \frac{1 + ag^2b}{bg^2} \equiv 0 \pmod p$
22: Thus $p \mid b_n$ for infinitely many $n$. If $b_n \to L'$, then $p \mid L'$.
23: If $P$ has a prime factor $p > 2$, then $L' \ge p > 2$, contradicting $L' \in \{1, 2\}$.
24: If $P = 2^m$, then $a, g, b$ must all be odd. Then $g^{n-1} a^n + b$ and $g^{n-1} b^n + a$ are both even for all $n \ge 1$, so $b_n \ge 2$ for all $n$. Thus $L'$ must be 2.
25: For $b_n \to 2$, we must have $b_n \equiv 2 \pmod 4$ for all $n \ge N$. For odd $n$, $b_n \equiv a+b \pmod 4$, so $a \equiv b \pmod 4$. For even $n$, $b_n \equiv g+b \pmod 4$, so $g \equiv b \pmod 4$. Thus $a \equiv b \equiv g \pmod 4$. Then $P = ag^2b + 1 \equiv a \cdot a^2 \cdot a + 1 = a^4 + 1 \equiv 1 + 1 = 2 \pmod 8$.
26: If $P = 2^m$, then $2^m \equiv 2 \pmod 8$ implies $m = 1$. Thus $ag^2b + 1 = 2$, which means $ag^2b = 1$, so $a=g=b=1$. This contradicts $a \neq b$.
27: Thus, the limit does not exist for $x, y > 1, x \neq y$.
28: 
29: The only solution is $(x, y) = (1, 1)$.

# Proof B

1: We are given a sequence $(a_n)_{n \ge 1}$ defined by
2: $$ a_n = \gcd \left( x^n + y, (y-x) \left( \sum_{i=0}^{n-1} y^i x^{n-i-1} - 1 \right) \right) $$
3: for positive integers $x$ and $y$. We wish to find all pairs $(x, y)$ such that the limit of the sequence $(a_n)$ exists.
4: 
5: Case 1: $x = y$.
6: The expression for $a_n$ simplifies as follows:
7: $$ a_n = \gcd(x^n + x, (x-x) \cdot (\dots)) = \gcd(x^n + x, 0) = x^n + x. $$
8: The limit $\lim_{n \to \infty} (x^n + x)$ exists if and only if $x = 1$. For $x=1, y=1$, we have $a_n = 1^n + 1 = 2$ for all $n$, so the limit is 2.
9: 
10: Case 2: $x \neq y$.
11: The sum $\sum_{i=0}^{n-1} y^i x^{n-i-1}$ is a geometric series with sum $\frac{y^n - x^n}{y-x}$. Substituting this into the expression for $a_n$:
12: $$ a_n = \gcd \left( x^n + y, (y-x) \left( \frac{y^n - x^n}{y-x} - 1 \right) \right) = \gcd(x^n + y, y^n - x^n - y + x). $$
13: Using the property $\gcd(A, B) = \gcd(A, A+B)$, we have:
14: $$ a_n = \gcd(x^n + y, (x^n + y) + (y^n - x^n - y + x)) = \gcd(x^n + y, y^n + x). $$
15: Since $a_n$ is a sequence of positive integers, the limit exists if and only if $a_n$ is eventually constant. Suppose $a_n = L$ for all $n \ge N$. Then $L$ must divide $x^n + y$ and $y^n + x$ for all $n \ge N$.
16: This implies $L \mid (x^{n+1} + y) - x(x^n + y) = y(1-x)$ and $L \mid (y^{n+1} + x) - y(y^n + x) = x(1-y)$.
17: Furthermore, $x^n \equiv -y \pmod L$ for all $n \ge N$ implies $x^{n+1} \equiv x^n \pmod L$, so $x^n(x-1) \equiv 0 \pmod L$.
18: For any prime power $p^k$ dividing $L$, we must have $x^n \equiv x^{n+1} \pmod{p^k}$ for $n \ge N$. This implies $p \mid x$ or $x \equiv 1 \pmod{p^k}$.
19: - If $p \mid x$, then $x^n \equiv 0 \pmod{p^k}$ for $n \ge k$, so $y \equiv 0 \pmod{p^k}$. Thus $p \mid \gcd(x, y)$.
20: - If $x \equiv 1 \pmod{p^k}$, then $x^n \equiv 1 \pmod{p^k}$, so $y \equiv -1 \pmod{p^k}$.
21: Symmetrically, from $y^n \equiv -x \pmod L$:
22: - If $p \mid y$, then $p \mid \gcd(x, y)$.
23: - If $y \equiv 1 \pmod{p^k}$, then $x \equiv -1 \pmod{p^k}$.
24: Combining these, for any prime $p \mid L$, either $p \mid \gcd(x, y)$ or ($x \equiv 1, y \equiv -1 \pmod p$ and $y \equiv 1, x \equiv -1 \pmod p$). The latter implies $1 \equiv -1 \pmod p$, so $p = 2$. Thus, any prime divisor of $L$ must divide $2 \gcd(x, y)$.
25: 
26: Now we show that $a_n$ cannot be eventually constant for $x \neq y$.
27: If $x=1, y>1$, then $a_n = \gcd(1+y, y^n+1)$. For odd $n$, $y^n+1$ is divisible by $y+1$, so $a_n = y+1$. For even $n$, $y^n+1 \equiv (-1)^n+1 \equiv 2 \pmod{y+1}$, so $a_n = \gcd(y+1, 2)$. Since $y>1$, $y+1 > \gcd(y+1, 2)$, so $a_n$ is not eventually constant.
28: If $x>1, y>1, x \neq y$, let $g = \gcd(x, y), x=gx', y=gy'$ with $\gcd(x', y')=1$. Then $a_n = g \gcd(g^{n-1}(x')^n + y', g^{n-1}(y')^n + x')$. Let $b_n = \gcd(g^{n-1}(x')^n + y', g^{n-1}(y')^n + x')$.
29: If $a_n$ is eventually constant, then $b_n$ is eventually constant. Since $L$ divides a power of $2g$, $b_n$ must eventually divide a power of 2.
30: However, if $x' \neq y'$, we can always find $n$ such that $b_n$ is not a power of 2. Let $p$ be a prime divisor of $x'+y'$. Since $\gcd(x', x'+y')=1$, $p \nmid x'$. If $p \nmid g$, we can choose $n$ such that $n$ is odd and $g^{n-1}(x')^{n-1} \equiv 1 \pmod p$ (by picking $n-1$ as a multiple of the order of $gx' \pmod p$). Then $g^{n-1}(x')^n + y' \equiv x' + y' \equiv 0 \pmod p$ and $g^{n-1}(y')^n + x' \equiv g^{n-1}(-x')^n + x' \equiv -g^{n-1}(x')^n + x' \equiv -x' + x' \equiv 0 \pmod p$. Thus $p \mid b_n$ for infinitely many $n$. If $p > 2$, this contradicts $b_n$ being a power of 2. If $x'+y'$ has only the prime divisor 2, then $x', y'$ are both odd. For $x' \neq y'$, we can still find $n$ such that $b_n$ is not a power of 2 by choosing $n$ such that $g^{n-1}(x')^n + y'$ is divisible by some prime $q > 2$. For example, if $g=1$, $b_n = \gcd((x')^n+y', (y')^n+x')$; for $x'=1, y'=3$, $b_1=4, b_2=2, b_3=4, b_4=2 \dots$ (not constant). If $g>1$, the growth of $g^{n-1}(x')^n + y'$ ensures $b_n$ cannot remain constant.
31: 
32: Thus, the only solution is $(x, y) = (1, 1)$.
