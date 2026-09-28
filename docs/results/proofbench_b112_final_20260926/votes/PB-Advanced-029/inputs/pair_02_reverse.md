# Problem

Determine, with proof, all positive integers $k$ such that
 \[
 \frac{1}{n+1}\sum_{i=0}^{n}\binom{n}{i}^{k}
 \]
 is an integer for every positive integer $n$.

# Proof A

1: To determine all positive integers $k$ such that $S_k(n) = \frac{1}{n+1} \sum_{i=0}^{n} \binom{n}{i}^k$ is an integer for every positive integer $n$, we first examine the condition for small values of $n$.
2: 
3: For $n=1$, $S_k(1) = \frac{1}{2}(\binom{1}{0}^k + \binom{1}{1}^k) = \frac{1+1}{2} = 1$, which is an integer for all $k \in \mathbb{Z}^+$.
4: For $n=2$, $S_k(2) = \frac{1}{3}(\binom{2}{0}^k + \binom{2}{1}^k + \binom{2}{2}^k) = \frac{1+2^k+1}{3} = \frac{2^k+2}{3}$. For $S_k(2)$ to be an integer, we require $2^k+2 \equiv 0 \pmod 3$, which simplifies to $2^k \equiv -2 \equiv 1 \pmod 3$. Since $2^1 \equiv 2 \pmod 3$ and $2^2 \equiv 1 \pmod 3$, this condition is satisfied if and only if $k$ is even.
5: 
6: We now prove that for any even positive integer $k$, $S_k(n)$ is an integer for all $n \ge 1$. Let $m = n+1$. We wish to show that $m$ divides $T_k(m-1) = \sum_{i=0}^{m-1} \binom{m-1}{i}^k$. It suffices to show that for every prime power $p^v$ such that $p^v$ exactly divides $m$ (i.e., $v = v_p(m)$), $T_k(m-1) \equiv 0 \pmod{p^v}$.
7: 
8: The binomial coefficient $\binom{m-1}{i}$ can be written as
9: \[ \binom{m-1}{i} = \prod_{j=1}^i \frac{m-j}{j} = (-1)^i \prod_{j=1}^i \left(1 - \frac{m}{j}\right). \]
10: Since $k$ is even, we have $\binom{m-1}{i}^k = \prod_{j=1}^i (1 - \frac{m}{j})^k$. Let $f(m, i) = \prod_{j=1}^i (1 - \frac{m}{j})$. We consider this product in the ring of $p$-adic integers $\mathbb{Z}_p$. We split the indices $j \in \{1, \dots, i\}$ into those coprime to $p$ and those divisible by $p$:
11: \[ f(m, i) = \left( \prod_{j=1, p \nmid j}^i \left(1 - \frac{m}{j}\right) \right) \left( \prod_{l=1}^{\lfloor i/p \rfloor} \left(1 - \frac{m}{pl}\right) \right). \]
12: Since $v_p(m) = v$, for any $j$ coprime to $p$, $v_p(m/j) = v$, so $1 - m/j \equiv 1 \pmod{p^v}$. Thus, the first product is congruent to $1 \pmod{p^v}$. The second product is exactly $f(m/p, \lfloor i/p \rfloor)$. Therefore, we have the congruence
13: \[ f(m, i) \equiv f(m/p, \lfloor i/p \rfloor) \pmod{p^v}. \]
14: Substituting this into the sum $T_k(m-1)$:
15: \[ T_k(m-1) = \sum_{i=0}^{m-1} f(m, i)^k \equiv \sum_{i=0}^{m-1} f(m/p, \lfloor i/p \rfloor)^k \pmod{p^v}. \]
16: We group the sum by $q = \lfloor i/p \rfloor$. For each $q \in \{0, 1, \dots, \frac{m}{p}-1\}$, there are exactly $p$ values of $i \in \{0, \dots, m-1\}$ such that $\lfloor i/p \rfloor = q$. Thus,
17: \[ T_k(m-1) \equiv p \sum_{q=0}^{m/p-1} f(m/p, q)^k \pmod{p^v}. \]
18: Since $k$ is even, $f(m/p, q)^k = \binom{m/p-1}{q}^k$. The sum is therefore $T_k(m/p-1)$. We have established the recurrence:
19: \[ T_k(m-1) \equiv p T_k(m/p-1) \pmod{p^v}. \]
20: We now prove $T_k(m-1) \equiv 0 \pmod{p^v}$ by induction on $v = v_p(m)$.
21: Base case: $v=1$. Then $T_k(m-1) \equiv p T_k(m/p-1) \equiv 0 \pmod p$, since $T_k(m/p-1)$ is an integer.
22: Inductive step: Assume that for any $m'$ with $v_p(m') = v-1$, $T_k(m'-1) \equiv 0 \pmod{p^{v-1}}$. Let $m$ be such that $v_p(m) = v$. Then $v_p(m/p) = v-1$. By the inductive hypothesis, $T_k(m/p-1) = p^{v-1} Z$ for some integer $Z$. Then
23: \[ T_k(m-1) \equiv p (p^{v-1} Z) \equiv p^v Z \equiv 0 \pmod{p^v}. \]
24: Thus, $p^v$ divides $T_k(m-1)$ for all prime powers $p^v$ dividing $m$. By the Chinese Remainder Theorem, $m$ divides $T_k(m-1)$, so $S_k(n)$ is an integer for all $n \ge 1$.
25: 
26: The positive integers $k$ are all even positive integers.

# Proof B

1: To determine all positive integers $k$ such that $S_n(k) = \frac{1}{n+1} \sum_{i=0}^{n} \binom{n}{i}^{k}$ is an integer for every positive integer $n$, we analyze the condition that $m = n+1$ must divide the sum $S(m) = \sum_{i=0}^{m-1} \binom{m-1}{i}^{k}$ for all $m \ge 2$.
2: 
3: **1. Necessary Condition for $k$**
4: Consider the case $n=2$, so $m=3$. The sum is:
5: \[ S(3) = \sum_{i=0}^{2} \binom{2}{i}^k = \binom{2}{0}^k + \binom{2}{1}^k + \binom{2}{2}^k = 1^k + 2^k + 1^k = 2^k + 2 \]
6: For $S_2(k)$ to be an integer, we require $3 \mid (2^k + 2)$, which means $2^k \equiv -2 \equiv 1 \pmod{3}$.
7: The powers of $2$ modulo $3$ are $2^1 \equiv 2 \pmod{3}$ and $2^2 \equiv 1 \pmod{3}$, alternating with parity. Thus, $2^k \equiv 1 \pmod{3}$ if and only if $k$ is even. Therefore, $k$ must be an even positive integer.
8: 
9: **2. Sufficient Condition for Even $k$**
10: Let $k$ be any even positive integer. We wish to show that $m \mid S(m)$ for all $m \ge 2$. By the Chinese Remainder Theorem, it suffices to prove that for any prime power $p^e$ dividing $m$, we have $S(m) \equiv 0 \pmod{p^e}$.
11: Let $m = N p^e$ for some positive integer $N$. We examine $S(m) \pmod{p^e}$.
12: 
13: **Lemma:** For any $0 \le i < m$, $\binom{m-1}{i} \equiv (-1)^{i - \lfloor i/p \rfloor} \binom{N p^{e-1} - 1}{\lfloor i/p \rfloor} \pmod{p^e}$.
14: *Proof:* The binomial coefficient is given by $\binom{m-1}{i} = \prod_{j=1}^i \frac{m-j}{j}$. We partition the product into indices $j$ where $p \nmid j$ and indices $j$ where $p \mid j$.
15: For $p \nmid j$, the term $\frac{m-j}{j} = \frac{m}{j} - 1$. Since $m = N p^e$, we have $\frac{m}{j} \equiv 0 \pmod{p^e}$ because $j$ is invertible modulo $p^e$. Thus, $\frac{m-j}{j} \equiv -1 \pmod{p^e}$. There are exactly $i - \lfloor i/p \rfloor$ such terms in the product.
16: For $j = pv$, the product over these indices is:
17: \[ \prod_{v=1}^{\lfloor i/p \rfloor} \frac{m-pv}{pv} = \prod_{v=1}^{\lfloor i/p \rfloor} \frac{N p^e - pv}{pv} = \prod_{v=1}^{\lfloor i/p \rfloor} \frac{N p^{e-1} - v}{v} = \binom{N p^{e-1} - 1}{\lfloor i/p \rfloor} \]
18: Combining these, we obtain $\binom{m-1}{i} \equiv (-1)^{i - \lfloor i/p \rfloor} \binom{N p^{e-1} - 1}{\lfloor i/p \rfloor} \pmod{p^e}$. $\square$
19: 
20: Using this lemma, we substitute into the sum $S(m)$:
21: \[ S(m) = \sum_{i=0}^{m-1} \binom{m-1}{i}^k \equiv \sum_{i=0}^{m-1} \left( (-1)^{i - \lfloor i/p \rfloor} \binom{N p^{e-1} - 1}{\lfloor i/p \rfloor} \right)^k \pmod{p^e} \]
22: Since $k$ is even, $(-1)^{k(i - \lfloor i/p \rfloor)} = 1$. Thus:
23: \[ S(m) \equiv \sum_{i=0}^{m-1} \binom{N p^{e-1} - 1}{\lfloor i/p \rfloor}^k \pmod{p^e} \]
24: As $i$ ranges from $0$ to $m-1 = N p^e - 1$, the value $j = \lfloor i/p \rfloor$ takes each integer from $0$ to $N p^{e-1} - 1$ exactly $p$ times. Therefore:
25: \[ S(m) \equiv p \sum_{j=0}^{N p^{e-1} - 1} \binom{N p^{e-1} - 1}{j}^k = p S(N p^{e-1}) \pmod{p^e} \]
26: 
27: We now prove $p^e \mid S(N p^e)$ by induction on $e$ for a fixed $N$:
28: - Base case $e=1$: $S(N p) \equiv p S(N) \equiv 0 \pmod{p}$, which is true since $S(N)$ is an integer.
29: - Inductive step: Assume $p^{e-1} \mid S(N p^{e-1})$. Then $S(N p^{e-1}) = A p^{e-1}$ for some integer $A$. From our recurrence, $S(N p^e) \equiv p (A p^{e-1}) = A p^e \equiv 0 \pmod{p^e}$.
30: 
31: Thus, $S(m)$ is divisible by $p^e$ for every prime power dividing $m$, implying $m \mid S(m)$ for all $m \ge 2$ when $k$ is even.
32: 
33: The positive integers $k$ such that $\frac{1}{n+1}\sum_{i=0}^{n}\binom{n}{i}^{k}$ is an integer for every positive integer $n$ are all even positive integers.
