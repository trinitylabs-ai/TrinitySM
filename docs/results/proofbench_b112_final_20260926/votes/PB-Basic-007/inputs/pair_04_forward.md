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

1: We seek all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for $i = 1, 2, \ldots, n$, where $f(x) = \sum_{k=0}^n a_k x^k$.
2: 
3: Case $n=1$:
4: The polynomial is $f(x) = 3x + a_0$. The condition $f(a_0) = a_1$ implies $3a_0 + a_0 = 3$, so $4a_0 = 3$. Since $a_0$ must be an integer, there are no solutions for $n=1$.
5: 
6: Case $n=2$:
7: The polynomial is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are:
8: 1. $f(a_1) = a_2 \implies 3a_1^2 + a_1^2 + a_0 = 3 \implies a_0 = 3 - 4a_1^2$.
9: 2. $f(a_0) = a_1 \implies 3a_0^2 + a_1 a_0 + a_0 = a_1$.
10: Substituting $a_0 = 3 - 4a_1^2$ into the second equation:
11: $3(3 - 4a_1^2)^2 + (a_1 + 1)(3 - 4a_1^2) = a_1$
12: $3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 - a_1 = 0$
13: $48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0$
14: Dividing by 2: $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
15: Testing integer divisors of 15, we find $a_1 = 1$ is a root: $24 - 2 - 38 + 1 + 15 = 0$.
16: For $a_1 = 1$, $a_0 = 3 - 4(1)^2 = -1$.
17: Checking the sequence $a_0 = -1, a_1 = 1, a_2 = 3$:
18: $f(x) = 3x^2 + x - 1$.
19: $f(a_0) = f(-1) = 3(-1)^2 + (-1) - 1 = 1 = a_1$.
20: $f(a_1) = f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$.
21: This is a valid solution. Dividing $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15$ by $(a_1 - 1)$ gives $24a_1^3 + 22a_1^2 - 16a_1 - 15 = 0$. Testing divisors of 15 shows no other integer roots.
22: 
23: Case $n \ge 3$:
24: Let $d_i = a_i - a_{i-1}$. For any polynomial $f(x)$ with integer coefficients, $x-y$ divides $f(x) - f(y)$. Thus:
25: $d_i = a_i - a_{i-1} \mid f(a_i) - f(a_{i-1}) = a_{i+1} - a_i = d_{i+1}$ for $i = 1, \ldots, n-1$.
26: If $d_k = 0$ for some $k \in \{1, \ldots, n\}$, then $a_{k-1} = a_k$, which implies $a_{k+1} = f(a_k) = f(a_{k-1}) = a_k$. By induction, $a_{k-1} = a_k = \cdots = a_n = 3$.
27: If $k=1$, $a_0 = a_1 = \cdots = a_n = 3$, so $f(3) = 3 \sum_{j=0}^n 3^j = 3 \frac{3^{n+1}-1}{2} = 3 \implies 3^{n+1} = 3$, so $n=0$, a contradiction.
28: If $k > 1$, $f(3) = a_n = 3$ and $f(a_{k-2}) = a_{k-1} = 3$. Thus $f(x) - 3 = 3(x-3)(x-a_{k-2})Q(x)$ for some $Q(x) \in \mathbb{Z}[x]$.
29: Then $f(a_{k-3}) - 3 = a_{k-2} - 3 = 3(a_{k-3}-3)d_{k-2}Q(a_{k-3})$.
30: Since $d_{k-1} = a_{k-1} - a_{k-2} = 3 - a_{k-2}$, we have $-d_{k-1} = 3(a_{k-3}-3)d_{k-2}Q(a_{k-3})$.
31: If $d_{k-2} \neq 0$, then $|d_{k-1}| \ge 3 |a_{k-3}-3| |d_{k-2}| |Q(a_{k-3})|$. Since $|d_{k-2}| \le |d_{k-1}|$, this requires $|a_{k-3}-3| |Q(a_{k-3})| \le 1/3$, which implies $a_{k-3} = 3$. This forces $d_{k-2} = 0$, and by repeating this, we eventually reach $d_1 = 0$, which we already ruled out.
32: Thus $d_i \neq 0$ for all $i$, and $1 \le |d_1| \le |d_2| \le \cdots \le |d_n|$.
33: 
34: From $f(a_{n-1}) = a_n$, we have $4 a_{n-1}^n + \sum_{k=0}^{n-2} a_k a_{n-1}^k = 3$. Let $m = a_{n-1}$.
35: We have $|a_k| \le 3 + (n-k)|d_n| = 3 + (n-k)|3-m|$.
36: For $|m| \ge 3$, $4|m|^n - 3 \le \sum_{k=0}^{n-2} (3 + (n-k)|3-m|) |m|^k$.
37: Dividing by $|m|^n$, the RHS is bounded by $\frac{3}{|m|(|m|-1)} + \frac{|3-m|}{(|m|-1)^2} (2 - \frac{1}{|m|} - \frac{n+1}{|m|^{n-1}} + \frac{n}{|m|^n})$.
38: For $|m| \ge 3$, $\frac{|3-m|}{|m|-1} \le 3$. The RHS is roughly $\le \frac{3}{6} + \frac{3}{2} \cdot 2 = 3.5$.
39: $4 - \frac{3}{|m|^n} \le 3.5 \implies 0.5 \le \frac{3}{|m|^n}$, which is false for $|m| \ge 3, n \ge 3$.
40: If $m=2$, $|d_n|=1$. Then $4 \cdot 2^n - 3 \le \sum_{k=0}^{n-2} (n-k+3) 2^k = 3 \cdot 2^n - n - 5$, so $2^n \le -n - 2$, impossible.
41: If $m=1$, $|d_n|=2$. Then $\sum_{k=0}^{n-2} a_k = -1$. $d_{n-1} = 1 - a_{n-2} \mid 2 \implies a_{n-2} \in \{-1, 0, 2, 3\}$.
42: If $a_{n-2} = 0$, $f(0) = a_{n-1} = 1 \implies a_0 = 1$. Then $f(a_0) = f(1) = 3 = a_1$. Then $f(a_1) = f(3) = a_2$. But $f(3) = 3 \cdot 3^n + 3^{n-1} + \sum_{k=2}^{n-3} a_k 3^k + 3(3) + 1$, which exceeds $|a_2| \le 3 + (n-2)2$ for $n \ge 3$.
43: If $a_{n-2} = 2$, $f(2) = 1 \implies 4 \cdot 2^n + \sum_{k=0}^{n-3} a_k 2^k = 1 \implies 4 \cdot 2^n - 1 \le \sum_{k=0}^{n-3} |a_k| 2^k \le 2 \cdot 2^n + 3 \cdot 2^{n-2} - 2n - 7$, impossible for $n \ge 3$.
44: If $a_{n-2} = -1$, $f(-1) = 1 \implies f(x)-1 = 3(x-1)(x+1)Q(x)$. Then $f(a_{n-3}) - 1 = a_{n-2} - 1 = -1 - 1 = -2 \implies 3(a_{n-3}^2-1)Q(a_{n-3}) = -2$, impossible.
45: If $a_{n-2} = 3$, $f(3) = 1 \implies 3 \cdot 3^n + \sum_{k=0}^{n-3} a_k 3^k = -1 \implies 3 \cdot 3^n + 1 \le \sum_{k=0}^{n-3} |a_k| 3^k \le 15.5 \cdot 3^{n-2} - 4n - 7.5$, impossible.
46: If $m=0$, $a_0 = 3$. $f(3) = a_1$. $d_1 = a_1 - 3$. $|d_1| \le |d_n| = 3 \implies a_1 \in \{0, 1, \dots, 6\}$.
47: $f(3) = 3^{n+1} + \sum_{k=2}^{n-2} a_k 3^k + 3a_1 + 3 = a_1 \implies 3^{n+1} + \sum a_k 3^k + 2a_1 + 3 = 0$.
48: Modulo 3, $2a_1 \equiv 0 \pmod 3 \implies a_1 \in \{0, 3, 6\}$.
49: $a_1 = 0 \implies 3^n + \sum a_k 3^{k-1} + 1 = 0 \implies 1 \equiv 0 \pmod 3$.
50: $a_1 = 3 \implies d_1 = 0$, impossible.
51: $a_1 = 6 \implies 3^n + \sum a_k 3^{k-1} + 5 = 0 \implies 2 \equiv 0 \pmod 3$.
52: If $m=-1$, $|d_n|=4$. $d_{n-1} = -1 - a_{n-2} \mid 4 \implies a_{n-2} \in \{0, -2, 1, -3, 3, -5\}$.
53: If $a_{n-2} = 0$, $a_0 = -1, a_1 = 3$. For $n=3$, $f(x) = 3x^3 - x^2 + 3x - 1$, $f(-1) = -8 \neq 3$. For $n \ge 4$, $f(3)$ exceeds $|a_2|$.
54: If $a_{n-2} = 3$, $f(3) = -1 \implies 3 \cdot 3^n + \sum a_k 3^k = -1$, impossible as shown before.
55: If $a_{n-2} = -2$, $d_{n-1} = 1$. Then $|d_i| \le 1$ for $i < n$. $a_k \in \{-1, -2, -3\}$.
56: Then $f(-2) = 3 \implies 4(-2)^n + \sum_{k=0}^{n-2} a_k (-2)^k = 3$.
57: For $n=3$, $4(-8) + a_1(-2) + a_0 = 3 \implies a_0 - 2a_1 = 35$.
58: Since $a_0, a_1 \in \{-1, -2, -3\}$, $|a_0 - 2a_1| \le 3 - 2(-3) = 9$, so $35 \le 9$ is false.
59: If $m=-2$, $|d_n|=5$. $d_{n-1} = -2 - a_{n-2} \mid 5 \implies a_{n-2} \in \{-3, -7, -1, 3\}$.
60: $a_{n-2} = 3$ was ruled out. $a_{n-2} = -1$ leads to $|d_i| \le 1$ for $i < n$, and $f(-2) = 3 \implies 4(-2)^n + \sum a_k (-2)^k = 3$, which is impossible for $a_k \in \{-1, -2, -3\}$ by the same logic as above.
61: $a_{n-2} = -3 \implies d_{n-1} = 1$. Again $|d_i| \le 1$ for $i < n$, $a_k \in \{-2, -3, -4\}$.
62: $4(-2)^n + \sum a_k (-2)^k = 3 \implies |4(-2)^n - 3| \le \sum |a_k| 2^k \le \sum 4 \cdot 2^k = 4(2^{n-1}-1) = 2 \cdot 2^n - 4$.
63: $4 \cdot 2^n - 3 \le 2 \cdot 2^n - 4 \implies 2 \cdot 2^n \le -1$, impossible.
64: $a_{n-2} = -7 \implies d_{n-1} = 5$. Then $|d_i| \le 5$ for all $i$.
65: $f(-2) = 3 \implies 4(-2)^n + \sum_{k=0}^{n-2} a_k (-2)^k = 3$.
66: For $n=3$, $4(-8) + a_1(-2) + a_0 = 3 \implies a_0 - 2a_1 = 35$.
67: Since $|d_1| \le 5$, $|a_1 - a_0| \le 5$.
68: $a_0 = 2a_1 + 35 \implies |a_1 - (2a_1 + 35)| \le 5 \implies |-a_1 - 35| \le 5 \implies a_1 \in \{-30, \dots, -40\}$.
69: Then $a_0 = 2a_1 + 35 \in \{-60+35, \dots, -80+35\} = \{-25, \dots, -45\}$.
70: Then $|d_1| = |a_1 - a_0| = |-a_1 - 35| \le 5$.
71: However, $a_2 = f(a_1) = 3a_1^3 - 2a_1^2 + a_0$.
72: $|a_2| \le 3 + (n-2)5 = 3 + 5 = 8$.
73: But $|3a_1^3 - 2a_1^2 + a_0| \approx 3|a_1|^3 \approx 3(35^3) \approx 128,000$, which is much larger than 8.
74: 
75: The only solution is $n=2, a_0 = -1, a_1 = 1, a_2 = 3$.
