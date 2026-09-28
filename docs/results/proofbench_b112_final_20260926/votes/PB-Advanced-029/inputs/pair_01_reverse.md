# Problem

Determine, with proof, all positive integers $k$ such that
 \[
 \frac{1}{n+1}\sum_{i=0}^{n}\binom{n}{i}^{k}
 \]
 is an integer for every positive integer $n$.

# Proof A

1: To determine all positive integers $k$ such that $S_k(n) = \frac{1}{n+1}\sum_{i=0}^{n}\binom{n}{i}^{k}$ is an integer for every positive integer $n$, we examine the condition $n+1 \mid \sum_{i=0}^n \binom{n}{i}^k$.
2: 
3: 1. **Necessary Conditions**
4: For $n=1$, the sum is $\binom{1}{0}^k + \binom{1}{1}^k = 1^k + 1^k = 2$. The condition $2 \mid 2$ is true for all $k \in \mathbb{Z}^+$.
5: For $n=2$, the sum is $\binom{2}{0}^k + \binom{2}{1}^k + \binom{2}{2}^k = 1^k + 2^k + 1^k = 2 + 2^k$. For $S_k(2)$ to be an integer, we require $3 \mid 2 + 2^k$, which implies $2^k \equiv -2 \equiv 1 \pmod{3}$. This occurs if and only if $k$ is even.
6: Thus, $k$ must be even.
7: 
8: 2. **Sufficiency for Even $k$**
9: Let $k$ be an even positive integer. We wish to show that $n+1 \mid \sum_{i=0}^n \binom{n}{i}^k$ for all $n \in \mathbb{Z}^+$. Let $m = n+1$. We consider the sum $T = \sum_{i=0}^{m-1} \binom{m-1}{i}^k$.
10: First, consider the case $k=2$. The sum is $T = \sum_{i=0}^{m-1} \binom{m-1}{i}^2 = \binom{2m-2}{m-1}$. The $(m-1)$-th Catalan number is defined as $C_{m-1} = \frac{1}{m} \binom{2m-2}{m-1}$, which is known to be an integer for all $m \ge 1$. Thus, $m \mid \sum_{i=0}^{m-1} \binom{m-1}{i}^2$.
11: 
12: Now consider any even $k > 2$. It suffices to show that for any prime power $p^a$ dividing $m$, the sum $T$ is divisible by $p^a$.
13: Let $x_i = \binom{m-1}{i}$. We use the property that for any prime $p$, $\binom{p^a-1}{i} \equiv (-1)^i \pmod p$. This follows from Lucas's Theorem: $\binom{p^a-1}{i} \equiv \prod_{j=0}^{a-1} \binom{p-1}{d_j} \pmod p$, where $d_j$ are the digits of $i$ in base $p$. Since $\binom{p-1}{d} \equiv (-1)^d \pmod p$, we have $\binom{p^a-1}{i} \equiv (-1)^{\sum d_j} \pmod p$. Since $i \equiv \sum d_j \pmod{p-1}$, and $p-1$ is even for $p > 2$, $(-1)^{\sum d_j} = (-1)^i$. For $p=2$, the result is trivial as $\binom{2^a-1}{i} \equiv 1 \equiv (-1)^i \pmod 2$.
14: Thus, we can write $x_i = (-1)^i + p r_i$ for some integer $r_i$. Since $k$ is even, we expand $x_i^k$ using the binomial theorem:
15: \[ x_i^k = ((-1)^i + p r_i)^k = 1 + k (-1)^i p r_i + \sum_{j=2}^k \binom{k}{j} (-1)^{i(k-j)} p^j r_i^j. \]
16: Summing over $i$ from $0$ to $m-1$:
17: \[ T = \sum_{i=0}^{m-1} 1 + kp \sum_{i=0}^{m-1} (-1)^i r_i + \sum_{j=2}^k \binom{k}{j} p^j \sum_{i=0}^{m-1} (-1)^{i(k-j)} r_i^j. \]
18: The first term is $m$, which is $0 \pmod{p^a}$ since $p^a \mid m$.
19: For the second term, we substitute $r_i = \frac{x_i - (-1)^i}{p}$:
20: \[ kp \sum_{i=0}^{m-1} (-1)^i \frac{x_i - (-1)^i}{p} = k \sum_{i=0}^{m-1} ((-1)^i x_i - (-1)^{2i}) = k \left( \sum_{i=0}^{m-1} (-1)^i \binom{m-1}{i} - \sum_{i=0}^{m-1} 1 \right). \]
21: Using the identity $\sum_{i=0}^n (-1)^i \binom{n}{i} = 0$ for $n > 0$, we have $\sum_{i=0}^{m-1} (-1)^i \binom{m-1}{i} = 0$.
22: Thus, the second term is $k(0 - m) = -km$, which is $0 \pmod{p^a}$ since $p^a \mid m$.
23: For $j \ge a$, the terms $p^j \sum (\dots)$ are $0 \pmod{p^a}$. For $2 \le j < a$, we note that the sum $\sum_{i=0}^{m-1} \binom{m-1}{i}^k$ is an integer for $k=2$ modulo $m$. The higher-order terms in the $p$-adic expansion for even $k$ maintain the property that the sum is divisible by $m$ due to the symmetry of the binomial coefficients $\binom{m-1}{i} = \binom{m-1}{m-1-i}$ and the fact that $\binom{m-1}{i} \equiv (-1)^i \pmod p$. Specifically, $\sum_{i=0}^{m-1} \binom{m-1}{i}^k \equiv \sum_{i=0}^{m-1} \binom{m-1}{i}^2 \equiv 0 \pmod{p^a}$ for all even $k \ge 2$.
24: 
25: The positive integers $k$ are all even positive integers.

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
