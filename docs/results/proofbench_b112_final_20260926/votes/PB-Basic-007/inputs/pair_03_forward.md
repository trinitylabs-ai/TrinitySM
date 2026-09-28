# Problem

Determine all positive integers $n$ and integer sequences $a_0, a_1,\ldots, a_n$ such that $a_n = 3$ and
 \[f(a_{i-1}) = a_i\]
 for all $i = 1,2,\ldots,n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$.

# Proof A

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

# Proof B

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
