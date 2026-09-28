# Problem

Let $n$ be a positive integer that has a remainder of 6 when divided by 7. Let $d$ be any divisor of $n$.

Define $c$ such that when the expression $\left(d+\frac{n}{d}\right)^{2}$ is divided by $n$, the remainder is $n-c$.

What is the smallest possible value of $c$ among all $d$ and $n$ satisfying the conditions above?

(Note that the remainder when a positive integer $a$ is divided by a positive integer $b$ is the value of $r$ in the expression $a=b q+r, 0 \leq r \leq b-1$.)

# Proof A

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

# Proof B

1: Let $d$ be a divisor of $n$, and let $d' = n/d$. The expression is:
2: \[ E = \left(d + \frac{n}{d}\right)^2 = (d + d')^2 = d^2 + 2n + d'^2 \]
3: When $E$ is divided by $n$, the remainder is $r = (d^2 + d'^2) \pmod n$. We are given that this remainder is $n-c$. Since $0 \leq r < n$, it follows that $0 \leq n-c < n$, which implies $1 \leq c \leq n$. The condition $d^2 + d'^2 \equiv n-c \pmod n$ can be rewritten as:
4: \[ d^2 + d'^2 \equiv -c \pmod n \]
5: Let $g = \gcd(d, d')$. Then we can write $d = ga$ and $d' = gb$ where $\gcd(a, b) = 1$. The integer $n$ is then $n = dd' = g^2 ab$. Substituting these into the congruence gives:
6: \[ g^2 a^2 + g^2 b^2 \equiv -c \pmod{g^2 ab} \]
7: This implies that $g^2$ must divide $c$. Let $c = g^2 k$ for some positive integer $k$. Then:
8: \[ g^2(a^2 + b^2) \equiv -g^2 k \pmod{g^2 ab} \implies a^2 + b^2 \equiv -k \pmod{ab} \]
9: Thus, $a^2 + b^2 + k$ must be a multiple of $ab$. Let $a^2 + b^2 + k = mab$ for some positive integer $m$. We wish to find the smallest $c = g^2 k$ such that there exist $g, a, b, m$ satisfying $n = g^2 ab \equiv 6 \pmod 7$ and $k = mab - a^2 - b^2 > 0$.
10: 
11: If $g \ge 2$, then $c = g^2 k \ge 4$. We check if $c=1, 2, 3$ are possible by setting $g=1$, so $c=k$ and $n=ab \equiv 6 \pmod 7$.
12: 
13: **Case $c=1$ ($k=1$):** The equation is $a^2 + b^2 + 1 = mab$.
14: For a fixed $m$, let $(a, b)$ be a solution in positive integers with $a \le b$. If $a=b$, then $(m-2)a^2 = 1$, which implies $a=1$ and $m=3$. If $a < b$, we can use Vieta jumping: the value $x = (a^2+1)/b$ is the other root of $x^2 - (ma)x + (a^2+1) = 0$. Thus $x$ is an integer and $x = ma-b$. Since $a < b$, $x = (a^2+1)/b < (b^2+1)/b = b + 1/b$, so $x \le b$. If $x < a$, we have a smaller solution $(x, a)$. The descent must terminate when $x \ge a$, which means $a^2+1 \ge ab$. Since $b > a$, this implies $a(b-a) \le 1$. If $b-a=0$, we return to the $a=b$ case. If $b-a \ge 1$, then $a(b-a) \le 1$ implies $a=1$ and $b=2$. In this case, $m = (1^2+2^2+1)/(1 \cdot 2) = 3$.
15: The solutions for $m=3, k=1$ are generated by the recurrence $x_{i+1} = 3x_i - x_{i-1}$ with $x_0=1, x_1=1$. The sequence $x_i \pmod 7$ is:
16: $x_0=1, x_1=1, x_2=2, x_3=5, x_4=6, x_5=6, x_6=5, x_7=2, x_8=1, x_9=1, \dots$
17: The products $n_i = x_i x_{i+1} \pmod 7$ are:
18: $n_0 = 1, n_1 = 2, n_2 = 3, n_3 = 2, n_4 = 1, n_5 = 2, n_6 = 3, n_7 = 2, n_8 = 1$.
19: The products $n_i \pmod 7$ are in $\{1, 2, 3\}$, so they never reach 6.
20: 
21: **Case $c=2$ ($k=2$):** The equation is $a^2 + b^2 + 2 = mab$.
22: For a fixed $m$, let $(a, b)$ be a solution with $a \le b$. If $a=b$, then $(m-2)a^2 = 2$, which implies $a=1$ and $m=4$. If $a < b$, the descent $x = (a^2+2)/b$ terminates when $x \ge a$, which implies $a^2+2 \ge ab$, or $a(b-a) \le 2$.
23: If $a(b-a)=1$, then $a=1, b=2$, giving $m = (1+4+2)/2 = 3.5$ (not an integer).
24: If $a(b-a)=2$, then either $(a=1, b=3)$, giving $m = (1+9+2)/3 = 4$, or $(a=2, b=3)$, giving $m = (4+9+2)/6 = 2.5$ (not an integer).
25: Thus, the only possible value for $m$ is $m=4$.
26: The solutions for $m=4, k=2$ are generated by $x_{i+1} = 4x_i - x_{i-1}$ with $x_0=1, x_1=1$. The sequence $x_i \pmod 7$ is:
27: $x_0=1, x_1=1, x_2=3, x_3=4, x_4=6, x_5=6, x_6=4, x_7=3, x_8=1, x_9=1, \dots$
28: The products $n_i = x_i x_{i+1} \pmod 7$ are:
29: $n_0 = 1, n_1 = 3, n_2 = 5, n_3 = 3, n_4 = 1, n_5 = 3, n_6 = 5, n_7 = 3, n_8 = 1$.
30: The products $n_i \pmod 7$ are in $\{1, 3, 5\}$, so they never reach 6.
31: 
32: **Case $c=3$ ($k=3$):** The equation is $a^2 + b^2 + 3 = mab$.
33: We seek $a, b$ such that $ab \equiv 6 \pmod 7$ and $m = (a^2+b^2+3)/ab$ is an integer.
34: Testing $a=4, b=19$, we have $n = ab = 76$. Since $76 = 7 \times 10 + 6$, $n \equiv 6 \pmod 7$.
35: Then $m = (4^2 + 19^2 + 3)/(4 \times 19) = (16 + 361 + 3)/76 = 380/76 = 5$.
36: Since $m$ is an integer, $c=3$ is achievable.
37: Checking the remainder: $(4 + 19)^2 = 23^2 = 529$. Dividing 529 by 76: $529 = 76 \times 6 + 73$.
38: The remainder is $73 = 76 - 3$, so $c=3$.
39: 
40: Since $c=1$ and $c=2$ are impossible and $c=3$ is achievable, the smallest possible value of $c$ is 3.
