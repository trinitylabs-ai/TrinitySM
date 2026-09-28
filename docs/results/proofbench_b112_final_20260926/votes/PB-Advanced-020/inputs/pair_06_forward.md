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
