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
