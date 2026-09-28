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
