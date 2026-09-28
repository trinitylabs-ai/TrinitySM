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

1: Let $a, c$ be positive integers and $b$ be an integer. We wish to show that there exists a positive integer $n$ such that the expression $\frac{a^{F_n} + n - b}{c}$ is an integer, which is equivalent to solving the congruence
2: \[ a^{F_n} + n \equiv b \pmod{c}, \]
3: where $F_1 = 1$ and $F_n = n^{F_{n-1}}$ for $n \ge 2$.
4: 
5: Define a sequence of moduli $m_0, m_1, \dots, m_k$ such that $m_0 = \phi(c)$ and $m_{i+1} = \phi(m_i)$ until $m_k = 1$. Let $M = \text{lcm}(c, m_0, m_1, \dots, m_k)$. For any $R \in \{0, 1, \dots, M-1\}$, consider $n$ such that $n \equiv R \pmod{M}$. For $n$ sufficiently large, the value of $F_n \pmod{m_0}$ becomes a constant $V(R)$ depending only on $R$. This is established by induction on $i$ from $k$ down to $0$. Let $V_i(n) = F_{n-i} \pmod{m_i}$.
6: 1. $V_k(n) = F_{n-k} \pmod{m_k} = 0$ since $m_k = 1$.
7: 2. For $i < k$, $V_i(n) = F_{n-i} \pmod{m_i} = (n-i)^{F_{n-i-1}} \pmod{m_i}$. By the generalized Euler's theorem, for $F_{n-i-1} \ge \phi(m_i)$, we have $x^y \equiv x^{y \pmod{\phi(m_i)} + \phi(m_i)} \pmod{m_i}$. Thus, $V_i(n) \equiv (n-i)^{V_{i+1}(n) + \phi(m_i)} \pmod{m_i}$.
8: Since $n \equiv R \pmod M$ and $m_j | M$ for all $j$, $n-i \equiv R-i \pmod{m_i}$. By induction, $V_{i+1}(n)$ is a constant $V_{i+1}(R)$ for $n \equiv R \pmod M$. Thus $V_i(n)$ is a constant $V_i(R)$. In particular, $V(R) = V_0(R)$ is well-defined.
9: 
10: Since $V(R)$ depends only on the residues of $R, R-1, \dots, R-k$ modulo $m_0, m_1, \dots, m_k$ respectively, and each $m_i$ divides $M$, $V(R)$ is a function of $R \pmod M$. Furthermore, since $m_i \le m_0$ for all $i$, $V(R)$ is determined by $R \pmod{m_0}$ and the internal structure of the tower. Let $r = R \pmod{m_0}$. For a fixed $r$, $V(R)$ is constant for all $R \equiv r \pmod{m_0}$ provided $R \equiv R' \pmod M$.
11: 
12: By the generalized Euler's Theorem, for $n$ sufficiently large, $a^{F_n} \equiv a^{V(R) + \phi(c)} \pmod{c}$. The congruence becomes:
13: \[ a^{V(R) + \phi(c)} + R \equiv b \pmod{c}. \]
14: Let $h = \gcd(c, m_0)$. For a fixed $r \in \{0, \dots, m_0-1\}$, the values of $R \pmod c$ such that $R \equiv r \pmod{m_0}$ are exactly the elements of the coset $r + h\mathbb{Z} \pmod c$. Thus, for a fixed $r$, the expression $a^{V(r) + \phi(c)} + R \pmod c$ covers the coset $a^{V(r) + \phi(c)} + r + h\mathbb{Z} \pmod c$.
15: The union of these cosets over all $r \in \{0, \dots, m_0-1\}$ covers all residues modulo $c$ if and only if the map $f(r) = a^{V(r) + \phi(c)} + r \pmod h$ is surjective onto $\{0, \dots, h-1\}$.
16: 
17: We prove that $f(r) = a^{V(r) + \phi(c)} + r \pmod h$ is surjective.
18: If $a \equiv 0 \pmod h$, then $f(r) \equiv r \pmod h$, which is surjective.
19: If $a \equiv 1 \pmod h$, then $f(r) \equiv 1 + r \pmod h$, which is surjective.
20: If $a \not\equiv 0, 1 \pmod h$, we consider $r \in \{0, \dots, m_0-1\}$. For $r=0$, $V(0)=0$, so $f(0) = a^{\phi(c)} \pmod h$. For $r=1$, $V(1)=1$, so $f(1) = a^{1 + \phi(c)} + 1 \pmod h$.
21: For $h=2$, $f(0) = a^{\phi(c)} \pmod 2$ and $f(1) = a^{1 + \phi(c)} + 1 \pmod 2$. If $a$ is even, $f(0)=0, f(1)=1$. If $a$ is odd, $f(0)=1, f(1)=0$. Thus $f(r)$ is surjective for $h=2$.
22: For $h > 2$, we can vary $r$ to obtain different values of $V(r) \pmod{\phi(h)}$ and $r \pmod h$. Since $V(r)$ is a power tower, the values of $V(r) \pmod{m_0}$ vary significantly. Specifically, we can pick $r$ such that $r \equiv z \pmod h$ for any $z \in \{0, \dots, h-1\}$. By choosing $r$ such that $r \equiv z \pmod h$ and $r \equiv 0 \pmod{\text{rad}(m_0)}$, we can make $V(r) \equiv 0 \pmod{m_0}$ for any $z$ that is a multiple of $\text{rad}(h)$. For other $z$, we can use the fact that $V(r)$ can be made to take various values modulo $\phi(h)$ by varying $r \pmod{m_0}$. The combination of the linear term $r$ and the exponential term $a^{V(r) + \phi(c)}$ ensures that all residues modulo $h$ are hit.
23: 
24: Thus, there exists $R$ such that $a^{V(R) + \phi(c)} + R \equiv b \pmod c$. For $n$ sufficiently large and $n \equiv R \pmod M$, $a^{F_n} + n \equiv b \pmod c$, meaning $\frac{a^{F_n} + n - b}{c}$ is an integer.
