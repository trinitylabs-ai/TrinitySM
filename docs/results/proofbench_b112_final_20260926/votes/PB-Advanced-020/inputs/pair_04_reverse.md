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
