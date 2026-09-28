# Problem

For a real number $r$, let $A(r)$ denote the fractional part of $2r$ in its decimal representation. For a real number $r$ and a positive integer $n$, define $B(n,r)$ as
 $$
 B(n,r)=\sum_{k=1}^n A(kr).
 $$
 Find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$.

# Proof A

1: To find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$, where $B(n,r) = \sum_{k=1}^n A(kr)$ and $A(kr)$ denotes the fractional part of $2kr$, we proceed as follows.
2: 
3: Let $\{x\}$ denote the fractional part of $x$. Then $A(kr) = \{2kr\}$. By definition, $\{x\} = x - \lfloor x \rfloor$. We substitute this into the expression for $B(n,r)$:
4: $$ B(n,r) = \sum_{k=1}^n \{2kr\} = \sum_{k=1}^n (2kr - \lfloor 2kr \rfloor) = 2r \sum_{k=1}^n k - \sum_{k=1}^n \lfloor 2kr \rfloor = 2r \frac{n(n+1)}{2} - \sum_{k=1}^n \lfloor 2kr \rfloor. $$
5: Simplifying the first term, we have $B(n,r) = n(n+1)r - \sum_{k=1}^n \lfloor 2kr \rfloor$. The condition given in the problem is that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all $n \in \mathbb{Z}^+$. Substituting the simplified expression for $B(n,r)$:
6: $$ n(n+1)r - \left( n(n+1)r - \sum_{k=1}^n \lfloor 2kr \rfloor \right) = \sum_{k=1}^n \lfloor 2kr \rfloor. $$
7: Thus, the condition is that $S_n = \sum_{k=1}^n \lfloor 2kr \rfloor$ must be a multiple of $n$ for all $n \in \mathbb{Z}^+$. Let $x = 2r$. We seek all $x > 0$ such that $S_n = \sum_{k=1}^n \lfloor kx \rfloor \equiv 0 \pmod{n}$ for all $n \ge 1$.
8: 
9: If $x$ is an even integer, say $x = 2m$ for some $m \in \mathbb{Z}^+$, then
10: $$ S_n = \sum_{k=1}^n \lfloor 2km \rfloor = \sum_{k=1}^n 2km = 2m \frac{n(n+1)}{2} = mn(n+1). $$
11: Since $mn(n+1) = n \cdot (m(n+1))$ and $m(n+1)$ is an integer, $mn(n+1)$ is a multiple of $n$ for all $n$. This corresponds to $2r = 2m$, or $r = m$, where $m$ is a positive integer.
12: 
13: Now we show that no other $x > 0$ satisfies the condition. Let $\lfloor x \rfloor = a$ and $x = a + \delta$ with $0 \le \delta < 1$.
14: For $n=2$, $S_2 = \lfloor x \rfloor + \lfloor 2x \rfloor = a + \lfloor 2a + 2\delta \rfloor = 3a + \lfloor 2\delta \rfloor$. For $S_2$ to be even:
15: 1. If $\lfloor 2\delta \rfloor = 0$ (i.e., $0 \le \delta < 1/2$), then $3a$ must be even, so $a$ is even.
16: 2. If $\lfloor 2\delta \rfloor = 1$ (i.e., $1/2 \le \delta < 1$), then $3a$ must be odd, so $a$ is odd.
17: 
18: In Case 1 ($a$ even, $0 \le \delta < 1/2$), $S_n = a \frac{n(n+1)}{2} + \sum_{k=1}^n \lfloor k\delta \rfloor$. Since $a$ is even, $a \frac{n(n+1)}{2}$ is always a multiple of $n$. Thus, we require $\sum_{k=1}^n \lfloor k\delta \rfloor \equiv 0 \pmod{n}$ for all $n$. We prove $\lfloor n\delta \rfloor = 0$ for all $n \ge 1$ by induction. For $n=1$, $\lfloor \delta \rfloor = 0$ since $0 \le \delta < 1/2$. Assume $\lfloor k\delta \rfloor = 0$ for all $k < n$. Then $\sum_{k=1}^n \lfloor k\delta \rfloor = \sum_{k=1}^{n-1} 0 + \lfloor n\delta \rfloor = \lfloor n\delta \rfloor$. For this to be a multiple of $n$, we must have $\lfloor n\delta \rfloor = qn$ for some integer $q$. Since $0 \le \delta < 1/2$, we have $0 \le n\delta < n/2$, so $0 \le \lfloor n\delta \rfloor < n/2$. The only multiple of $n$ in this range is 0, so $\lfloor n\delta \rfloor = 0$. Since $\lfloor n\delta \rfloor = 0$ for all $n \ge 1$, we have $n\delta < 1$ for all $n \ge 1$, which implies $\delta = 0$. This implies $x = a$, an even integer.
19: 
20: In Case 2 ($a$ odd, $1/2 \le \delta < 1$), we prove $\lfloor n\delta \rfloor = n-1$ for all $n \ge 1$ by induction. For $n=1$, $\lfloor \delta \rfloor = 0 = 1-1$. For $n=2$, $S_2 = 3a + 0 + \lfloor 2\delta \rfloor \equiv 1 + \lfloor 2\delta \rfloor \equiv 0 \pmod{2}$ (since $a$ is odd), so $\lfloor 2\delta \rfloor = 1 = 2-1$. Assume $\lfloor k\delta \rfloor = k-1$ for all $k < n$. Then $\sum_{k=1}^{n-1} \lfloor k\delta \rfloor = \sum_{k=1}^{n-1} (k-1) = \frac{(n-2)(n-1)}{2}$. The condition $S_n \equiv 0 \pmod{n}$ becomes $a \frac{n(n+1)}{2} + \frac{(n-2)(n-1)}{2} + \lfloor n\delta \rfloor \equiv 0 \pmod{n}$. Since $a$ is odd, $a = 2m+1$, so $a \frac{n(n+1)}{2} = mn(n+1) + \frac{n(n+1)}{2} \equiv \frac{n(n+1)}{2} \pmod{n}$. Thus, $\frac{n(n+1)}{2} + \frac{n^2-3n+2}{2} + \lfloor n\delta \rfloor = \frac{2n^2-2n+2}{2} + \lfloor n\delta \rfloor = n^2-n+1 + \lfloor n\delta \rfloor \equiv 1 + \lfloor n\delta \rfloor \equiv 0 \pmod{n}$. Since $0 \le \delta < 1$, we have $0 \le \lfloor n\delta \rfloor \le n-1$, so $\lfloor n\delta \rfloor = n-1$. This implies $n-1 \le n\delta < n$, or $1 - 1/n \le \delta < 1$ for all $n \in \mathbb{Z}^+$. As $n \to \infty$, we obtain $1 \le \delta < 1$, a contradiction.
21: 
22: Thus, $x$ must be an even integer, which implies $r$ must be a positive integer.
23: 
24: The positive real numbers $r$ are all positive integers. \(\square\)

# Proof B

1: Let $\{y\} = y - \lfloor y \rfloor$ denote the fractional part of a real number $y$. The problem defines $A(r) = \{2r\}$. For a positive integer $n$, we have
2: $$B(n,r) = \sum_{k=1}^n A(kr) = \sum_{k=1}^n \{2kr\} = \sum_{k=1}^n (2kr - \lfloor 2kr \rfloor).$$
3: We are given that $C(n,r) = n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$. Substituting the expression for $B(n,r)$:
4: $$C(n,r) = n(n+1)r - \left( 2r \sum_{k=1}^n k - \sum_{k=1}^n \lfloor 2kr \rfloor \right) = n(n+1)r - 2r \frac{n(n+1)}{2} + \sum_{k=1}^n \lfloor 2kr \rfloor = \sum_{k=1}^n \lfloor 2kr \rfloor.$$
5: The condition is that $S_n = \sum_{k=1}^n \lfloor 2kr \rfloor$ is a multiple of $n$ for all $n \in \mathbb{Z}^+$. Let $x = 2r$. The condition is $S_n = \sum_{k=1}^n \lfloor kx \rfloor \equiv 0 \pmod n$.
6: Let $x = m + \alpha$, where $m = \lfloor x \rfloor$ is a non-negative integer and $0 \le \alpha < 1$. Then
7: $$S_n = \sum_{k=1}^n \lfloor k(m+\alpha) \rfloor = \sum_{k=1}^n (km + \lfloor k\alpha \rfloor) = m \frac{n(n+1)}{2} + \sum_{k=1}^n \lfloor k\alpha \rfloor.$$
8: For any odd integer $n$, $n+1$ is even, so $m \frac{n(n+1)}{2} = n \cdot \frac{m(n+1)}{2}$ is a multiple of $n$. Thus, for odd $n$, the condition $S_n \equiv 0 \pmod n$ reduces to
9: $$\sum_{k=1}^n \lfloor k\alpha \rfloor \equiv 0 \pmod n.$$
10: Let $a_n = \frac{1}{n} \sum_{k=1}^n \lfloor k\alpha \rfloor$. For all odd $n$, $a_n$ must be an integer. We examine the difference $a_{n+2} - a_n$ for odd $n$:
11: $$a_n = \frac{1}{n} \sum_{k=1}^n (k\alpha - \{k\alpha\}) = \alpha \frac{n+1}{2} - \frac{1}{n} \sum_{k=1}^n \{k\alpha\}.$$
12: Let $E_n = \frac{1}{n} \sum_{k=1}^n \{k\alpha\}$. Then $a_n = \alpha \frac{n+1}{2} - E_n$. The difference is
13: $$a_{n+2} - a_n = \left( \alpha \frac{n+3}{2} - E_{n+2} \right) - \left( \alpha \frac{n+1}{2} - E_n \right) = \alpha - (E_{n+2} - E_n).$$
14: We analyze $E_{n+2} - E_n$:
15: $$E_{n+2} - E_n = \frac{\sum_{k=1}^{n+2} \{k\alpha\}}{n+2} - \frac{\sum_{k=1}^n \{k\alpha\}}{n} = \frac{n \sum_{k=1}^{n+2} \{k\alpha\} - (n+2) \sum_{k=1}^n \{k\alpha\}}{n(n+2)} = \frac{n(\{ (n+1)\alpha \} + \{ (n+2)\alpha \}) - 2 \sum_{k=1}^n \{k\alpha\}}{n(n+2)}.$$
16: Since $0 \le \{y\} < 1$, the numerator is bounded:
17: $$|n(\{ (n+1)\alpha \} + \{ (n+2)\alpha \}) - 2 \sum_{k=1}^n \{k\alpha\}| < 2n + 2n = 4n.$$
18: Thus, $|E_{n+2} - E_n| < \frac{4n}{n(n+2)} = \frac{4}{n+2}$. As $n \to \infty$, $E_{n+2} - E_n \to 0$.
19: Since $a_n$ is an integer for all odd $n$, $a_{n+2} - a_n$ is an integer for all odd $n$. A sequence of integers that converges must be eventually constant. Therefore, $\lim_{n \to \infty} (a_{n+2} - a_n) = \alpha$ must be an integer. Given $0 \le \alpha < 1$, we must have $\alpha = 0$.
20: 
21: Consequently, $x = 2r = m$ is an integer. The original condition $S_n \equiv 0 \pmod n$ becomes
22: $$m \frac{n(n+1)}{2} \equiv 0 \pmod n \implies \frac{m(n+1)}{2} \in \mathbb{Z} \text{ for all } n \in \mathbb{Z}^+.$$
23: For $n=2$, we have $\frac{3m}{2} \in \mathbb{Z}$, which implies $m$ must be even. Let $m = 2k$ for some positive integer $k$ (since $r > 0$). Then $\frac{2k(n+1)}{2} = k(n+1)$, which is always an integer for any $n$.
24: Since $2r = m = 2k$, we have $r = k$. Thus, $r$ must be a positive integer.
25: Testing $r=k \in \mathbb{Z}^+$, we find $C(n,k) = \sum_{j=1}^n \lfloor 2jk \rfloor = 2k \frac{n(n+1)}{2} = kn(n+1)$, which is a multiple of $n$ for all $n$.
26: 
27: The positive real numbers $r$ are all positive integers.
