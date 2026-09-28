# Problem

For a real number $r$, let $A(r)$ denote the fractional part of $2r$ in its decimal representation. For a real number $r$ and a positive integer $n$, define $B(n,r)$ as
 $$
 B(n,r)=\sum_{k=1}^n A(kr).
 $$
 Find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$.

# Proof A

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

# Proof B

1: To find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$, we first analyze the definition of $B(n,r)$.
2: 
3: The fractional part of a real number $x$ is denoted by $\{x\} = x - \lfloor x \rfloor$. The problem defines $A(r) = \{2r\}$. Thus, for a positive integer $n$, we have:
4: $$B(n,r) = \sum_{k=1}^n A(kr) = \sum_{k=1}^n \{2kr\} = \sum_{k=1}^n (2kr - \lfloor 2kr \rfloor)$$
5: Using the identity $\sum_{k=1}^n k = \frac{n(n+1)}{2}$, we can simplify $B(n,r)$:
6: $$B(n,r) = 2r \frac{n(n+1)}{2} - \sum_{k=1}^n \lfloor 2kr \rfloor = n(n+1)r - \sum_{k=1}^n \lfloor 2kr \rfloor$$
7: The condition given in the problem is that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all $n \in \mathbb{Z}^+$. Substituting the expression for $B(n,r)$, we get:
8: $$n(n+1)r - \left( n(n+1)r - \sum_{k=1}^n \lfloor 2kr \rfloor \right) = \sum_{k=1}^n \lfloor 2kr \rfloor$$
9: Let $S_n = \sum_{k=1}^n \lfloor 2kr \rfloor$. The condition is that $S_n \equiv 0 \pmod n$ for all $n \ge 1$.
10: Let $x = 2r$. We seek all $x > 0$ such that $\sum_{k=1}^n \lfloor kx \rfloor$ is a multiple of $n$ for all $n \ge 1$.
11: 
12: Case 1: $x$ is an integer.
13: If $x \in \mathbb{Z}^+$, then $\sum_{k=1}^n \lfloor kx \rfloor = \sum_{k=1}^n kx = x \frac{n(n+1)}{2}$.
14: For this to be a multiple of $n$, the value $\frac{x(n+1)}{2}$ must be an integer for all $n \ge 1$.
15: For $n=1$, $\frac{2x}{2} = x$ is an integer (which we assumed).
16: For $n=2$, $\frac{3x}{2}$ must be an integer, which implies $x$ must be even.
17: If $x = 2m$ for some $m \in \mathbb{Z}^+$, then $\frac{2m(n+1)}{2} = m(n+1)$, which is always an integer for all $n$.
18: Thus, $x$ must be an even integer, meaning $2r = 2m \implies r = m$ for some $m \in \mathbb{Z}^+$.
19: 
20: Case 2: $x$ is not an integer.
21: Let $x = I + f$, where $I = \lfloor x \rfloor$ and $0 < f < 1$. Then:
22: $$S_n = \sum_{k=1}^n \lfloor k(I+f) \rfloor = I \frac{n(n+1)}{2} + \sum_{k=1}^n \lfloor kf \rfloor$$
23: For any odd integer $n$, $I \frac{n(n+1)}{2} = n \cdot I \frac{n+1}{2}$, which is a multiple of $n$. Thus, we must have $T_n = \sum_{k=1}^n \lfloor kf \rfloor \equiv 0 \pmod n$ for all odd $n \ge 1$.
24: For $n=1$, $T_1 = \lfloor f \rfloor = 0$, which is always true for $0 < f < 1$.
25: For $n=3$, $T_3 = \lfloor 2f \rfloor + \lfloor 3f \rfloor \equiv 0 \pmod 3$. Since $0 \le \lfloor 2f \rfloor \le 1$ and $0 \le \lfloor 3f \rfloor \le 2$, the only possibilities are:
26: (i) $\lfloor 2f \rfloor = 0$ and $\lfloor 3f \rfloor = 0$, implying $f < 1/3$.
27: (ii) $\lfloor 2f \rfloor = 1$ and $\lfloor 3f \rfloor = 2$, implying $f \ge 2/3$.
28: 
29: In subcase (i), if $f < 1/3$, then for $n=5$, $T_5 = 0 + 0 + \lfloor 4f \rfloor + \lfloor 5f \rfloor \equiv 0 \pmod 5$. Since $f < 1/3$, we have $0 \le \lfloor 4f \rfloor \le 1$ and $0 \le \lfloor 5f \rfloor \le 1$. Their sum is at most 2, so we must have $\lfloor 4f \rfloor = 0$ and $\lfloor 5f \rfloor = 0$, implying $f < 1/5$. By induction, $\lfloor nf \rfloor = 0$ for all odd $n$, which implies $f=0$, a contradiction.
30: 
31: In subcase (ii), if $f \ge 2/3$, then for $n=5$, $T_5 = 1 + 2 + \lfloor 4f \rfloor + \lfloor 5f \rfloor = 3 + \lfloor 4f \rfloor + \lfloor 5f \rfloor \equiv 0 \pmod 5$. Given $f \in [2/3, 1)$, $\lfloor 4f \rfloor \in \{2, 3\}$ and $\lfloor 5f \rfloor \in \{3, 4\}$. The only combination that sums to a multiple of 5 is $\lfloor 4f \rfloor = 3$ and $\lfloor 5f \rfloor = 4$, implying $f \ge 4/5$. For $n=7$, $T_7 = 0+1+2+3+4 + \lfloor 6f \rfloor + \lfloor 7f \rfloor = 10 + \lfloor 6f \rfloor + \lfloor 7f \rfloor \equiv 0 \pmod 7$. Given $f \in [4/5, 1)$, $\lfloor 6f \rfloor \in \{4, 5\}$ and $\lfloor 7f \rfloor \in \{5, 6\}$. The only combination that sums to a multiple of 7 is $\lfloor 6f \rfloor = 5$ and $\lfloor 7f \rfloor = 6$, implying $f \ge 6/7$. By induction, we must have $\lfloor nf \rfloor = n-1$ for all $n \ge 2$, which implies $f \ge 1 - 1/n$ for all $n \in \mathbb{Z}^+$. Taking the limit as $n \to \infty$, we obtain $f \ge 1$, a contradiction.
32: 
33: Thus, the only solutions are the positive integers $r$.
34: 
35: The positive real numbers $r$ are all positive integers $r \in \{1, 2, 3, \dots\}$.
36: 
37: \(\square\)
