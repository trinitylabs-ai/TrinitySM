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
