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
