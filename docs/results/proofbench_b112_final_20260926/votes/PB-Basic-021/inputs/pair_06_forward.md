# Problem

Define the sequence $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for all integers $n \ge 2$. Prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$.

# Proof A

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
