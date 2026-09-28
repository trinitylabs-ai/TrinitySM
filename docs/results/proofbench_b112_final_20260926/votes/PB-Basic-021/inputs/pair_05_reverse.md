# Problem

Define the sequence $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for all integers $n \ge 2$. Prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$.

# Proof A

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

# Proof B

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
