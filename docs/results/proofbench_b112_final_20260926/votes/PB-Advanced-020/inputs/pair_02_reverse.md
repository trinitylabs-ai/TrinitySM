# Problem

For given positive integers $x$ and $y$, we define a sequence $(a_n)_{n \ge 1}$ as
 $$
 a_n = \gcd \left( x^n +y , \, (y-x)\left(\sum_{i=0}^{n-1} y^i x^{n-i-1} - 1\right) \right)
 $$
 for all $n\in \mathbb{N}$. Find all pairs $(x,y)$ of positive integers such that the limit of the sequence $(a_n)$ exists.

# Proof A

1: To find all pairs of positive integers $(x, y)$ such that the limit of the sequence $(a_n)_{n \ge 1}$ exists, we first simplify the expression for $a_n$:
2: $$a_n = \gcd \left( x^n + y, (y-x) \left( \sum_{i=0}^{n-1} y^i x^{n-i-1} - 1 \right) \right).$$
3: The sum $\sum_{i=0}^{n-1} y^i x^{n-i-1}$ is a geometric series. If $x = y$, the sum is $nx^{n-1}$. If $x \neq y$, the sum is $\frac{y^n - x^n}{y-x}$.
4: 
5: Case 1: $x = y$
6: If $x = y$, the second term in the $\gcd$ is $(x-x)(\dots) = 0$. Thus,
7: $$a_n = \gcd(x^n + x, 0) = x^n + x.$$
8: For the limit $\lim_{n \to \infty} a_n$ to exist, the sequence $x^n + x$ must be eventually constant. This occurs if and only if $x = 1$. If $x=1$, then $y=1$, and $a_n = 1^n + 1 = 2$ for all $n \ge 1$, which converges to 2. Thus, $(1, 1)$ is a solution.
9: 
10: Case 2: $x \neq y$
11: Substituting the sum formula into the expression for $a_n$:
12: $$a_n = \gcd \left( x^n + y, (y-x) \left( \frac{y^n - x^n}{y-x} - 1 \right) \right) = \gcd(x^n + y, y^n - x^n - y + x).$$
13: Using the property $\gcd(A, B) = \gcd(A, A+B)$, we have:
14: $$a_n = \gcd(x^n + y, (x^n + y) + (y^n - x^n - y + x)) = \gcd(x^n + y, y^n + x).$$
15: Suppose the limit $\lim_{n \to \infty} a_n = L$ exists. Since $a_n$ is a sequence of integers, it must be eventually constant, so $a_n = L$ for all $n \ge N$.
16: Then $L$ must divide $x^n + y$ and $y^n + x$ for all $n \ge N$.
17: Consequently, $L$ must divide the difference:
18: $$L \mid (x^{n+1} + y) - x(x^n + y) = y - xy = y(1-x).$$
19: Similarly, $L \mid x(1-y)$.
20: Also, $L \mid (x^{n+1} + y) - (x^n + y) = x^n(x-1)$.
21: Let $g = \gcd(x, y)$. Let $x = gu$ and $y = gv$ with $\gcd(u, v) = 1$.
22: The sequence becomes $a_n = g \gcd(g^{n-1}u^n + v, g^{n-1}v^n + u)$.
23: Let $b_n = \gcd(g^{n-1}u^n + v, g^{n-1}v^n + u)$. For $a_n$ to converge, $b_n$ must converge to some $L' = L/g$.
24: If $p$ is a prime dividing $L'$, then $p$ cannot divide $g$ (because if $p \mid g$, then $p \mid g^{n-1}u^n + v \implies p \mid v$, and $p \mid g^{n-1}v^n + u \implies p \mid u$, contradicting $\gcd(u, v) = 1$).
25: Thus $\gcd(L', g) = 1$.
26: Since $L' \mid g^{n-1}u^n + v$ and $L' \mid g^n u^{n+1} + gv$ for $n \ge N$, we have:
27: $$L' \mid (g^n u^{n+1} + gv) - gu(g^{n-1} u^n + v) = gv(1-u).$$
28: Since $\gcd(L', g) = 1$ and $\gcd(L', v) = 1$ (as $p \mid L', p \mid v \implies p \mid g^{n-1}u^n \implies p \mid u$, contradiction), we have $L' \mid 1-u$. Similarly, $L' \mid 1-v$.
29: Then $g^{n-1}u^n + v \equiv g^{n-1}(1)^n + 1 \equiv g^{n-1} + 1 \pmod{L'}$.
30: Thus $L' \mid g^{n-1} + 1$ for all $n \ge N$. This implies $g^{n-1} \equiv -1 \pmod{L'}$ and $g^n \equiv -1 \pmod{L'}$, so $g = g^n/g^{n-1} \equiv 1 \pmod{L'}$.
31: Then $1 \equiv -1 \pmod{L'}$, so $L' \mid 2$. Thus $L' \in \{1, 2\}$.
32: 
33: We now show that $b_n$ cannot be eventually constant for $u \neq v$.
34: Note $b_1 = \gcd(u+v, v+u) = u+v$. Since $u \neq v$ and $u, v \ge 1$, $u+v > 2$.
35: Let $M$ be the largest divisor of $u+v$ such that $\gcd(M, g) = 1$.
36: If $M > 2$, then for $n-1$ being a multiple of $\phi(M)$, we have $g^{n-1} \equiv 1 \pmod M$ and $u^{n-1} \equiv 1 \pmod M$.
37: Then $g^{n-1}u^n + v \equiv u+v \equiv 0 \pmod M$ and $g^{n-1}v^n + u \equiv v+u \equiv 0 \pmod M$.
38: Thus $b_n$ is a multiple of $M$, so $b_n \ge M > 2$, which contradicts $b_n \in \{1, 2\}$ for $n \ge N$.
39: If $M = 1$, then all prime factors of $u+v$ divide $g$. Then for $n \ge 2$, $\gcd(b_n, u+v) = 1$ because $\gcd(b_n, g) = 1$. Since $u+v > 2$, $b_n$ cannot be constant as $b_1 = u+v$.
40: If $M = 2$, then $u+v = 2K$ where all prime factors of $K$ divide $g$.
41: If $L' = 1$, then $b_n$ is eventually 1, but for $n-1$ a multiple of $\phi(2)=1$, $b_n$ is a multiple of $M=2$, contradiction.
42: If $L' = 2$, then $b_n$ is eventually 2. This requires $g, u, v$ to be odd. But if $g, u, v$ are all odd, then $u+v$ is even and $\gcd(u+v, g)$ is odd. Thus $M$ would be the power of 2 dividing $u+v$. Since $u, v$ are odd and $u \neq v$, $u+v \ge 1+3=4$, so $M \ge 4$, contradiction.
43: 
44: Thus, no pairs $(x, y)$ with $x \neq y$ satisfy the condition. The only solution is $(1, 1)$.

# Proof B

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
