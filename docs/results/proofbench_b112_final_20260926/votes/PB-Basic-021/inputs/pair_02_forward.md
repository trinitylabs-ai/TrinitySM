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

1: To prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$, we observe that $x_n = 2^{x_{n-1}} + 2$. Thus, the condition $x_{n-1} \mid x_n$ is equivalent to proving that $x_n \mid 2^{x_n} + 2$ for all $n \ge 1$.
2: 
3: Let $P(n)$ be the statement $x_n \mid 2^{x_n} + 2$ and $R(n)$ be the statement $x_n - 1 \mid 2^{x_n} + 1$. We will prove that both $P(n)$ and $R(n)$ are true for all $n \ge 1$ by induction.
4: 
5: **Base Case:**
6: For $n=1$, $x_1 = 6$.
7: $P(1): 6 \mid 2^6 + 2 = 66$. Since $66 = 6 \times 11$, $P(1)$ is true.
8: $R(1): x_1 - 1 = 5$ and $2^{x_1} + 1 = 2^6 + 1 = 65$. Since $65 = 5 \times 13$, $R(1)$ is true.
9: 
10: **Inductive Step:**
11: Assume $P(n)$ and $R(n)$ are true for some $n \ge 1$. We show that $P(n+1)$ and $R(n+1)$ are also true.
12: 
13: First, we prove $R(n) \implies P(n+1)$.
14: By definition, $x_{n+1} = 2^{x_n} + 2$. The statement $P(n+1)$ is $x_{n+1} \mid 2^{x_{n+1}} + 2$.
15: We can rewrite the terms as:
16: $x_{n+1} = 2(2^{x_n-1} + 1)$
17: $2^{x_{n+1}} + 2 = 2(2^{x_{n+1}-1} + 1) = 2(2^{2^{x_n} + 1} + 1)$
18: Thus, $P(n+1)$ is equivalent to $2^{x_n-1} + 1 \mid 2^{2^{x_n} + 1} + 1$.
19: We use the lemma that for any positive integers $k, m$, $2^k + 1 \mid 2^m + 1$ if and only if $m/k$ is an odd integer.
20: Here $k = x_n - 1$ and $m = 2^{x_n} + 1$. The condition for $P(n+1)$ to be true is that $\frac{2^{x_n} + 1}{x_n - 1}$ is an odd integer.
21: By the inductive hypothesis $R(n)$, we have $x_n - 1 \mid 2^{x_n} + 1$. Since $x_n$ is even for all $n \ge 1$ (as $x_1=6$ and $x_n=2^{x_{n-1}}+2$), both $x_n - 1$ and $2^{x_n} + 1$ are odd. Therefore, their quotient must also be odd. This proves $P(n+1)$.
22: 
23: Next, we prove $P(n) \implies R(n+1)$.
24: The statement $R(n+1)$ is $x_{n+1} - 1 \mid 2^{x_{n+1}} + 1$.
25: Substituting the definition of $x_{n+1}$, we have $x_{n+1} - 1 = 2^{x_n} + 1$.
26: Thus, $R(n+1)$ is $2^{x_n} + 1 \mid 2^{x_{n+1}} + 1$.
27: Using the same lemma, this holds if $x_{n+1}/x_n$ is an odd integer.
28: We have $x_{n+1}/x_n = (2^{x_n} + 2)/x_n$.
29: By the inductive hypothesis $P(n)$, we know $x_n \mid 2^{x_n} + 2$, so this quotient is an integer.
30: To check its parity, we look at the 2-adic valuation $v_2(x)$.
31: For $x_1=6$, $v_2(x_1) = 1$. For $n \ge 2$, $x_n = 2^{x_{n-1}} + 2 = 2(2^{x_{n-1}-1} + 1)$. Since $x_{n-1}-1 \ge 1$, the term $2^{x_{n-1}-1} + 1$ is odd, meaning $v_2(x_n) = 1$ for all $n \ge 1$.
32: Then $v_2(x_{n+1}/x_n) = v_2(x_{n+1}) - v_2(x_n) = 1 - 1 = 0$.
33: This implies that $x_{n+1}/x_n$ is an odd integer. This proves $R(n+1)$.
34: 
35: Since $P(1)$ and $R(1)$ are true, and $P(n) \implies R(n+1)$ and $R(n) \implies P(n+1)$, it follows by induction that $P(n)$ and $R(n)$ are true for all $n \ge 1$.
36: Specifically, $P(n-1)$ is true for all $n \ge 2$, meaning $x_{n-1} \mid 2^{x_{n-1}} + 2$.
37: Since $x_n = 2^{x_{n-1}} + 2$, we conclude that $x_{n-1} \mid x_n$ for all $n \ge 2$.
38: 
39: \(\square\)
