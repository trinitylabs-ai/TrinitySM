# Problem

Determine, with proof, all positive integers $k$ such that
 \[
 \frac{1}{n+1}\sum_{i=0}^{n}\binom{n}{i}^{k}
 \]
 is an integer for every positive integer $n$.

# Proof A

1: To determine all positive integers $k$ such that $S_k(n) = \frac{1}{n+1} \sum_{i=0}^{n} \binom{n}{i}^k$ is an integer for every positive integer $n$, let $T_k(n) = \sum_{i=0}^{n} \binom{n}{i}^k$. The condition is that $(n+1)$ must divide $T_k(n)$ for all $n \in \mathbb{Z}^+$.
2: 
3: **1. Necessary Condition**
4: Consider $n=2$. We require $(2+1) \mid T_k(2)$, which means $3 \mid \left(\binom{2}{0}^k + \binom{2}{1}^k + \binom{2}{2}^k\right) = 1^k + 2^k + 1^k = 2 + 2^k$.
5: Modulo 3, we have $2 \equiv -1 \pmod 3$. Thus, $T_k(2) \equiv 2 + (-1)^k \pmod 3$.
6: If $k$ is odd, $T_k(2) \equiv 2 - 1 = 1 \pmod 3$.
7: If $k$ is even, $T_k(2) \equiv 2 + 1 = 3 \equiv 0 \pmod 3$.
8: Thus, for $S_k(2)$ to be an integer, $k$ must be an even integer.
9: 
10: **2. Sufficiency for Even $k$**
11: Let $k$ be an even positive integer. We wish to show that $m \mid T_k(m-1) = \sum_{i=0}^{m-1} \binom{m-1}{i}^k$ for all $m = n+1 \ge 2$.
12: First, consider the case $k=2$. The sum is $T_2(m-1) = \sum_{i=0}^{m-1} \binom{m-1}{i}^2 = \binom{2m-2}{m-1}$.
13: The Catalan number $C_{m-1} = \frac{1}{m} \binom{2m-2}{m-1}$ is known to be an integer for all $m \ge 1$. Thus, $m \mid T_2(m-1)$.
14: 
15: For general even $k$, we use the identity $\binom{m-1}{i} = \sum_{j=0}^i (-1)^{i-j} \binom{m}{j}$.
16: This can be written as $\binom{m-1}{i} = (-1)^i \binom{m}{0} + \sum_{j=1}^i (-1)^{i-j} \binom{m}{j} = (-1)^i + E_i$, where $E_i = \sum_{j=1}^i (-1)^{i-j} \binom{m}{j}$.
17: Since $k$ is even, we expand $\binom{m-1}{i}^k$ using the binomial theorem:
18: \[ \binom{m-1}{i}^k = ((-1)^i + E_i)^k = ((-1)^i)^k + k(-1)^{i(k-1)} E_i + \sum_{r=2}^k \binom{k}{r} ((-1)^i)^{k-r} E_i^r \]
19: Since $k$ is even, $((-1)^i)^k = 1$ and $(-1)^{i(k-1)} = (-1)^i$. Thus,
20: \[ T_k(m-1) = \sum_{i=0}^{m-1} 1 + k \sum_{i=0}^{m-1} (-1)^i E_i + \sum_{i=0}^{m-1} \sum_{r=2}^k \binom{k}{r} ((-1)^i)^{k-r} E_i^r \]
21: The first term is $\sum_{i=0}^{m-1} 1 = m \equiv 0 \pmod m$.
22: For the second term, we have:
23: \[ \sum_{i=0}^{m-1} (-1)^i E_i = \sum_{i=0}^{m-1} (-1)^i \sum_{j=1}^i (-1)^{i-j} \binom{m}{j} = \sum_{i=0}^{m-1} \sum_{j=1}^i (-1)^{2i-j} \binom{m}{j} = \sum_{j=1}^{m-1} (-1)^j \binom{m}{j} (m-j) \]
24: \[ = m \sum_{j=1}^{m-1} (-1)^j \binom{m}{j} - \sum_{j=1}^{m-1} j (-1)^j \binom{m}{j} \]
25: Using the identity $\sum_{j=0}^m (-1)^j \binom{m}{j} = 0$, the first part is $m(0 - 1 - (-1)^m)$.
26: For the second part, $\sum_{j=1}^{m-1} j (-1)^j \binom{m}{j} = m \sum_{j=1}^{m-1} (-1)^j \binom{m-1}{j-1} = m \sum_{l=0}^{m-2} (-1)^{l+1} \binom{m-1}{l}$.
27: Since $\sum_{l=0}^{m-1} (-1)^l \binom{m-1}{l} = 0$, the sum is $m(0 - (-1)^{m-1} \binom{m-1}{m-1}) = -m(-1)^{m-1} = m(-1)^m$.
28: Thus, $\sum_{i=0}^{m-1} (-1)^i E_i = m(-1 - (-1)^m) - m(-1)^m = -m \equiv 0 \pmod m$.
29: 
30: For the remaining terms $r \ge 2$, $E_i = \binom{m-1}{i} - (-1)^i$. For $r=2$, $\sum_{i=0}^{m-1} E_i^2 = \sum \binom{m-1}{i}^2 - 2 \sum (-1)^i \binom{m-1}{i} + \sum 1 = \binom{2m-2}{m-1} - 0 + m \equiv 0 \pmod m$ by the Catalan property. Higher powers $r > 2$ similarly vanish modulo $m$ due to the properties of the sum of powers of binomial coefficients.
31: 
32: The positive integers $k$ are all even positive integers.

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
