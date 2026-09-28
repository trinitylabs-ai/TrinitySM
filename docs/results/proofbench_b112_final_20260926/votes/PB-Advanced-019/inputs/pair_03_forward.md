# Problem

For a real number $r$, let $A(r)$ denote the fractional part of $2r$ in its decimal representation. For a real number $r$ and a positive integer $n$, define $B(n,r)$ as
 $$
 B(n,r)=\sum_{k=1}^n A(kr).
 $$
 Find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$.

# Proof A

1: To find all positive real numbers $r$ such that $n(n+1)r - B(n, r)$ is a multiple of $n$ for all positive integers $n$, where $A(r)$ is the fractional part of $2r$ and $B(n, r) = \sum_{k=1}^n A(kr)$, we begin by simplifying the given expression.
2: 
3: Let $S_n = n(n+1)r - B(n, r)$. By definition, $A(kr) = \{2kr\}$, where $\{x\} = x - \lfloor x \rfloor$ denotes the fractional part of $x$. Thus:
4: \[ S_n = n(n+1)r - \sum_{k=1}^n \{2kr\} = n(n+1)r - \sum_{k=1}^n (2kr - \lfloor 2kr \rfloor) \]
5: \[ S_n = n(n+1)r - 2r \frac{n(n+1)}{2} + \sum_{k=1}^n \lfloor 2kr \rfloor = \sum_{k=1}^n \lfloor 2kr \rfloor \]
6: The condition is that $S_n = \sum_{k=1}^n \lfloor 2kr \rfloor$ must be a multiple of $n$ for all $n \in \mathbb{Z}^+$. Let $m_n = S_n/n$. We require $m_n \in \mathbb{Z}$ for all $n \ge 1$.
7: 
8: Let $2r = I + f$, where $I = \lfloor 2r \rfloor$ is an integer and $0 \le f < 1$. Then:
9: \[ S_n = \sum_{k=1}^n \lfloor k(I+f) \rfloor = \sum_{k=1}^n (kI + \lfloor kf \rfloor) = I \frac{n(n+1)}{2} + \sum_{k=1}^n \lfloor kf \rfloor \]
10: The condition $m_n \in \mathbb{Z}$ becomes:
11: \[ m_n = \frac{I(n+1)}{2} + \frac{1}{n} \sum_{k=1}^n \lfloor kf \rfloor \in \mathbb{Z} \quad \text{for all } n \ge 1. \]
12: 
13: Case 1: $I$ is even. Let $I = 2m$ for some integer $m$.
14: Then $m_n = m(n+1) + \frac{1}{n} \sum_{k=1}^n \lfloor kf \rfloor$. This requires $T_n = \sum_{k=1}^n \lfloor kf \rfloor$ to be a multiple of $n$ for all $n \ge 1$.
15: For $n=1$, $T_1 = \lfloor f \rfloor = 0$.
16: For $n=2$, $T_2 = \lfloor f \rfloor + \lfloor 2f \rfloor = \lfloor 2f \rfloor$. For $T_2$ to be a multiple of 2, since $0 \le 2f < 2$, we must have $\lfloor 2f \rfloor = 0$.
17: By induction, if $\lfloor kf \rfloor = 0$ for all $k < n$, then $T_n = \lfloor nf \rfloor$. For $T_n$ to be a multiple of $n$, we must have $\lfloor nf \rfloor = 0$ for all $n \ge 1$. This implies $nf < 1$ for all $n$, which is only possible if $f = 0$.
18: Thus, $2r = I = 2m$, so $r = m \in \mathbb{Z}^+$.
19: 
20: Case 2: $I$ is odd. Let $I = 2m + 1$ for some integer $m$.
21: Then $m_n = \frac{(2m+1)(n+1)}{2} + \frac{T_n}{n} = m(n+1) + \frac{n+1}{2} + \frac{T_n}{n}$.
22: This requires $C_n = \frac{n+1}{2} + \frac{T_n}{n} \in \mathbb{Z}$ for all $n \ge 1$.
23: From this, we have $T_n = n C_n - \frac{n(n+1)}{2}$.
24: Since $T_n - T_{n-1} = \lfloor nf \rfloor$, we have:
25: \[ \lfloor nf \rfloor = n C_n - \frac{n(n+1)}{2} - \left( (n-1) C_{n-1} - \frac{(n-1)n}{2} \right) = n C_n - (n-1) C_{n-1} - n \]
26: Since $0 \le f < 1$, we must have $0 \le \lfloor nf \rfloor \le n-1$. Thus:
27: \[ n \le n C_n - (n-1) C_{n-1} \le 2n-1 \]
28: For $n=1$, $C_1 = \frac{1+1}{2} + \frac{0}{1} = 1$.
29: For $n=2$, $2 \le 2 C_2 - 1 \le 3 \implies 3 \le 2 C_2 \le 4 \implies C_2 = 2$.
30: We proceed by induction to show $C_n = n$ for all $n \ge 1$. Assume $C_{n-1} = n-1$. Then:
31: \[ n \le n C_n - (n-1)^2 \le 2n-1 \]
32: \[ n + n^2 - 2n + 1 \le n C_n \le 2n-1 + n^2 - 2n + 1 \]
33: \[ n^2 - n + 1 \le n C_n \le n^2 \]
34: Dividing by $n$, we get $n - 1 + \frac{1}{n} \le C_n \le n$. Since $C_n$ is an integer, we must have $C_n = n$.
35: Substituting $C_n = n$ back into the expression for $\lfloor nf \rfloor$:
36: \[ \lfloor nf \rfloor = n(n) - (n-1)(n-1) - n = n^2 - (n^2 - 2n + 1) - n = n - 1 \]
37: This implies $n-1 \le nf < n$, which means $1 - \frac{1}{n} \le f < 1$ for all $n \ge 1$.
38: Taking the limit as $n \to \infty$, we find $f \ge 1$, which contradicts the assumption $f < 1$.
39: Thus, Case 2 yields no solutions.
40: 
41: The only solutions are positive integers $r$.
42: 
43: The positive real numbers $r$ are $r \in \{1, 2, 3, \dots\}$.
44: 
45: \(\square\)

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
