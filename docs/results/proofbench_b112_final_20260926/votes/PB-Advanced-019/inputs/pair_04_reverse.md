# Problem

For a real number $r$, let $A(r)$ denote the fractional part of $2r$ in its decimal representation. For a real number $r$ and a positive integer $n$, define $B(n,r)$ as
 $$
 B(n,r)=\sum_{k=1}^n A(kr).
 $$
 Find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$.

# Proof A

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

# Proof B

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
