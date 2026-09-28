# Problem

Define the sequence $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for all integers $n \ge 2$. Prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$.

# Proof A

1: To prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$, where the sequence is defined by $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$, we proceed by induction.
2: 
3: ### 1. Preliminary Lemma
4: **Lemma:** For integers $a > 1$ and $n, m \ge 1$, $a^n + 1$ divides $a^m + 1$ if and only if $m$ is an odd multiple of $n$.
5: 
6: *Proof:* 
7: If $m = (2k+1)n$ for some integer $k \ge 0$, then $a^m + 1 = (a^n)^{2k+1} + 1$. Using the factorization $y^{2k+1} + 1 = (y+1)(y^{2k} - y^{2k-1} + \dots + 1)$ with $y = a^n$, we see that $a^n + 1$ divides $a^m + 1$.
8: Conversely, suppose $a^n + 1 \mid a^m + 1$. Let $m = qn + r$ where $0 \le r < n$. Then
9: $a^m + 1 = a^r(a^n)^q + 1 \equiv a^r(-1)^q + 1 \pmod{a^n + 1}$.
10: For this to be $0 \pmod{a^n + 1}$, we must have $(-1)^q a^r + 1 \equiv 0 \pmod{a^n + 1}$.
11: If $q$ is even, $a^r + 1 \equiv 0 \pmod{a^n + 1}$. Since $0 \le r < n$, we have $1 < a^r + 1 < a^n + 1$, so this is impossible.
12: If $q$ is odd, $-a^r + 1 \equiv 0 \pmod{a^n + 1}$. This requires $a^r = 1$, which implies $r = 0$.
13: Thus, $m = qn$ with $q$ odd. $\square$
14: 
15: ### 2. Inductive Framework
16: We define two properties for $n \ge 1$:
17: - $P(n): x_n \mid 2^{x_n} + 2$
18: - $Q(n): x_n - 1 \mid 2^{x_n} + 1$
19: 
20: Note that $x_n = 2^{x_{n-1}} + 2$, so the goal $x_{n-1} \mid x_n$ for $n \ge 2$ is exactly the statement $P(n-1)$ for $n \ge 2$.
21: 
22: **Base Cases:**
23: - For $n=1$, $x_1 = 6$. $2^6 + 2 = 66$. Since $6 \mid 66$, $P(1)$ is true.
24: - For $n=1$, $x_1 - 1 = 5$. $2^6 + 1 = 65$. Since $5 \mid 65$, $Q(1)$ is true.
25: 
26: ### 3. Inductive Steps
27: **Part A: $Q(n) \implies P(n+1)$**
28: Assume $Q(n)$ is true: $x_n - 1 \mid 2^{x_n} + 1$.
29: We want to show $P(n+1): x_{n+1} \mid 2^{x_{n+1}} + 2$.
30: Substituting $x_{n+1} = 2^{x_n} + 2$:
31: $P(n+1) \iff 2^{x_n} + 2 \mid 2^{2^{x_n} + 2} + 2 \iff 2(2^{x_n-1} + 1) \mid 2(2^{2^{x_n} + 1} + 1) \iff 2^{x_n-1} + 1 \mid 2^{2^{x_n} + 1} + 1$.
32: By the Lemma, this holds if and only if $2^{x_n} + 1$ is an odd multiple of $x_n - 1$.
33: Since both $2^{x_n} + 1$ and $x_n - 1$ are odd, any integer quotient between them must be odd. Thus, $2^{x_n} + 1$ is an odd multiple of $x_n - 1$ if and only if $x_n - 1 \mid 2^{x_n} + 1$, which is $Q(n)$.
34: 
35: **Part B: $P(n) \implies Q(n+1)$**
36: Assume $P(n)$ is true: $x_n \mid 2^{x_n} + 2$.
37: We want to show $Q(n+1): x_{n+1} - 1 \mid 2^{x_{n+1}} + 1$.
38: Substituting $x_{n+1} - 1 = 2^{x_n} + 1$:
39: $Q(n+1) \iff 2^{x_n} + 1 \mid 2^{2^{x_n} + 2} + 1$.
40: By the Lemma, this holds if and only if $2^{x_n} + 2$ is an odd multiple of $x_n$.
41: Let $2^{x_n} + 2 = q x_n$. Then $q = \frac{2(2^{x_n-1} + 1)}{x_n}$.
42: For $n=1$, $x_1/2 = 3$ (odd). For $n \ge 2$, $x_n/2 = 2^{x_{n-1}-1} + 1$, which is odd because $x_{n-1} \ge 6$.
43: Thus, $q = \frac{2^{x_n-1} + 1}{x_n/2}$ is a ratio of two odd numbers. Therefore, $q$ is odd whenever it is an integer.
44: The condition that $q$ is an integer is exactly $x_n \mid 2^{x_n} + 2$, which is $P(n)$.
45: 
46: ### 4. Final Synthesis
47: We have $P(1)$ and $Q(1)$ as true. The implications $P(n) \implies Q(n+1)$ and $Q(n) \implies P(n+1)$ establish by induction that $P(n)$ is true for all $n \ge 1$.
48: Since $P(n-1)$ is the statement $x_{n-1} \mid 2^{x_{n-1}} + 2$ and $x_n = 2^{x_{n-1}} + 2$, it follows that $x_{n-1} \mid x_n$ for all $n \ge 2$.

# Proof B

1: To prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$, where $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$, it is sufficient to prove that $x_n$ divides $2^{x_n} + 2$ for all integers $n \ge 1$.
2: 
3: We define two statements $P(n)$ and $S(n)$ for $n \ge 1$:
4: $P(n)$: The quotient $q_n = \frac{2^{x_n} + 2}{x_n}$ is an odd integer.
5: $S(n)$: The quotient $r_n = \frac{2^{x_n} + 1}{x_n - 1}$ is an odd integer.
6: 
7: **Base Cases:**
8: For $n=1$, we have $x_1 = 6$.
9: $2^{x_1} + 2 = 2^6 + 2 = 66$. Then $q_1 = \frac{66}{6} = 11$, which is an odd integer. Thus, $P(1)$ is true.
10: For $n=1$, $x_1 - 1 = 5$ and $2^{x_1} + 1 = 2^6 + 1 = 65$. Then $r_1 = \frac{65}{5} = 13$, which is an odd integer. Thus, $S(1)$ is true.
11: 
12: **Inductive Step:**
13: We prove that $P(n) \implies S(n+1)$ and $S(n) \implies P(n+1)$.
14: 
15: 1.  **Proof that $P(n) \implies S(n+1)$:**
16:     Assume $P(n)$ is true. We want to show that $S(n+1)$ is true, i.e., $x_{n+1} - 1$ divides $2^{x_{n+1}} + 1$ and the quotient is odd.
17:     From the definition, $x_{n+1} - 1 = (2^{x_n} + 2) - 1 = 2^{x_n} + 1$.
18:     We need to show $2^{x_n} + 1 \mid 2^{x_{n+1}} + 1$. Let $M = 2^{x_n} + 1$. Then $2^{x_n} \equiv -1 \pmod{M}$.
19:     The expression $2^{x_{n+1}} + 1$ can be written as $2^{2^{x_n} + 2} + 1$.
20:     Since $P(n)$ is true, $2^{x_n} + 2 = q_n x_n$ where $q_n$ is an odd integer.
21:     Then $2^{x_{n+1}} = 2^{q_n x_n} = (2^{x_n})^{q_n}$.
22:     Substituting the congruence $2^{x_n} \equiv -1 \pmod{M}$:
23:     $2^{x_{n+1}} \equiv (-1)^{q_n} \pmod{M}$.
24:     Since $q_n$ is odd, $2^{x_{n+1}} \equiv -1 \pmod{M}$, so $M \mid 2^{x_{n+1}} + 1$.
25:     Because both $2^{x_{n+1}} + 1$ and $x_{n+1} - 1$ are odd, their quotient $r_{n+1}$ must be odd. Thus, $S(n+1)$ is true.
26: 
27: 2.  **Proof that $S(n) \implies P(n+1)$:**
28:     Assume $S(n)$ is true. We want to show that $P(n+1)$ is true, i.e., $x_{n+1}$ divides $2^{x_{n+1}} + 2$ and the quotient is odd.
29:     $x_{n+1} = 2^{x_n} + 2$. Let $N = x_{n+1}$. We want to show $N \mid 2^N + 2$.
30:     $q_{n+1} = \frac{2^N + 2}{N} = \frac{2(2^{N-1} + 1)}{2(2^{x_n-1} + 1)} = \frac{2^{N-1} + 1}{2^{x_n-1} + 1}$.
31:     Let $L = 2^{x_n-1} + 1$. We need to show $L \mid 2^{N-1} + 1$.
32:     Note that $2^{x_n-1} \equiv -1 \pmod{L}$, which implies $2^{2(x_n-1)} \equiv 1 \pmod{L}$.
33:     The exponent is $N-1 = 2^{x_n} + 1$.
34:     Since $S(n)$ is true, $x_n - 1 \mid 2^{x_n} + 1$ and the quotient $r_n$ is odd.
35:     Thus, $N-1 = r_n(x_n - 1)$.
36:     $2^{N-1} = (2^{x_n-1})^{r_n} \equiv (-1)^{r_n} \pmod{L}$.
37:     Since $r_n$ is odd, $2^{N-1} \equiv -1 \pmod{L}$, so $L \mid 2^{N-1} + 1$.
38:     Because both $2^{N-1} + 1$ and $L$ are odd, the quotient $q_{n+1}$ must be odd. Thus, $P(n+1)$ is true.
39: 
40: **Conclusion:**
41: By induction, $P(n)$ and $S(n)$ are true for all $n \ge 1$. Since $P(n)$ is true, $x_n \mid 2^{x_n} + 2$ for all $n \ge 1$.
42: For any $n \ge 2$, we have $x_n = 2^{x_{n-1}} + 2$.
43: Since $P(n-1)$ is true, $x_{n-1} \mid 2^{x_{n-1}} + 2$.
44: Therefore, $x_{n-1} \mid x_n$ for all integers $n \ge 2$.
45: 
46: \(\square\)
