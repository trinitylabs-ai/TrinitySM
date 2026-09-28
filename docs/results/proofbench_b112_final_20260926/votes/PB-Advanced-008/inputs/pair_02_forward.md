# Problem

Let $\left\{F_{n}\right\}_{n \geq 1}$ be a sequence of integers satisfying $F_{1}=1$ and for $n \geq 2$,
 \[
 F_{n}=n^{F_{n-1}}.
 \]
 For example, $F_3 = 3^2= 9$ and $F_4 = 4^9$.

 Prove that for any positive integers $a, c$ and integer $b$, there exists a positive integer $n$ such that the following expression is an integer:

 \[
 \frac{a^{F_{n}}+n-b}{c}.
 \]

# Proof A

1: To prove that for any positive integers $a, c$ and integer $b$, there exists a positive integer $n$ such that the expression $\frac{a^{F_n}+n-b}{c}$ is an integer, we must show that the congruence $a^{F_n} + n \equiv b \pmod{c}$ has a solution $n \in \mathbb{Z}^+$.
2: 
3: **1. The Periodicity of $F_n \pmod{m}$**
4: Let $F_1 = 1$ and $F_n = n^{F_{n-1}}$ for $n \geq 2$. For any positive integer $m$, we claim that the sequence $F_n \pmod{m}$ is eventually periodic. Let $T(m)$ be a period of this sequence.
5: For $m=1$, $T(1)=1$. For $m \geq 2$, we have $F_n = n^{F_{n-1}}$. For $n$ sufficiently large, $n \equiv n+T \pmod{m}$ if $T$ is a multiple of $m$. Furthermore, by the general version of Euler's Theorem, if $F_{n-1} \equiv F_{n-1+T} \pmod{\phi(m)}$ and $F_{n-1} \geq \phi(m)$, then $n^{F_{n-1}} \equiv (n+T)^{F_{n-1+T}} \pmod{m}$.
6: Thus, a period $T(m)$ can be constructed as $T(m) = \text{lcm}(m, T(\phi(m)))$. By iterating this relation, we find that
7: \[ T(m) = \text{lcm}(m, \phi(m), \phi(\phi(m)), \dots, 1) \]
8: is a valid period for the sequence $F_n \pmod{m}$ for $n$ sufficiently large.
9: 
10: **2. The Shift Property of $g(n)$**
11: Define $g_c(n) = a^{F_n} + n \pmod{c}$. Let $L = T(\phi(c))$. For $n$ sufficiently large, we have $F_{n+L} \equiv F_n \pmod{\phi(c)}$. By the general version of Euler's Theorem, $a^x \equiv a^{x \pmod{\phi(c)} + \phi(c)} \pmod{c}$ for $x \geq \phi(c)$. Since $F_n$ grows rapidly, for $n$ large enough, $F_n \geq \phi(c)$, and thus $a^{F_{n+L}} \equiv a^{F_n} \pmod{c}$. Consequently, there exists a threshold $K_{shift}$ such that for all $n \geq K_{shift}$:
12: \[ g_c(n+L) = a^{F_{n+L}} + n + L \equiv a^{F_n} + n + L \equiv g_c(n) + L \pmod{c}. \]
13: 
14: **3. Induction on $c$**
15: Let $P(c)$ be the statement: "For any positive integers $a, K$ and integer $b$, there exists $n \geq K$ such that $g_c(n) \equiv b \pmod{c}$."
16: Base case: $P(1)$ is trivial since any $n \geq K$ satisfies $g_1(n) \equiv b \pmod 1$.
17: Inductive step: Assume $P(c')$ is true for all $c' < c$. Let $L = T(\phi(c))$ and $c' = \gcd(L, c)$. We first show $c' < c$ by proving $c \nmid L$.
18: Let $p$ be the largest prime factor of $c$, and let $v_p(c) = k \geq 1$. The prime factors of $\phi(c)$ are the prime factors of $c$ and the prime factors of $q-1$ for $q|c$. Since $p$ is the largest prime factor of $c$, for any $q|c$, $q \leq p$, so $q-1 < p$. Thus, the only prime factor of $\phi(c)$ that is $\geq p$ is $p$ itself. Specifically, $v_p(\phi(c)) = v_p(c \prod_{q|c} \frac{q-1}{q}) = k + \sum_{q|c} v_p(q-1) - v_p(p) = k + 0 - 1 = k-1$.
19: For $m \geq 1$, let $\phi^{(m)}(c)$ denote the $m$-th iterate of the totient function. Since the only prime factor of $\phi^{(m)}(c)$ that is $\geq p$ is $p$, and $v_p(\phi(m)) = v_p(m)-1$ if $v_p(m)>0$ and $0$ otherwise, it follows that $v_p(\phi^{(m)}(c))$ is a non-increasing sequence. Thus, $v_p(L) = \max_{m \geq 1} v_p(\phi^{(m)}(c)) = v_p(\phi(c)) = k-1$.
20: Since $v_p(L) = k-1 < k = v_p(c)$, we have $c \nmid L$, and thus $c' = \gcd(L, c) < c$.
21: 
22: By the induction hypothesis $P(c')$, for any $a, b$ and a sufficiently large $K'$, there exists $n_0 \geq K'$ such that $g_{c'}(n_0) \equiv b \pmod{c'}$. We choose $K'$ such that $n_0 \geq K$ and $n_0 \geq K_{shift}$.
23: We seek $n \geq K$ such that $g_c(n) \equiv b \pmod{c}$. Let $n = n_0 + mL$ for some $m \geq 0$. By the shift property:
24: \[ g_c(n_0 + mL) \equiv g_c(n_0) + mL \pmod{c}. \]
25: We want to solve for $m$:
26: \[ mL \equiv b - g_c(n_0) \pmod{c}. \]
27: This linear congruence in $m$ has a solution if and only if $\gcd(L, c) \mid (b - g_c(n_0))$, which is $c' \mid (b - g_c(n_0))$, or $g_c(n_0) \equiv b \pmod{c'}$. Since $g_c(n_0) \pmod{c'} = (a^{F_{n_0}} + n_0) \pmod{c'} = g_{c'}(n_0)$, this is exactly the condition $g_{c'}(n_0) \equiv b \pmod{c'}$ provided by $P(c')$. By choosing $m \geq 0$, we ensure $n \geq n_0 \geq K$.
28: 
29: Thus, for any $a, c, b$, there exists $n$ such that $a^{F_n} + n \equiv b \pmod{c}$, which means $\frac{a^{F_n} + n - b}{c}$ is an integer.

# Proof B

1: To prove that for any positive integers $a, c$ and integer $b$, there exists a positive integer $n$ such that the expression $\frac{a^{F_n} + n - b}{c}$ is an integer, we must show that the congruence
2: \[ n + a^{F_n} \equiv b \pmod{c} \]
3: has a solution in $\mathbb{Z}^+$.
4: 
5: **1. Periodicity of the sequence $F_n \pmod{m}$**
6: Let $m_0 = c$ and define the $\phi$-chain $m_{i+1} = \phi(m_i)$ for $i \ge 0$. Since $\phi(m) < m$ for $m > 1$, there exists $k$ such that $m_k = 1$.
7: We claim that for each $i \in \{0, \dots, k\}$, the sequence $F_n \pmod{m_i}$ is periodic for $n$ sufficiently large.
8: - For $m_k = 1$, $F_n \equiv 0 \pmod{1}$ for all $n$, so it is periodic with period $T_k = 1$.
9: - For $m_i$ with $i < k$, we have $F_n \equiv n^{F_{n-1}} \pmod{m_i}$. If $T_i$ is a multiple of $m_i$ and $T_{i+1}$ (the period of $F_n \pmod{m_{i+1}}$), then for $n$ sufficiently large:
10:   \[ F_{n+T_i} \equiv (n+T_i)^{F_{n+T_i-1}} \equiv n^{F_{n+T_i-1}} \pmod{m_i}. \]
11:   Since $T_i$ is a multiple of $T_{i+1}$, $F_{n+T_i-1} \equiv F_{n-1} \pmod{m_{i+1}}$. Because $m_{i+1} = \phi(m_i)$, the generalized Euler's Totient Theorem states that $x^u \equiv x^v \pmod{m}$ if $u \equiv v \pmod{\phi(m)}$ and $u, v \ge \phi(m)$. Since $F_n$ grows rapidly ($F_1=1, F_2=2, F_3=9, F_4=4^9, \dots$), $F_{n-1} \ge \phi(m_i)$ for $n \ge 5$ (or larger if $\phi(m_i)$ is very large). Thus,
12:   \[ n^{F_{n+T_i-1}} \equiv n^{F_{n-1}} \equiv F_n \pmod{m_i}. \]
13:   Hence, $T_i = \text{lcm}(m_i, T_{i+1})$ is a period for $n$ sufficiently large. By induction, $T_1 = \text{lcm}(m_1, m_2, \dots, m_k)$.
14: 
15: **2. Analysis of $d = \gcd(T_1, c)$**
16: We show that $d = \gcd(T_1, c) < c$ for $c > 1$. Let $p$ be the largest prime factor of $c$, and let $v = v_p(c)$.
17: The value of $m_1 = \phi(c)$ is $m_1 = c \prod_{q|c} \frac{q-1}{q}$. Since $p$ is the largest prime factor of $c$, for any prime $q|c$, $q \le p$, so $q-1 < p$, which implies $v_p(q-1) = 0$. Thus, $v_p(m_1) = v_p(c) - 1 = v-1$.
18: For $i \ge 1$, the prime factors of $m_i$ are the prime factors of $\phi(m_{i-1})$. Since the largest prime factor of $m_1$ is at most $p$, any prime factor $r$ of $m_i$ satisfies $r \le p$. If $v_p(m_i) > 0$, then $v_p(m_{i+1}) = v_p(\phi(m_i)) = v_p(m_i) - 1$ because $p$ is the only prime factor of $m_i$ that is not strictly less than $p$.
19: Thus, $v_p(T_1) = \max(v_p(m_1), \dots, v_p(m_k)) = v_p(m_1) = v-1$.
20: Since $v_p(T_1) = v-1 < v = v_p(c)$, $c$ does not divide $T_1$, so $d = \gcd(T_1, c) < c$.
21: 
22: **3. Inductive Proof**
23: We proceed by induction on $c$. Let $P(c)$ be the statement: "For any $b \in \mathbb{Z}$ and any $N \in \mathbb{Z}^+$, there exists $n > N$ such that $n + a^{F_n} \equiv b \pmod{c}$."
24: - Base case: For $c=1$, $n + a^{F_n} \equiv b \pmod{1}$ is always true for any $n > N$.
25: - Inductive step: Assume $P(c')$ is true for all $c' < c$.
26: Let $b \in \mathbb{Z}$ and $N \in \mathbb{Z}^+$. Let $T_1$ be the period of $F_n \pmod{\phi(c)}$ for $n \ge N_{\phi(c)}$, and let $d = \gcd(T_1, c)$. Since $d < c$, by the inductive hypothesis $P(d)$, there exists $n_0 > \max(N, N_{\phi(c)}, 5, \text{threshold for } F_n \ge \phi(c))$ such that $n_0 + a^{F_{n_0}} \equiv b \pmod{d}$.
27: Define $g(n) = n + a^{F_n} \pmod{c}$. For $n \ge N_{\phi(c)}$, we have $F_{n+T_1} \equiv F_n \pmod{\phi(c)}$. Since $F_n \ge \phi(c)$ for the chosen $n_0$, we have $a^{F_{n+T_1}} \equiv a^{F_n} \pmod{c}$ by the generalized Euler's Totient Theorem. Thus,
28: \[ g(n + T_1) = (n + T_1) + a^{F_{n+T_1}} \equiv n + T_1 + a^{F_n} \equiv g(n) + T_1 \pmod{c}. \]
29: By iteration, $g(n_0 + kT_1) \equiv g(n_0) + kT_1 \pmod{c}$ for $k \in \mathbb{Z}^+$.
30: We seek $k$ such that $kT_1 \equiv b - g(n_0) \pmod{c}$. This linear congruence has a solution if and only if $\gcd(T_1, c)$ divides $b - g(n_0)$.
31: Since $\gcd(T_1, c) = d$ and $g(n_0) = n_0 + a^{F_{n_0}} \equiv b \pmod{d}$, the condition $d \mid (b - g(n_0))$ is satisfied.
32: Choosing a sufficiently large $k$ ensures $n = n_0 + kT_1 > N$ and $n + a^{F_n} \equiv b \pmod{c}$.
33: Thus $P(c)$ is true. By induction, the statement holds for all $c \in \mathbb{Z}^+$.
