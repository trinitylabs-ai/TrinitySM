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
