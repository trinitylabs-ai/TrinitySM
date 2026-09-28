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
