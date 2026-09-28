# Problem

Let $n$ be a positive integer that has a remainder of 6 when divided by 7. Let $d$ be any divisor of $n$.

Define $c$ such that when the expression $\left(d+\frac{n}{d}\right)^{2}$ is divided by $n$, the remainder is $n-c$.

What is the smallest possible value of $c$ among all $d$ and $n$ satisfying the conditions above?

(Note that the remainder when a positive integer $a$ is divided by a positive integer $b$ is the value of $r$ in the expression $a=b q+r, 0 \leq r \leq b-1$.)

# Proof A

1: Let $n$ be a positive integer such that $n \equiv 6 \pmod{7}$, and let $d$ be a divisor of $n$. Let $k = n/d$. The expression given is $(d + k)^2 = d^2 + 2n + k^2$. When this is divided by $n$, the remainder is the same as the remainder of $d^2 + k^2$ divided by $n$. We are given that this remainder is $n-c$, where $0 \le n-c \le n-1$. This implies $1 \le c \le n$ and
2: $$d^2 + k^2 \equiv n-c \equiv -c \pmod{n}.$$
3: Thus, $n$ must divide $d^2 + k^2 + c$. Since $n=dk$, there exists a positive integer $m$ such that
4: $$d^2 + k^2 + c = mdk.$$
5: We want to find the smallest positive integer $c$ for which there exist positive integers $d, k$ such that $dk \equiv 6 \pmod{7}$ and $d^2 + k^2 + c = mdk$.
6: 
7: For a fixed $m$ and $c$, let $(d, k)$ be a solution to $d^2 + k^2 + c = mdk$ with $d \le k$. If $d < k$, the equation $x^2 - (md)x + (d^2+c) = 0$ has roots $k$ and $k' = md-k = \frac{d^2+c}{k}$. Since $d, k, m, c$ are positive integers, $k'$ is also a positive integer. If we choose a solution $(d, k)$ such that $d+k$ is minimal, we must have $k' \ge k$, which implies $\frac{d^2+c}{k} \ge k$, or $d^2+c \ge k^2$. Since $d \le k$, this means $k^2 - d^2 \le c$.
8: 
9: Case $c=1$:
10: The condition $k^2 - d^2 \le 1$ with $d \le k$ implies either $d=k$ or $k^2-d^2=1$. If $d=k$, then $2d^2+1=md^2$, which implies $(m-2)d^2=1$, so $d=1$ and $m=3$. If $k^2-d^2=1$, then $(k-d)(k+d)=1$, which has no solutions in positive integers. Thus, $m=3$ is the only possibility.
11: For $m=3$, the solutions $(d_i, d_{i+1})$ satisfy $d_{i+1} = 3d_i - d_{i-1}$ with $d_1=1, d_2=1$. The sequence modulo 7 is $1, 1, 2, 5, 6, 6, 5, 2, 1, 1, \dots$. The possible values of $n = d_i d_{i+1} \pmod{7}$ are $1\cdot 1=1, 1\cdot 2=2, 2\cdot 5 \equiv 3, 5\cdot 6 \equiv 2, 6\cdot 6 \equiv 1, 6\cdot 5 \equiv 2, 5\cdot 2 \equiv 3, 2\cdot 1=2$. None are $6 \pmod{7}$.
12: 
13: Case $c=2$:
14: The condition $k^2 - d^2 \le 2$ with $d \le k$ implies $d=k$ or $k^2-d^2 \in \{1, 2\}$. If $d=k$, then $2d^2+2=md^2$, so $(m-2)d^2=2$, which implies $d=1$ and $m=4$. If $k^2-d^2=1$ or $2$, there are no positive integer solutions since $k+d \ge 3$. Thus, $m=4$ is the only possibility.
15: For $m=4$, the solutions satisfy $d_{i+1} = 4d_i - d_{i-1}$ with $d_1=1, d_2=1$. The sequence modulo 7 is $1, 1, 3, 4, 6, 6, 4, 3, 1, 1, \dots$. The possible values of $n = d_i d_{i+1} \pmod{7}$ are $1\cdot 1=1, 1\cdot 3=3, 3\cdot 4 \equiv 5, 4\cdot 6 \equiv 3, 6\cdot 6 \equiv 1, 6\cdot 4 \equiv 3, 4\cdot 3 \equiv 5, 3\cdot 1=3$. None are $6 \pmod{7}$.
16: 
17: Case $c=3$:
18: The condition $k^2 - d^2 \le 3$ with $d \le k$ implies $d=k$ or $k^2-d^2 \in \{1, 2, 3\}$. If $d=k$, then $2d^2+3=md^2$, so $(m-2)d^2=3$, which implies $d=1$ and $m=5$. If $k^2-d^2=3$, then $(k-d)(k+d)=3$, so $k-d=1$ and $k+d=3$, giving $k=2, d=1$. Then $1^2+2^2+3=m(1)(2)$, so $8=2m$, which means $m=4$.
19: 
20: For $m=5$, the solutions satisfy $d_{i+1} = 5d_i - d_{i-1}$ with $d_1=1, d_2=1$. The sequence is $d_1=1, d_2=1, d_3=4, d_4=19, \dots$.
21: Testing $n = d_3 d_4 = 4 \cdot 19 = 76$:
22: $76 = 7 \times 10 + 6 \equiv 6 \pmod{7}$.
23: For $n=76$ and $d=4$, we have $(4 + 19)^2 = 23^2 = 529$.
24: Dividing 529 by 76: $529 = 6 \times 76 + 73$.
25: The remainder is $73 = 76 - 3$, so $c=3$.
26: 
27: For $m=4$, the solutions for $c=3$ satisfy $d_{i+1} = 4d_i - d_{i-1}$ with $d_1=1, d_2=2$. The sequence modulo 7 is $1, 2, 0, 5, 6, 5, 0, 2, 1, 2, \dots$. The possible values of $n = d_i d_{i+1} \pmod{7}$ are $1\cdot 2=2, 2\cdot 0=0, 0\cdot 5=0, 5\cdot 6 \equiv 2, 6\cdot 5 \equiv 2, 5\cdot 0=0, 0\cdot 2=0, 2\cdot 1=2$. None are $6 \pmod{7}$.
28: 
29: Since $c=1$ and $c=2$ are impossible and $c=3$ is achievable, the smallest possible value of $c$ is 3.

# Proof B

1: To find the smallest possible value of $c$, we begin by analyzing the given expression. Let $n$ be a positive integer such that $n \equiv 6 \pmod{7}$, and let $d$ be any divisor of $n$. Let $k = \frac{n}{d}$, so that $n = dk$. The expression is:
2: \[ \left(d + \frac{n}{d}\right)^2 = (d+k)^2 = d^2 + 2dk + k^2 = d^2 + 2n + k^2 \]
3: The remainder when this expression is divided by $n$ is the same as the remainder when $d^2 + k^2$ is divided by $n$. Let this remainder be $R$. According to the problem, $R = n-c$. By the definition of the remainder, we have $0 \le n-c < n$, which implies $0 < c \le n$. We can write the condition $R = n-c$ as:
4: \[ d^2 + k^2 \equiv n-c \equiv -c \pmod{n} \]
5: This means that $n$ must divide $d^2 + k^2 + c$. Since $n = dk$, we have:
6: \[ d^2 + k^2 + c = mdk \]
7: for some positive integer $m$. Rearranging this gives the quadratic equation:
8: \[ d^2 - mdk + k^2 + c = 0 \]
9: We wish to find the smallest positive integer $c$ such that there exist $m, d, k$ satisfying this equation and the condition $dk \equiv 6 \pmod{7}$. For a fixed $m$ and $c$, let $(d, k)$ be a solution with $d \le k$. We can use the method of Vieta jumping to analyze the solutions. Consider the quadratic $f(x) = x^2 - mdx + d^2 + c = 0$. One root is $k$, and the other root is $k' = md - k = \frac{d^2+c}{k}$. If $k > d$, we can generate a sequence of smaller solutions $(d, k')$ until the descent stops. The descent stops when $k' \ge k$, which occurs if and only if $\frac{d^2+c}{k} \ge k$, or $k^2 \le d^2+c$.
10: 
11: We test small values of $c$:
12: 1. If $c=1$, the descent stops when $k^2 \le d^2+1$. Since $k \ge d$, this implies $k=d$ (as $k > d \implies k^2 \ge (d+1)^2 = d^2+2d+1 > d^2+1$). If $k=d$, then $(m-2)d^2 = 1$, which forces $d=1$ and $m=3$. For $m=3, c=1$, the solutions $(d, k)$ are pairs of consecutive odd-indexed Fibonacci numbers $(F_{2j-1}, F_{2j+1})$, as they satisfy $F_{2j+1} = 3F_{2j-1} - F_{2j-3}$ and $F_1^2 - 3F_1F_3 + F_3^2 + 1 = 1 - 3(1)(2) + 4 + 1 = 0$. The odd-indexed Fibonacci numbers modulo 7 are $1, 2, 5, 6, 6, 5, 2, 1, \dots$ (period 8). The products $n = F_{2j-1}F_{2j+1} \pmod{7}$ are $1\times 2=2, 2\times 5=3, 5\times 6=2, 6\times 6=1, 6\times 5=2, 5\times 2=3, 2\times 1=2, 1\times 1=1$. None of these equal 6.
13: 
14: 2. If $c=2$, the descent stops when $k^2 \le d^2+2$. If $k=d$, then $(m-2)d^2 = 2$, which forces $d=1$ and $m=4$. If $k=d+1$, then $(d+1)^2 \le d^2+2 \implies 2d+1 \le 2 \implies d=0$, which is not possible. Thus, $m=4$ is the only case. The solutions $x_j$ follow $x_{j+1} = 4x_j - x_{j-1}$ with $x_0=1, x_1=3$. The sequence modulo 7 is $1, 3, 4, 6, 6, 4, 3, 1, \dots$. The products $n = x_j x_{j+1} \pmod{7}$ are $1\times 3=3, 3\times 4=5, 4\times 6=3, 6\times 6=1, 6\times 4=3, 4\times 3=5, 3\times 1=3, 1\times 1=1$. None of these equal 6.
15: 
16: 3. If $c=3$, the descent stops when $k^2 \le d^2+3$. If $k=d$, then $(m-2)d^2 = 3$, which forces $d=1$ and $m=5$. If $k=d+1$, then $(d+1)^2 \le d^2+3 \implies 2d+1 \le 3 \implies d=1$. For $d=1, k=2$, we have $1 - 2m + 4 + 3 = 0 \implies 2m = 8 \implies m=4$.
17: If $m=5$, the solutions $x_j$ follow $x_{j+1} = 5x_j - x_{j-1}$ with $x_0=1, x_1=4$. The next term is $x_2 = 5(4) - 1 = 19$.
18: Checking $n = x_1 x_2 = 4 \times 19 = 76$:
19: - $76 = 7 \times 10 + 6$, so $n \equiv 6 \pmod{7}$.
20: - For $d=4, k=19$, $(d+k)^2 = 23^2 = 529$.
21: - $529 = 6 \times 76 + 73$.
22: - The remainder is $R=73$.
23: - $n-c = 76-3 = 73$. This matches.
24: 
25: Thus, the smallest possible value of $c$ is 3.
26: 
27: \(\square\)
