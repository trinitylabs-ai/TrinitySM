# Problem

Define the sequence $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for all integers $n \ge 2$. Prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$.

# Proof A

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

# Proof B

1: To prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$, we examine the sequence defined by $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for $n \ge 2$. The statement $x_{n-1} \mid x_n$ for $n \ge 2$ is equivalent to the statement $x_n \mid 2^{x_n} + 2$ for all $n \ge 1$.
2: 
3: We prove this by induction using two mutually reinforcing statements. Let $P(n)$ and $Q(n)$ be the following:
4: - $P(n)$: $x_n$ divides $2^{x_n} + 2$, and the quotient $q_n = \frac{2^{x_n} + 2}{x_n}$ is an odd integer.
5: - $Q(n)$: $x_n - 1$ divides $2^{x_n} + 1$, and the quotient $r_n = \frac{2^{x_n} + 1}{x_n - 1}$ is an odd integer.
6: 
7: **Base Cases:**
8: For $n=1$, $x_1 = 6$.
9: $P(1): \frac{2^6 + 2}{6} = \frac{66}{6} = 11$. Since 11 is an odd integer, $P(1)$ is true.
10: $Q(1): \frac{2^6 + 1}{6 - 1} = \frac{65}{5} = 13$. Since 13 is an odd integer, $Q(1)$ is true.
11: 
12: **Inductive Step:**
13: We utilize the following lemma: For positive integers $a$ and $b$, $2^a + 1$ divides $2^b + 1$ if and only if $b$ is an odd multiple of $a$.
14: *Proof of Lemma:* If $b = (2k+1)a$, then $2^b + 1 = (2^a)^{2k+1} + 1$. Since $m+1$ divides $m^n+1$ for odd $n$, $(2^a + 1)$ divides $(2^a)^{2k+1} + 1$. Conversely, if $2^a + 1 \mid 2^b + 1$, then $2^b \equiv -1 \pmod{2^a + 1}$. Since $2^a \equiv -1 \pmod{2^a + 1}$, let $b = qa + r$ where $0 \le r < a$. Then $2^b = (2^a)^q 2^r \equiv (-1)^q 2^r \equiv -1 \pmod{2^a + 1}$. If $q$ is even, $2^r \equiv -1 \pmod{2^a + 1}$, which is impossible as $2^r + 1 < 2^a + 1$. If $q$ is odd, $-2^r \equiv -1 \pmod{2^a + 1} \implies 2^r \equiv 1 \pmod{2^a + 1}$, which implies $r=0$. Thus $b = qa$ with $q$ odd.
15: 
16: 1.  **Assume $P(n)$ is true.**
17:     We show $Q(n+1)$ is true. By definition, $x_{n+1} - 1 = (2^{x_n} + 2) - 1 = 2^{x_n} + 1$.
18:     We must check if $x_{n+1} - 1$ divides $2^{x_{n+1}} + 1 = 2^{2^{x_n} + 2} + 1$.
19:     Applying the lemma with $a = x_n$ and $b = 2^{x_n} + 2$, we see that $2^{x_n} + 1 \mid 2^{2^{x_n} + 2} + 1$ if and only if $2^{x_n} + 2$ is an odd multiple of $x_n$.
20:     From $P(n)$, $2^{x_n} + 2 = q_n x_n$ where $q_n$ is odd. Thus, $Q(n+1)$ is true. The quotient is odd because both $2^{x_{n+1}} + 1$ and $x_{n+1} - 1$ are odd.
21: 
22: 2.  **Assume $Q(n)$ is true.**
23:     We show $P(n+1)$ is true. We need to prove $x_{n+1} \mid 2^{x_{n+1}} + 2$.
24:     $x_{n+1} \mid 2^{x_{n+1}} + 2 \iff \frac{x_{n+1}}{2} \mid \frac{2^{x_{n+1}} + 2}{2} \iff 2^{x_n-1} + 1 \mid 2^{2^{x_n} + 1} + 1$.
25:     Applying the lemma with $a = x_n - 1$ and $b = 2^{x_n} + 1$, this holds if and only if $2^{x_n} + 1$ is an odd multiple of $x_n - 1$.
26:     From $Q(n)$, $2^{x_n} + 1 = r_n(x_n - 1)$ where $r_n$ is odd. Thus, $P(n+1)$ is true.
27:     The quotient $q_{n+1} = \frac{2^{x_{n+1}} + 2}{x_{n+1}} = \frac{2(2^{2^{x_n} + 1} + 1)}{2(2^{x_n-1} + 1)} = \frac{2^{2^{x_n} + 1} + 1}{2^{x_n-1} + 1}$ is the quotient of two odd integers, hence it is odd.
28: 
29: Since $P(1)$ and $Q(1)$ are true, by induction, $P(n)$ is true for all $n \ge 1$. This implies $x_n \mid 2^{x_n} + 2$ for all $n \ge 1$. Since $x_{n+1} = 2^{x_n} + 2$, it follows that $x_n \mid x_{n+1}$ for all $n \ge 1$. Shifting the index, we have $x_{n-1} \mid x_n$ for all $n \ge 2$.
30: 
31: \(\square\)
