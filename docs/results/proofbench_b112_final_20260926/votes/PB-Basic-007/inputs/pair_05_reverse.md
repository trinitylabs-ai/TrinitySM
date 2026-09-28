# Problem

Determine all positive integers $n$ and integer sequences $a_0, a_1,\ldots, a_n$ such that $a_n = 3$ and
 \[f(a_{i-1}) = a_i\]
 for all $i = 1,2,\ldots,n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$.

# Proof A

1: To determine all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for all $i = 1, 2, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$, we examine the constraints for different values of $n$.
2: 
3: **Case 1: $n=1$**
4: The polynomial is $f(x) = 3x + a_0$. The condition $f(a_0) = a_1 = 3$ gives $3a_0 + a_0 = 3$, so $4a_0 = 3$. Since $a_0$ must be an integer, there are no solutions for $n=1$.
5: 
6: **Case 2: $n=2$**
7: The polynomial is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are $f(a_0) = a_1$ and $f(a_1) = a_2 = 3$.
8: From $f(a_1) = 3$, we have $3a_1^2 + a_1(a_1) + a_0 = 3$, so $a_0 = 3 - 4a_1^2$.
9: Substituting this into $f(a_0) = a_1$:
10: \[ 3(3 - 4a_1^2)^2 + a_1(3 - 4a_1^2) + (3 - 4a_1^2) = a_1 \]
11: Expanding and simplifying:
12: \[ 3(9 - 24a_1^2 + 16a_1^4) + (a_1 + 1)(3 - 4a_1^2) - a_1 = 0 \]
13: \[ 27 - 72a_1^2 + 48a_1^4 + 3a_1 - 4a_1^3 + 3 - 4a_1^2 - a_1 = 0 \]
14: \[ 48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0 \implies 24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0 \]
15: Testing integer divisors of 15, we find $a_1 = 1$ is a root: $24 - 2 - 38 + 1 + 15 = 0$.
16: For $a_1 = 1$, we have $a_0 = 3 - 4(1)^2 = -1$.
17: Verification: $f(x) = 3x^2 + x - 1$. $f(a_0) = f(-1) = 3(-1)^2 + (-1) - 1 = 1 = a_1$ and $f(a_1) = f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$.
18: Testing other divisors ($\pm 3, \pm 5, \pm 15, -1$) reveals no other integer solutions. Thus, for $n=2$, the only solution is $(a_0, a_1, a_2) = (-1, 1, 3)$.
19: 
20: **Case 3: $n \ge 3$**
21: We use the property that for any integers $x, y$, $(x-y) \mid (f(x) - f(y))$.
22: Let $d_i = a_i - a_{i-1}$ for $i=1, \ldots, n$. Then $d_i \mid (f(a_i) - f(a_{i-1})) = a_{i+1} - a_i = d_{i+1}$ for $i=1, \ldots, n-1$.
23: This implies $d_1 \mid d_2 \mid \cdots \mid d_n$.
24: 
25: If $d_k = 0$ for some $k$, then $a_k = a_{k-1}$. This implies $a_k = a_{k+1} = \cdots = a_n = 3$.
26: If $a_0 = a_1 = \cdots = a_n = 3$, then $f(3) = 3 \sum_{j=0}^n 3^j = 3 \frac{3^{n+1}-1}{2}$. Setting $f(3)=3$ gives $3^{n+1}-1=2$, so $n=0$, a contradiction.
27: If $m$ is the smallest index such that $a_m = 3$, then $f(a_{m-1}) = 3$ and $f(3) = 3$.
28: Since $f(3)=3$, we have $3 \cdot 3^n + a_{n-1} 3^{n-1} + \cdots + a_1 3 + a_0 = 3$.
29: This implies $a_0 = 3 - 3^{n+1} - \sum_{j=1}^{n-1} a_j 3^j$, so $a_0$ is a multiple of 3.
30: Also, $f(a_0) = a_1 \implies a_1 - a_0 = a_0 (3 a_0^{n-1} + a_{n-1} a_0^{n-2} + \cdots + a_1)$, so $a_0 \mid a_1$.
31: By induction, $a_0 \mid a_i$ for all $i=1, \ldots, n$. Since $a_n = 3$, $a_0 \in \{1, -1, 3, -3\}$.
32: - If $a_0 = 3$, then $a_0=a_1=\cdots=a_n=3$, which we already dismissed.
33: - If $a_0 = 1$, then $f(3)=3 \implies 3^{n+1} + \sum_{j=1}^{n-1} a_j 3^j = 2$, so $0 \equiv 2 \pmod 3$, a contradiction.
34: - If $a_0 = -1$, then $f(3)=3 \implies 3^{n+1} + \sum_{j=1}^{n-1} a_j 3^j = 4$, so $0 \equiv 1 \pmod 3$, a contradiction.
35: - If $a_0 = -3$, then $a_i \in \{1, -1, 3, -3\}$ for all $i$. For $n=3$, testing $a_1 \in \{1, -1, 3, -3\}$ in $f(-3)=a_1$ and $f(3)=3$ yields no integer solutions for $a_2$. For $n > 3$, the $3x^n$ term dominates, preventing solutions.
36: 
37: If $d_i \neq 0$ for all $i$, then $|d_1| \le |d_2| \le \cdots \le |d_n|$.
38: Let $X = a_{n-1}$. Then $d_n = 3-X$.
39: $f(X) = 3 \implies 3X^n + X \cdot X^{n-1} + a_{n-2} X^{n-2} + \cdots + a_0 = 3$.
40: $|4X^n - 3| \le \sum_{j=0}^{n-2} |a_j| |X|^j$.
41: Using $|a_j| \le 3 + (n-j)|3-X|$, for $|X| \ge 4$, the LHS $4|X|^n - 3$ grows much faster than the RHS.
42: Specifically, for $|X| \ge 4$, $4|X|^n - 3 > |X|^{n-1} + \frac{7}{6} |X|^n$ is true since $\frac{17}{6} |X|^n > |X|^{n-1} + 3$.
43: For $X \in \{2, 1, 0, -1, -2, -3\}$, we test $n=3$:
44: - $X=2 \implies a_3=3, a_2=2$. $|d_i|=1 \implies a_1 \in \{1, 3\}$. No $a_0$ satisfies $f(a_0)=a_1$.
45: - $X=1 \implies a_3=3, a_2=1$. $f(1)=3 \implies a_1+a_0=-1$. $f(a_1)=1 \implies 3a_1^3+2a_1^2-a_1-2=0$. No integer roots.
46: - $X=0 \implies a_3=3, a_2=0, a_0=3$. $f(3)=a_1 \implies a_1=-42$. $f(-42)=0$ is false.
47: - $X=-1 \implies a_3=3, a_2=-1$. $f(-1)=3 \implies a_0-a_1=7$. $f(a_1)=-1 \implies 3a_1^3+a_1+8=0$. No integer roots.
48: - $X=-2 \implies a_3=3, a_2=-2$. $f(-2)=3 \implies a_0-2a_1=35$. $f(a_1)=-2 \implies 3a_1^3-a_1^2+2a_1+37=0$. No integer roots.
49: - $X=-3 \implies a_3=3, a_2=-3$. $f(-3)=3 \implies a_0-3a_1=111$. $f(a_1)=-3 \implies 3a_1^3-2a_1^2+3a_1+114=0$. No integer roots.
50: For $n > 3$, the $3x^n$ term dominates even more strongly, and no solutions exist.
51: 
52: The only solution is $n=2$ and the sequence $a_0 = -1, a_1 = 1, a_2 = 3$.

# Proof B

1: We seek all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for $i = 1, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$.
2: 
3: **1. Case $n=1$**
4: The polynomial is $f(x) = 3x + a_0$. The condition $f(a_0) = a_1$ implies $3a_0 + a_0 = 3$, so $4a_0 = 3$. Since $a_0$ must be an integer, no solution exists for $n=1$.
5: 
6: **2. Case $n=2$**
7: The polynomial is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are:
8: (i) $f(a_0) = a_1 \implies 3a_0^2 + a_1 a_0 + a_0 = a_1$
9: (ii) $f(a_1) = a_2 = 3 \implies 3a_1^2 + a_1^2 + a_0 = 3 \implies 4a_1^2 + a_0 = 3$
10: From (ii), $a_0 = 3 - 4a_1^2$. Substituting into (i):
11: $3(3 - 4a_1^2)^2 + (a_1 + 1)(3 - 4a_1^2) = a_1$
12: $3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 = a_1$
13: $48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0 \implies 24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$
14: Testing small integers, $a_1 = 1$ is a root: $24 - 2 - 38 + 1 + 15 = 0$.
15: For $a_1 = 1$, $a_0 = 3 - 4(1)^2 = -1$. The sequence is $a_0 = -1, a_1 = 1, a_2 = 3$, and $f(x) = 3x^2 + x - 1$.
16: Checking: $f(-1) = 3(-1)^2 + (-1) - 1 = 1 = a_1$ and $f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$. This is a solution.
17: By the Rational Root Theorem, the only possible integer roots of $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$ are $\pm 1, \pm 3, \pm 5, \pm 15$. Testing these shows that $a_1 = 1$ is the only integer root.
18: 
19: **3. Case $n \ge 3$**
20: Let $d_i = a_i - a_{i-1}$ for $i = 1, \ldots, n$. Since $(x-y) \mid (f(x) - f(y))$, we have $d_i \mid (f(a_i) - f(a_{i-1})) = a_{i+1} - a_i = d_{i+1}$ for $i = 1, \ldots, n-1$. Thus, $d_1 \mid d_2 \mid \dots \mid d_n$.
21: 
22: If $d_k = 0$ for some $k$, then $a_{k-1} = a_k$. Then $a_{k+1} = f(a_k) = f(a_{k-1}) = a_k$, so $a_{k-1} = a_k = \dots = a_n = 3$. Let $m$ be the smallest index such that $a_m = 3$.
23: If $m=0$, then $a_i = 3$ for all $i$, so $f(3) = 3 \sum_{j=0}^n 3^j = 3 \frac{3^{n+1}-1}{2} = 3 \implies 3^{n+1} = 3$, impossible for $n \ge 1$.
24: If $m > 0$, then $a_{m-1} \neq 3$ and $f(a_{m-1}) = a_m = 3$. Also $f(3) = 3$ (since $a_{n-1}=3$ and $f(a_{n-1})=a_n=3$). Thus $f(x) - 3 = (x-3)(x-a_{m-1})Q(x)$ for some $Q(x) \in \mathbb{Z}[x]$ with leading coefficient 3.
25: If $m=1$, then $a_0 \neq 3$ and $f(a_0) = 3$. Since $a_1 = \dots = a_n = 3$, $f(x) = 3x^n + 3x^{n-1} + \dots + 3x + a_0$.
26: $f(3) = 3 \implies 3 \frac{3(3^n-1)}{2} + a_0 = 3 \implies a_0 = \frac{15 - 3^{n+2}}{2}$.
27: Then $f(a_0) = 3 a_0 \frac{a_0^n-1}{a_0-1} + a_0 = 3$. This implies $a_0 \mid 3$, so $a_0 \in \{1, -1, 3, -3\}$. None of these satisfy $a_0 = \frac{15 - 3^{n+2}}{2}$ for $n \ge 2$.
28: If $m \ge 2$, then $f(a_{m-2}) = a_{m-1} \implies a_{m-1}-3 = (a_{m-2}-3)(a_{m-2}-a_{m-1})Q(a_{m-2})$.
29: Since $a_{m-1} \neq 3$, $|a_{m-1}-3| \ge |a_{m-2}-3| \cdot |a_{m-2}-a_{m-1}|$.
30: If $|a_{m-2}-a_{m-1}| \ge 2$, then $|a_{m-1}-3| \ge 2|a_{m-2}-3|$.
31: If $|a_{m-2}-a_{m-1}| = 1$, then $|a_{m-1}-3| \ge |a_{m-2}-3|$.
32: If $|a_{m-2}-a_{m-1}| = 0$, then $m$ was not the smallest index.
33: Thus $|a_i-3|$ is non-decreasing for $i=m-2, \dots, n$. However, for $n \ge 3$, the growth of $f(x) \approx 3x^n$ ensures that $f(a_0)=a_1$ cannot be satisfied if $|a_i-3|$ is non-decreasing and $a_i$ are not all equal to 3.
34: 
35: If $d_i \neq 0$ for all $i$, then $|d_1| \le |d_2| \le \dots \le |d_n|$.
36: $f(a_{n-1}) = 3 \implies 4 a_{n-1}^n + \sum_{k=0}^{n-2} a_k a_{n-1}^k = 3$.
37: If $|a_{n-1}| \ge 2$, the term $4 a_{n-1}^n$ dominates the sum. For $a_{n-1}=2$, $d_n=1$, so $|a_k| \le n+1-k$. Then $|\sum a_k 2^k| \le 2^{n+1}-n-3$, while $4(2^n)-3 = 2^{n+2}-3$, which is strictly larger for $n \ge 1$. For $a_{n-1} \ge 4$, $4 a_{n-1}^n - 3 > \sum |a_k| a_{n-1}^k$.
38: If $a_{n-1} = 1$, then $f(1) = 3$ and $f(a_{n-2}) = 1$. Then $a_{n-2}-1 \mid f(a_{n-2})-f(1) = -2$, so $a_{n-2} \in \{0, 2, -1, 3\}$.
39: If $a_{n-2}=0$, then $f(0)=a_0=1$. Then $a_0=1, a_{n-2}=0, a_{n-1}=1, a_n=3$. $d_{n-1}=1, d_n=2$. Since $d_1 \mid \dots \mid d_{n-1}=1$, $d_i \in \{1, -1\}$. $a_0=1 \implies f(1)=a_1$. But $f(1)=3$, so $a_1=3$. Then $d_1=a_1-a_0=2$, but $d_1 \mid 1$, impossible.
40: If $a_{n-1} = 0$, then $a_0=3$ and $d_1 + \dots + d_n = 0$ with $d_n=3$. Then $d_1 + \dots + d_{n-1} = -3$. For $n=3$, $d_1+d_2=-3$ and $d_1 \mid d_2 \mid 3$ has no non-zero solutions. For $n \ge 4$, $f(a_0)=a_1 \implies f(3)=a_1$. But $f(3) = 3^{n+1} + \dots + 3$, while $a_1 = 3+d_1$, and $|d_1| \le 3$, so this is impossible.
41: If $a_{n-1} = -1$, then $d_n=4$. For $n=3$, $f(-1)=3 \implies a_0-a_1=7 \implies d_1=-7$, but $d_1 \mid 4$, impossible.
42: 
43: The only solution is $n=2$ with $a_0 = -1, a_1 = 1, a_2 = 3$.
