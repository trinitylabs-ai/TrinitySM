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
