# Problem

For a real number $r$, let $A(r)$ denote the fractional part of $2r$ in its decimal representation. For a real number $r$ and a positive integer $n$, define $B(n,r)$ as
 $$
 B(n,r)=\sum_{k=1}^n A(kr).
 $$
 Find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$.

# Proof A

1: To find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$, where $B(n,r) = \sum_{k=1}^n A(kr)$ and $A(kr)$ denotes the fractional part of $2kr$, we proceed as follows.
2: 
3: Let $\{x\}$ denote the fractional part of $x$. Then $A(kr) = \{2kr\}$. By definition, $\{x\} = x - \lfloor x \rfloor$. We substitute this into the expression for $B(n,r)$:
4: $$ B(n,r) = \sum_{k=1}^n \{2kr\} = \sum_{k=1}^n (2kr - \lfloor 2kr \rfloor) = 2r \sum_{k=1}^n k - \sum_{k=1}^n \lfloor 2kr \rfloor = 2r \frac{n(n+1)}{2} - \sum_{k=1}^n \lfloor 2kr \rfloor. $$
5: Simplifying the first term, we have $B(n,r) = n(n+1)r - \sum_{k=1}^n \lfloor 2kr \rfloor$. The condition given in the problem is that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all $n \in \mathbb{Z}^+$. Substituting the simplified expression for $B(n,r)$:
6: $$ n(n+1)r - \left( n(n+1)r - \sum_{k=1}^n \lfloor 2kr \rfloor \right) = \sum_{k=1}^n \lfloor 2kr \rfloor. $$
7: Thus, the condition is that $S_n = \sum_{k=1}^n \lfloor 2kr \rfloor$ must be a multiple of $n$ for all $n \in \mathbb{Z}^+$. Let $x = 2r$. We seek all $x > 0$ such that $S_n = \sum_{k=1}^n \lfloor kx \rfloor \equiv 0 \pmod{n}$ for all $n \ge 1$.
8: 
9: If $x$ is an even integer, say $x = 2m$ for some $m \in \mathbb{Z}^+$, then
10: $$ S_n = \sum_{k=1}^n \lfloor 2km \rfloor = \sum_{k=1}^n 2km = 2m \frac{n(n+1)}{2} = mn(n+1). $$
11: Since $mn(n+1) = n \cdot (m(n+1))$ and $m(n+1)$ is an integer, $mn(n+1)$ is a multiple of $n$ for all $n$. This corresponds to $2r = 2m$, or $r = m$, where $m$ is a positive integer.
12: 
13: Now we show that no other $x > 0$ satisfies the condition. Let $\lfloor x \rfloor = a$ and $x = a + \delta$ with $0 \le \delta < 1$.
14: For $n=2$, $S_2 = \lfloor x \rfloor + \lfloor 2x \rfloor = a + \lfloor 2a + 2\delta \rfloor = 3a + \lfloor 2\delta \rfloor$. For $S_2$ to be even:
15: 1. If $\lfloor 2\delta \rfloor = 0$ (i.e., $0 \le \delta < 1/2$), then $3a$ must be even, so $a$ is even.
16: 2. If $\lfloor 2\delta \rfloor = 1$ (i.e., $1/2 \le \delta < 1$), then $3a$ must be odd, so $a$ is odd.
17: 
18: In Case 1 ($a$ even, $0 \le \delta < 1/2$), $S_n = a \frac{n(n+1)}{2} + \sum_{k=1}^n \lfloor k\delta \rfloor$. Since $a$ is even, $a \frac{n(n+1)}{2}$ is always a multiple of $n$. Thus, we require $\sum_{k=1}^n \lfloor k\delta \rfloor \equiv 0 \pmod{n}$ for all $n$. We prove $\lfloor n\delta \rfloor = 0$ for all $n \ge 1$ by induction. For $n=1$, $\lfloor \delta \rfloor = 0$ since $0 \le \delta < 1/2$. Assume $\lfloor k\delta \rfloor = 0$ for all $k < n$. Then $\sum_{k=1}^n \lfloor k\delta \rfloor = \sum_{k=1}^{n-1} 0 + \lfloor n\delta \rfloor = \lfloor n\delta \rfloor$. For this to be a multiple of $n$, we must have $\lfloor n\delta \rfloor = qn$ for some integer $q$. Since $0 \le \delta < 1/2$, we have $0 \le n\delta < n/2$, so $0 \le \lfloor n\delta \rfloor < n/2$. The only multiple of $n$ in this range is 0, so $\lfloor n\delta \rfloor = 0$. Since $\lfloor n\delta \rfloor = 0$ for all $n \ge 1$, we have $n\delta < 1$ for all $n \ge 1$, which implies $\delta = 0$. This implies $x = a$, an even integer.
19: 
20: In Case 2 ($a$ odd, $1/2 \le \delta < 1$), we prove $\lfloor n\delta \rfloor = n-1$ for all $n \ge 1$ by induction. For $n=1$, $\lfloor \delta \rfloor = 0 = 1-1$. For $n=2$, $S_2 = 3a + 0 + \lfloor 2\delta \rfloor \equiv 1 + \lfloor 2\delta \rfloor \equiv 0 \pmod{2}$ (since $a$ is odd), so $\lfloor 2\delta \rfloor = 1 = 2-1$. Assume $\lfloor k\delta \rfloor = k-1$ for all $k < n$. Then $\sum_{k=1}^{n-1} \lfloor k\delta \rfloor = \sum_{k=1}^{n-1} (k-1) = \frac{(n-2)(n-1)}{2}$. The condition $S_n \equiv 0 \pmod{n}$ becomes $a \frac{n(n+1)}{2} + \frac{(n-2)(n-1)}{2} + \lfloor n\delta \rfloor \equiv 0 \pmod{n}$. Since $a$ is odd, $a = 2m+1$, so $a \frac{n(n+1)}{2} = mn(n+1) + \frac{n(n+1)}{2} \equiv \frac{n(n+1)}{2} \pmod{n}$. Thus, $\frac{n(n+1)}{2} + \frac{n^2-3n+2}{2} + \lfloor n\delta \rfloor = \frac{2n^2-2n+2}{2} + \lfloor n\delta \rfloor = n^2-n+1 + \lfloor n\delta \rfloor \equiv 1 + \lfloor n\delta \rfloor \equiv 0 \pmod{n}$. Since $0 \le \delta < 1$, we have $0 \le \lfloor n\delta \rfloor \le n-1$, so $\lfloor n\delta \rfloor = n-1$. This implies $n-1 \le n\delta < n$, or $1 - 1/n \le \delta < 1$ for all $n \in \mathbb{Z}^+$. As $n \to \infty$, we obtain $1 \le \delta < 1$, a contradiction.
21: 
22: Thus, $x$ must be an even integer, which implies $r$ must be a positive integer.
23: 
24: The positive real numbers $r$ are all positive integers. \(\square\)

# Proof B

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
