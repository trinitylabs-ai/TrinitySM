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

1: To find the smallest possible value of $c$, we start by analyzing the given conditions. Let $n$ be a positive integer such that $n \equiv 6 \pmod{7}$. Let $d$ be a divisor of $n$, and let $k = n/d$. The expression given is $X = \left(d + \frac{n}{d}\right)^2 = (d + k)^2 = d^2 + k^2 + 2n$. When $X$ is divided by $n$, the remainder $r$ is the same as the remainder of $d^2 + k^2$ divided by $n$. We are told $r = n - c$, where $0 \le r < n$, which implies $0 < c \le n$. Thus, $c$ is the smallest positive integer such that $d^2 + k^2 + c$ is a multiple of $n$.
2: 
3: Let $d^2 + k^2 + c = mn$ for some positive integer $m$. Since $n = dk$, we have the equation:
4: \[ d^2 + k^2 + c = mdk \]
5: We want to find the smallest $c$ for which there exist $n, d, k$ such that $dk = n \equiv 6 \pmod{7}$ and $d^2 + k^2 + c = mdk$.
6: 
7: First, we test if $c=1$ is possible. The equation is $d^2 + k^2 + 1 = mdk$. Using the method of Vieta Jumping, for a fixed $m$, if $(d, k)$ is a solution with $d \le k$, the smallest solution must satisfy $d=k$ or $d=1$.
8: - If $d=k$, then $2d^2 + 1 = md^2$, so $(m-2)d^2 = 1$, which implies $d=1$ and $m=3$.
9: - If $d=1$, then $k^2 - mk + 2 = 0$, so $k$ must be a divisor of 2. If $k=1$, then $m=3$. If $k=2$, then $4-2m+2=0$, so $m=3$.
10: Thus, the only possible value for $m$ is $m=3$. For $m=3$, the solutions $(d, k)$ are pairs of alternate Fibonacci numbers $(F_{2j-1}, F_{2j+1})$. Then $n = F_{2j-1}F_{2j+1}$. The Fibonacci sequence modulo 7 is $0, 1, 1, 2, 3, 5, 1, 6, 0, 6, 6, 5, 4, 2, 6, 1, 0, \dots$ (period 16). The sequence $F_{2j-1} \pmod{7}$ is $1, 2, 5, 6, 6, 5, 2, 1, \dots$ (period 8). The products $n = F_{2j-1}F_{2j+1} \pmod{7}$ are:
11: $1\cdot 2=2, 2\cdot 5=10\equiv 3, 5\cdot 6=30\equiv 2, 6\cdot 6=36\equiv 1, 6\cdot 5=30\equiv 2, 5\cdot 2=10\equiv 3, 2\cdot 1=2, 1\cdot 1=1$.
12: None of these are $6 \pmod{7}$, so $c=1$ is impossible.
13: 
14: Next, we test if $c=2$ is possible. The equation is $d^2 + k^2 + 2 = mdk$. Again, by Vieta Jumping, the smallest solution $(d, k)$ with $d \le k$ must satisfy $d=k$ or $d=1$.
15: - If $d=k$, then $2d^2 + 2 = md^2$, so $(m-2)d^2 = 2$. This implies $d=1$ and $m=4$.
16: - If $d=1$, then $k^2 - mk + 3 = 0$, so $k$ must be a divisor of 3. If $k=1$, then $m=4$. If $k=3$, then $9-3m+3=0$, so $m=4$.
17: Thus, the only possible value for $m$ is $m=4$. For $m=4$, the solutions $x_j$ are generated by $x_0=1, x_1=1, x_{j+1}=4x_j - x_{j-1}$. The sequence $x_j \pmod{7}$ is $1, 1, 3, 4, 6, 6, 4, 3, 1, 1, \dots$ (period 8). The products $n = x_j x_{j+1} \pmod{7}$ are:
18: $1\cdot 1=1, 1\cdot 3=3, 3\cdot 4=12\equiv 5, 4\cdot 6=24\equiv 3, 6\cdot 6=36\equiv 1, 6\cdot 4=24\equiv 3, 4\cdot 3=12\equiv 5, 3\cdot 1=3$.
19: None of these are $6 \pmod{7}$, so $c=2$ is impossible.
20: 
21: Finally, we test $c=3$. We look for $n, d, k$ such that $d^2 + k^2 + 3 = mdk$ and $dk \equiv 6 \pmod{7}$.
22: Let $n=76$. Then $n = 7 \times 10 + 6 \equiv 6 \pmod{7}$.
23: Taking $d=4$, we have $k = 76/4 = 19$.
24: Calculating $d^2 + k^2 + 3$:
25: \[ 4^2 + 19^2 + 3 = 16 + 361 + 3 = 380 \]
26: Since $380 = 5 \times 76$, the condition $d^2 + k^2 + 3 = m n$ is satisfied with $m=5$.
27: To verify the remainder:
28: \[ (d + k)^2 = (4 + 19)^2 = 23^2 = 529 \]
29: Dividing 529 by 76:
30: \[ 529 = 6 \times 76 + 73 \]
31: The remainder is $r = 73$.
32: We have $n - c = 76 - c = 73$, which gives $c = 3$.
33: 
34: Since $c=1$ and $c=2$ are impossible, the smallest possible value is 3.
35: 
36: The smallest possible value of $c$ is 3. \(\square\)
