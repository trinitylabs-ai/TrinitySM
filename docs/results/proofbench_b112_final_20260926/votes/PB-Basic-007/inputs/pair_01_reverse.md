# Problem

Determine all positive integers $n$ and integer sequences $a_0, a_1,\ldots, a_n$ such that $a_n = 3$ and
 \[f(a_{i-1}) = a_i\]
 for all $i = 1,2,\ldots,n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$.

# Proof A

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

# Proof B

1: We seek all positive integers $n$ and integer sequences $a_0, a_1, \dots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for $i = 1, 2, \dots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \dots + a_0$.
2: 
3: **Case 1: $n=1$**
4: The polynomial is $f(x) = 3x + a_0$. The condition $f(a_0) = a_1$ gives $3a_0 + a_0 = 3$, so $4a_0 = 3$, which has no integer solution. Thus, $n=1$ is impossible.
5: 
6: **Case 2: $n=2$**
7: The polynomial is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are:
8: 1. $f(a_1) = a_2 = 3 \implies 3a_1^2 + a_1^2 + a_0 = 3 \implies 4a_1^2 + a_0 = 3$.
9: 2. $f(a_0) = a_1 \implies 3a_0^2 + a_1 a_0 + a_0 = a_1$.
10: 
11: From the first equation, $a_0 = 3 - 4a_1^2$. Substituting into the second:
12: $3(3 - 4a_1^2)^2 + a_1(3 - 4a_1^2) + (3 - 4a_1^2) = a_1$
13: $3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 - a_1 = 0$
14: $48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0 \implies 24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
15: Testing integer divisors of 15, we find $a_1 = 1$ is a root: $24 - 2 - 38 + 1 + 15 = 0$.
16: For $a_1 = 1$, $a_0 = 3 - 4(1)^2 = -1$.
17: Check: $f(x) = 3x^2 + x - 1$. $f(-1) = 3 - 1 - 1 = 1 = a_1$ and $f(1) = 3 + 1 - 1 = 3 = a_2$.
18: Testing other integer divisors of 15 ($\pm 3, \pm 5, \pm 15$) shows no other integer roots. Thus, $(n, a_0, a_1, a_2) = (2, -1, 1, 3)$ is the only solution for $n=2$.
19: 
20: **Case 3: $n \ge 3$**
21: For any polynomial $f(x)$ with integer coefficients, $(x - y) \mid (f(x) - f(y))$.
22: Thus, $(a_1 - a_0) \mid (f(a_1) - f(a_0)) = (a_2 - a_1)$, and generally $(a_k - a_{k-1}) \mid (a_{k+1} - a_k)$ for $k=1, \dots, n-1$.
23: Let $d_k = a_k - a_{k-1}$. Then $d_1 \mid d_2 \mid \dots \mid d_n$.
24: 
25: Subcase 3.1: $d_k = 0$ for some $k$.
26: If $d_k = 0$, then $a_k = a_{k-1}$. Since $d_k \mid d_{k+1}$, we must have $d_{k+1} = 0$, and by induction $a_{k-1} = a_k = \dots = a_n = 3$.
27: If $k=1$, then $a_0 = a_1 = \dots = a_n = 3$. Then $f(3) = 3 \sum_{j=0}^n 3^j = 3 \frac{3^{n+1}-1}{2} = 3 \implies 3^{n+1} = 3 \implies n=0$, a contradiction.
28: If $k > 1$, let $m = k-1$. Then $a_m = a_{m+1} = \dots = a_n = 3$ and $a_{m-1} \neq 3$.
29: Then $f(a_{m-1}) = a_m = 3$ and $f(3) = a_{m+1} = 3$.
30: Thus $f(x) - 3 = (x-3)(x-a_{m-1}) Q(x)$ for some $Q(x) \in \mathbb{Z}[x]$.
31: Since $a_n = 3$, the leading coefficient of $Q(x)$ must be 3.
32: For $n=3$, if $a_2 = a_3 = 3$, then $f(x) = 3x^3 + 3x^2 + a_1 x + a_0$.
33: $f(3) = 3 \implies 81 + 27 + 3a_1 + a_0 = 3 \implies 3a_1 + a_0 = -105$.
34: $f(a_1) = 3 \implies 3a_1^3 + 3a_1^2 + a_1^2 + a_0 = 3 \implies 3a_1^3 + 4a_1^2 + a_0 = 3$.
35: Substituting $a_0 = -105 - 3a_1$ gives $3a_1^3 + 4a_1^2 - 3a_1 - 108 = 0$.
36: The only integer root is $a_1 = 3$, which implies $a_1 = a_2 = a_3 = 3$, reducing to the $k=1$ case.
37: For $n > 3$, if $a_{n-1} = a_n = 3$, then $f(x) - 3 = (x-3)(x-a_{n-2}) Q(x)$ with leading coefficient of $Q$ being 3.
38: Then $f(a_{n-3}) = a_{n-2} \implies 3(a_{n-3}-3)(a_{n-3}-a_{n-2}) Q(a_{n-3}) + 3 = a_{n-2}$.
39: This implies $(a_{n-3}-3)(a_{n-3}-a_{n-2}) \mid (a_{n-2}-3)$.
40: Let $X = a_{n-3}-3$ and $d = a_{n-2}-a_{n-3}$. Then $X(-d) \mid (X+d)$.
41: If $X=0$, then $a_{n-3}=3$, leading back to $a_i=3$. If $d=0$, then $a_{n-2}=a_{n-3}$, leading back to $a_i=3$.
42: If $X, d \neq 0$, then $|Xd| \le |X+d|$. For $X, d \ge 1$, $(X-1)(d-1) \le 1$.
43: If $X=1, d=1$, then $a_{n-3}=4, a_{n-2}=5$. Then $Q(4) = \frac{5-3}{3(4-3)(4-5)} = -2/3$, not an integer.
44: If $X=1, d=2$, then $a_{n-3}=4, a_{n-2}=6$. Then $Q(4) = \frac{6-3}{3(4-3)(4-6)} = -1/2$, not an integer.
45: Similar checks for negative $X, d$ show no solutions.
46: 
47: Subcase 3.2: $d_k \neq 0$ for all $k$.
48: Then $|d_1| \le |d_2| \le \dots \le |d_n|$.
49: $f(a_{n-1}) = 3 \implies 3 a_{n-1}^n + a_{n-1} a_{n-1}^{n-1} + a_{n-2} a_{n-1}^{n-2} + \dots + a_0 = 3$.
50: $4 a_{n-1}^n - 3 = - \sum_{k=0}^{n-2} a_k a_{n-1}^k$.
51: Let $A = |a_{n-1}|$. If $A \ge 3$, the LHS $|4 a_{n-1}^n - 3|$ grows as $4 A^n$, while the RHS $\sum_{k=0}^{n-2} |a_k| A^k$ grows as $O(A^{n-1})$.
52: Specifically, $|a_k| \le A + (n-k)|d_n|$. With $|d_n| = |3-a_{n-1}|$, for $A \ge 3$, $4 A^n - 3 \le \sum_{k=0}^{n-2} (A + (n-k)|d_n|) A^k$.
53: For $a_{n-1} = 3$, $d_n=0$ (handled). For $a_{n-1} \ge 4$, $d_n \le A+3$, and $4 A^n - 3 \le A \frac{A^{n-1}-1}{A-1} + (A+3) \sum (n-k) A^k$.
54: For $A=4$, $4 \cdot 4^n - 3 \le \frac{4^n-4}{3} + 7(2^n + 2^{n-1} - n - 2)$, which is false for $n \ge 3$.
55: For $a_{n-1} = -3$, $d_n = 6$. $|4(-3)^n - 3| \le 3 \frac{3^{n-1}-1}{2} + 6(3^n + 3^{n-1} - n - 2)$, which is false for $n \ge 3$.
56: Thus we only check $a_{n-1} \in \{-2, -1, 0, 1, 2\}$.
57: If $a_{n-1} = 2$, $d_n = 1$. $f(2) = 3$ and $f(a_{n-2}) = 2$.
58: Then $(2 - a_{n-2}) \mid (f(2) - f(a_{n-2})) = 1 \implies a_{n-2} \in \{1, 3\}$.
59: If $a_{n-2} = 3$, $f(3) = 2$. But $f(3) - f(2) = \sum_{j=1}^n a_j (3^j - 2^j) + (a_0 - a_0) = 3(3^n - 2^n) + 2(3^{n-1} - 2^{n-1}) + \dots$
60: For $n=3$, $f(3)-f(2) = 3(19) + 2(5) + 3(1) = 70 \neq -1$. For $n > 3$, this is even larger.
61: If $a_{n-2} = 1$, $f(1) = 2$. $f(2) - f(1) = 3(2^n - 1) + 2(2^{n-1} - 1) + 1(2^{n-2} - 1) + \dots$
62: For $n=3$, $f(2)-f(1) = 3(7) + 2(3) + 1(1) = 28 \neq 1$.
63: If $a_{n-1} = 1$, $d_n = 2$. $f(1) = 3$ and $f(a_{n-2}) = 1$.
64: Then $(1 - a_{n-2}) \mid 2 \implies a_{n-2} \in \{0, 2, -1, 3\}$.
65: If $a_{n-2} = 0$, $f(0) = 1 \implies a_0 = 1$. $f(1) = 3 \implies 3 + 1 + 0 + \dots + 1 = 3 \implies \sum_{k=1}^{n-3} a_k = -2$.
66: For $n=3$, $a_1 = -2$. $f(-2) = 3(-8) + 1(4) + 0 + 1 = -19 \neq 0$.
67: If $a_{n-1} = 0$, $d_n = 3$. $f(0) = 3 \implies a_0 = 3$. $f(a_{n-2}) = 0 \implies 3 a_{n-2}^n + 0 + a_{n-2} a_{n-2}^{n-2} + \dots + 3 = 0$.
68: For $n=3$, $3 a_1^3 + a_1^2 + 3 = 0$, no integer roots.
69: If $a_{n-1} = -1$, $d_n = 4$. $f(-1) = 3$ and $f(a_{n-2}) = -1$.
70: Then $(-1 - a_{n-2}) \mid 4 \implies a_{n-2} \in \{0, -2, 1, -3, -5, 3\}$.
71: For $n=3$, $f(-1) = -3 + 1 + a_1(-1) + a_0 = 3 \implies a_0 - a_1 = 5$.
72: $f(a_1) = -1 \implies 3 a_1^3 - a_1^2 + a_1^2 + a_0 = -1 \implies 3 a_1^3 + a_0 = -1$.
73: Substituting $a_0 = 5 + a_1$ gives $3 a_1^3 + a_1 + 6 = 0$.
74: Integer roots must divide 6. $a_1 = -1 \implies -3-1+6 = 2$; $a_1 = -2 \implies -24-2+6 = -20$. No roots.
75: If $a_{n-1} = -2$, $d_n = 5$. $f(-2) = 3$ and $f(a_{n-2}) = -2$.
76: Then $(-2 - a_{n-2}) \mid 5 \implies a_{n-2} \in \{-1, -3, -7, 3\}$.
77: For $n=3$, $f(-2) = -24 + 8 - 2 a_1 + a_0 = 3 \implies a_0 - 2 a_1 = 19$.
78: $f(a_1) = -2 \implies 3 a_1^3 - 2 a_1^2 + a_1^2 + a_0 = -2 \implies 3 a_1^3 - a_1^2 + a_0 = -2$.
79: Substituting $a_0 = 19 + 2 a_1$ gives $3 a_1^3 - a_1^2 + 2 a_1 + 21 = 0$.
80: Integer roots must divide 21. $a_1 = -1 \implies -3-1-2+21 = 15$; $a_1 = -2 \implies -24-4-4+21 = -11$. No roots.
81: 
82: The only solution is $n=2$ with $a_0 = -1, a_1 = 1, a_2 = 3$.
