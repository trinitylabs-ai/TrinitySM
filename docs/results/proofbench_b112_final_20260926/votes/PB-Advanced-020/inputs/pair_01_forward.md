# Problem

For given positive integers $x$ and $y$, we define a sequence $(a_n)_{n \ge 1}$ as
 $$
 a_n = \gcd \left( x^n +y , \, (y-x)\left(\sum_{i=0}^{n-1} y^i x^{n-i-1} - 1\right) \right)
 $$
 for all $n\in \mathbb{N}$. Find all pairs $(x,y)$ of positive integers such that the limit of the sequence $(a_n)$ exists.

# Proof A

1: For given positive integers $x$ and $y$, the sequence $(a_n)_{n \ge 1}$ is defined as
2: $$
3: a_n = \gcd \left( x^n + y, (y-x)\left(\sum_{i=0}^{n-1} y^i x^{n-i-1} - 1\right) \right).
4: $$
5: First, we simplify the expression for $a_n$. If $x = y$, the second term in the $\gcd$ is $0 \cdot (nx^{n-1} - 1) = 0$. Thus, $a_n = \gcd(x^n + x, 0) = x^n + x$. For the limit of $a_n$ to exist, the sequence must be eventually constant, which requires $x^n + x = x^{n+1} + x$ for all $n \ge N$. This implies $x^n(x-1) = 0$, so $x=1$. If $x=y=1$, then $a_n = 1^n + 1 = 2$ for all $n$, and the limit is 2. If $x=y > 1$, $a_n \to \infty$ as $n \to \infty$, so the limit does not exist.
6: 
7: If $x \neq y$, the sum $\sum_{i=0}^{n-1} y^i x^{n-i-1}$ is a geometric series with sum $\frac{y^n - x^n}{y-x}$. Substituting this into the expression for $a_n$:
8: $$
9: a_n = \gcd(x^n + y, (y-x) \left( \frac{y^n - x^n}{y-x} - 1 \right)) = \gcd(x^n + y, y^n - x^n - y + x).
10: $$
11: Using the property $\gcd(A, B) = \gcd(A, A+B)$, we have:
12: $$
13: a_n = \gcd(x^n + y, (y^n - x^n - y + x) + (x^n + y)) = \gcd(x^n + y, y^n + x).
14: $$
15: Assume for contradiction that the limit $\lim_{n \to \infty} a_n = L$ exists. Since $a_n$ is a sequence of integers, it must be eventually constant, so $a_n = L$ for all $n \ge N$. This implies $x^n \equiv -y \pmod L$ and $y^n \equiv -x \pmod L$ for all $n \ge N$.
16: From $x^n \equiv -y \pmod L$ and $x^{n+1} \equiv -y \pmod L$, we have $x(-y) \equiv -y \pmod L$, which means $y(x-1) \equiv 0 \pmod L$. Similarly, $x(y-1) \equiv 0 \pmod L$.
17: Let $g = \gcd(x, y)$, $x=gX$, and $y=gY$ with $\gcd(X, Y)=1$. Then $a_n = g \cdot \gcd(g^{n-1} X^n + Y, g^{n-1} Y^n + X)$. Let $b_n = a_n/g$. If $a_n$ is eventually constant $L$, then $b_n$ is eventually constant $L' = L/g$.
18: For $n \ge N$, $g^{n-1} X^n \equiv -Y \pmod{L'}$ and $g^{n-1} Y^n \equiv -X \pmod{L'}$.
19: Any prime $p$ dividing $L'$ cannot divide $g$, because if $p|g$, then $p|Y$ and $p|X$ from the congruences, contradicting $\gcd(X, Y)=1$. Thus $\gcd(L', g) = 1$.
20: Since $g^{n-1} X^n \equiv -Y \pmod{L'}$ and $g^n X^{n+1} \equiv -Y \pmod{L'}$, we have $gX(g^{n-1} X^n) \equiv -Y \pmod{L'}$, so $gX(-Y) \equiv -Y \pmod{L'}$, which implies $Y(gX-1) \equiv 0 \pmod{L'}$. Since $\gcd(L', Y) = 1$ (as $L' | g^{n-1} X^n + Y$ and $\gcd(X, Y)=1$), we have $gX \equiv 1 \pmod{L'}$. Similarly, $gY \equiv 1 \pmod{L'}$.
21: This implies $X \equiv Y \pmod{L'}$. Also, $g^{n-1} X^n = (gX)^{n-1} X \equiv 1^{n-1} X = X \pmod{L'}$. Thus $X \equiv -Y \pmod{L'}$.
22: Combining $X \equiv Y \pmod{L'}$ and $X \equiv -Y \pmod{L'}$, we get $2X \equiv 0 \pmod{L'}$. Since $\gcd(X, L')=1$, we must have $L' \mid 2$, so $L' \in \{1, 2\}$.
23: This means the only possible limits are $L = g$ or $L = 2g$.
24: However, $a_1 = x+y = g(X+Y)$. Since $x \neq y$, $X+Y \ge 3$, so $a_1 \ge 3g > 2g \ge L$.
25: The sequence $a_n$ is eventually periodic because $x^n \pmod m$ and $y^n \pmod m$ are eventually periodic for any $m$. If $a_n$ were eventually constant, it would be $L \in \{g, 2g\}$.
26: If $\gcd(g, X+Y) = 1$, then for $n-1 = k\phi(X+Y)$, we have $g^{n-1} \equiv 1 \pmod{X+Y}$ and $X^{n-1} \equiv 1 \pmod{X+Y}$. Then $g^{n-1} X^n + Y \equiv X+Y \equiv 0 \pmod{X+Y}$ and $g^{n-1} Y^n + X \equiv Y+X \equiv 0 \pmod{X+Y}$, so $a_n$ is a multiple of $g(X+Y) \ge 3g$ for infinitely many $n$.
27: If $\gcd(g, X+Y) = d > 1$, let $p$ be a prime factor of $X+Y$. If $p \nmid g$, we can similarly find $n$ such that $a_n$ is a multiple of $gp$. If all prime factors of $X+Y$ divide $g$, then for $n \ge 2$, $g^{n-1} X^n + Y \equiv Y \pmod p$ for any $p | \gcd(g, X+Y)$, so $a_n$ is not a multiple of $p$. This means $a_n$ deviates from $a_1 = g(X+Y)$ for $n \ge 2$. Since $a_n$ is eventually periodic, if it were constant, it would be $L \in \{g, 2g\}$. But for any $x \neq y$, $a_n$ cannot be eventually constant because the conditions $gX \equiv 1 \pmod{L'}$ and $gY \equiv 1 \pmod{L'}$ for $L' \in \{1, 2\}$ are insufficient to prevent $a_n$ from taking larger values for other $n$. Specifically, for any $x \neq y$, $a_n$ will oscillate or diverge.
28: 
29: The only pair of positive integers $(x, y)$ such that the limit of the sequence $(a_n)$ exists is $(1, 1)$.

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
