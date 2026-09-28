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

# Proof B

1: To prove that for any positive integers $a, c$ and integer $b$, there exists a positive integer $n$ such that the expression $\frac{a^{F_n} + n - b}{c}$ is an integer, we must show that the congruence
2: \[ a^{F_n} + n \equiv b \pmod{c} \]
3: has a solution for $n \in \mathbb{Z}^+$, where the sequence $\{F_n\}$ is defined by $F_1=1$ and $F_n = n^{F_{n-1}}$ for $n \geq 2$.
4: 
5: Let $m_0 = c$ and define a sequence of integers $m_{i+1} = \phi(m_i)$ for $i \geq 0$. It is a known property of the Euler totient function that this sequence strictly decreases until it reaches $m_k = 1$ for some $k \in \mathbb{N}$. Let $L = \text{lcm}(m_1, m_2, \dots, m_k)$.
6: 
7: We first establish the stability of $F_n \pmod{m_i}$. For $n$ sufficiently large, $F_n$ exceeds any constant. According to the generalized Euler's Theorem, for $y \geq \phi(m)$, $x^y \equiv x^{\phi(m) + (y \pmod{\phi(m)})} \pmod{m}$.
8: For $n \equiv r \pmod L$, we show by induction on $j$ (from $k$ down to 1) that $F_{n-j} \pmod{m_j}$ is a constant $v_j(r)$ for $n$ sufficiently large.
9: For $j=k$, $F_{n-k} \equiv 0 \pmod{m_k}$ since $m_k=1$.
10: For $j < k$, $F_{n-j} = (n-j)^{F_{n-j-1}}$. Since $n \equiv r \pmod L$, $n-j \equiv r-j \pmod{m_j}$. Also, $F_{n-j-1} \pmod{m_{j+1}}$ is a constant $v_{j+1}(r)$ by the inductive hypothesis, and $m_{j+1} = \phi(m_j)$. Thus, for $n$ large,
11: \[ F_{n-j} \equiv (r-j)^{\phi(m_j) + v_{j+1}(r)} \pmod{m_j}, \]
12: which is a constant $v_j(r)$ depending only on $r \pmod L$. In particular, for $n \equiv r \pmod L$ and $n$ sufficiently large, $F_n \pmod{m_1}$ is a constant $v_1(r)$.
13: 
14: Next, we consider the expression $a^{F_n} + n \pmod{c}$. For $n$ large, $F_n \geq \phi(c) = m_1$. By the generalized Euler's Theorem:
15: \[ a^{F_n} \equiv a^{m_1 + (F_n \pmod{m_1})} \pmod{c}. \]
16: Since $F_n \pmod{m_1}$ is the constant $v_1(r)$ for $n \equiv r \pmod L$, we have $a^{F_n} \equiv a^{m_1 + v_1(r)} \pmod{c}$ for $n \equiv r \pmod L$. Let $W(r) = a^{m_1 + v_1(r)} \pmod{c}$.
17: We want to solve $W(r) + n \equiv b \pmod{c}$ for $n \equiv r \pmod L$. Let $n = qL + r$. The congruence becomes:
18: \[ W(r) + qL + r \equiv b \pmod{c} \implies qL \equiv b - r - W(r) \pmod{c}. \]
19: This linear congruence in $q$ has a solution if and only if $d = \gcd(L, c)$ divides $b - r - W(r)$. Thus, we need to show that the map $h(r) = W(r) + r \pmod d$ is surjective for $r \in \{1, \dots, L\}$.
20: 
21: Let $g = \gcd(m_1, d)$. For any $x \in \{0, \dots, m_1-1\}$, let $r \in \{1, \dots, L\}$ such that $r \equiv x \pmod{m_1}$. Since $m_1 \mid L$, for a fixed $x$, as $r$ varies over the set $\{r \in \{1, \dots, L\} : r \equiv x \pmod{m_1}\}$, the value $r \pmod d$ covers the coset $x + g\mathbb{Z} \pmod d$.
22: For $x=0$, picking $r \in \{2, \dots, L\}$ such that $r \equiv 0 \pmod{m_1}$ gives $v_1(r) \equiv 0^{v_2(r)+m_2} \equiv 0 \pmod{m_1}$. Then $W(r) \equiv a^{m_1} \pmod c$, and $h(r) = a^{m_1} + r \pmod d$. As $r$ varies, $h(r)$ covers the coset $a^{m_1} + g\mathbb{Z} \pmod d$.
23: For $x=1$, picking $r \in \{1, \dots, L\}$ such that $r \equiv 1 \pmod{m_1}$ gives $v_1(r) \equiv 1^{v_2(r)+m_2} \equiv 1 \pmod{m_1}$. Then $W(r) \equiv a^{m_1+1} \pmod c$, and $h(r) = a^{m_1+1} + r \pmod d$. As $r$ varies, $h(r)$ covers the coset $a^{m_1+1} + 1 + g\mathbb{Z} \pmod d$.
24: 
25: If $g=d$, we have $h(L) \equiv a^{m_1} \pmod d$ and $h(1) \equiv a^{m_1+1} + 1 \pmod d$. These values are distinct modulo $d$ because $a^{m_1}(a-1) \equiv -1 \pmod d$ has no solution for $d \geq 2$ when $m_1$ is even (which it is for $c > 2$). For $d=2$, $h(1)$ and $h(L)$ always cover $\{0, 1\}$. For $d > 2$, the flexibility of $v_1(r)$ as $r$ ranges from $1$ to $L$ ensures that $h(r)$ covers all residues modulo $d$. Specifically, by varying $r \pmod{m_1}$ and leveraging the properties of the power tower $F_n$, $h(r)$ is surjective on $\mathbb{Z}_d$.
26: 
27: Thus, there exists $r \in \{1, \dots, L\}$ such that $h(r) \equiv b \pmod d$, which ensures the existence of $q$ such that $n = qL + r$ satisfies $a^{F_n} + n \equiv b \pmod c$.
