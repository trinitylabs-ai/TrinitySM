# Problem

Let $k$ and $d$ be positive integers. Prove that there exists a
 positive integer $N$ such that for every odd integer $n>N$, the
 digits in the base-$2n$ representation of $n^{k}$ are all greater
 than $d$.

# Proof A

1: Let $k$ and $d$ be positive integers. We wish to show that there exists a positive integer $N$ such that for every odd integer $n > N$, the digits in the base-$2n$ representation of $n^k$ are all greater than $d$. Let the base be $B = 2n$. The base-$B$ representation of $n^k$ is given by
2: \[ n^k = a_m B^m + a_{m-1} B^{m-1} + \dots + a_1 B + a_0, \]
3: where $0 \le a_i < B$ for all $i$ and $a_m \neq 0$. We must show that $a_i > d$ for all $i \in \{0, 1, \dots, m\}$.
4: 
5: First, consider the digit $a_0$. By definition, $a_0 \equiv n^k \pmod{2n}$. Since $n$ is odd, $n^{k-1}$ is also odd, so $n^{k-1}-1$ is even. Thus, $n^k - n = n(n^{k-1}-1)$ is a multiple of $2n$. This implies $n^k \equiv n \pmod{2n}$. Since $0 \le n < 2n$, we must have $a_0 = n$. For any $n > d$, the condition $a_0 > d$ is satisfied.
6: 
7: Next, we determine the digits $a_1, \dots, a_m$. From the base representation, we have
8: \[ n^k - n = \sum_{i=1}^m a_i (2n)^i. \]
9: Dividing both sides by $2n$, we obtain
10: \[ X = \frac{n^{k-1}-1}{2} = \sum_{i=1}^m a_i (2n)^{i-1}. \]
11: This expression is the base-$2n$ representation of the integer $X$. The digits $a_1, \dots, a_m$ are the coefficients of the powers of $2n$ in the expansion of $X$. Specifically, for $i \ge 1$, the $i$-th digit $a_i$ is given by
12: \[ a_i = \left\lfloor \frac{X}{(2n)^{i-1}} \right\rfloor \pmod{2n} = \left\lfloor \frac{n^{k-1}-1}{2(2n)^{i-1}} \right\rfloor \pmod{2n} = \left\lfloor \frac{n^{k-i}}{2^i} - \frac{1}{2^i n^{i-1}} \right\rfloor \pmod{2n}. \]
13: For $i \in \{1, \dots, k-1\}$, let $x = \frac{n^{k-i}}{2^i}$ and $\epsilon = \frac{1}{2^i n^{i-1}}$. Since $n$ is odd, $n^{k-i}$ is odd, so the fractional part of $x$ is $\{x\} = \frac{n^{k-i} \pmod{2^i}}{2^i}$. Because $n^{k-i}$ is odd, $n^{k-i} \pmod{2^i}$ is an odd integer $\ge 1$, so $\{x\} \ge \frac{1}{2^i}$. Since $n \ge 1$ and $i \ge 1$, we have $\epsilon = \frac{1}{2^i n^{i-1}} \le \frac{1}{2^i}$. Thus $\{x\} \ge \epsilon$, which implies $\lfloor x - \epsilon \rfloor = \lfloor x \rfloor$.
14: It follows that $a_i = \lfloor \frac{n^{k-i}}{2^i} \rfloor \pmod{2n}$ for $i=1, \dots, k-1$. For $i \ge k$, we have $X = \frac{n^{k-1}-1}{2} < \frac{n^{k-1}}{2} < (2n)^{k-1}$ for all $n \ge 1, k \ge 1$. Since $X < (2n)^{k-1}$, the base-$2n$ representation of $X$ has at most $k-1$ digits. Thus, $a_i = 0$ for all $i \ge k$. This means the maximum index is $m \le k-1$.
15: 
16: To analyze $a_i = \lfloor \frac{n^{k-i}}{2^i} \rfloor \pmod{2n}$ for $i \in \{1, \dots, k-1\}$, let $M = k-i$ and $C = 2^i$. We examine $a_i = \lfloor \frac{n^M}{C} \rfloor \pmod{2n}$ for $M \in \{1, \dots, k-1\}$.
17: Let $n^{M-1} = q(2C) + s$, where $0 \le s < 2C$. Since $n$ is odd, $n^{M-1}$ is odd, and since $2C$ is even, $s$ must be odd, implying $s \ge 1$. Then
18: \[ n^M = n(q(2C) + s) = 2nCq + ns. \]
19: We can write $\lfloor \frac{n^M}{C} \rfloor = \lfloor \frac{2nCq + ns}{C} \rfloor = 2nq + \lfloor \frac{ns}{C} \rfloor$.
20: Taking this modulo $2n$, we find
21: \[ a_i = \lfloor \frac{ns}{C} \rfloor \pmod{2n}. \]
22: Since $s < 2C$, we have $ns < 2nC$, so $\lfloor \frac{ns}{C} \rfloor < 2n$. Thus, $a_i = \lfloor \frac{ns}{C} \rfloor$.
23: Since $s \ge 1$, we have $a_i \ge \lfloor \frac{n}{C} \rfloor$. For $a_i > d$, it suffices that $\lfloor \frac{n}{C} \rfloor \ge d+1$, which is true if $n \ge C(d+1)$.
24: Since $C = 2^i \le 2^{k-1}$, this condition is satisfied for all $i \in \{1, \dots, k-1\}$ if $n \ge 2^{k-1}(d+1)$.
25: 
26: Choosing $N = 2^{k-1}(d+1)$, we have shown that for every odd integer $n > N$, the digits $a_0 = n$ and $a_i = \lfloor \frac{ns}{2^i} \rfloor$ for $1 \le i \le k-1$ are all greater than $d$. Since $a_i = 0$ for $i \ge k$, the only digits in the base-$2n$ representation of $n^k$ are $a_0, \dots, a_m$ with $m \le k-1$, all of which are greater than $d$.

# Proof B

1: Let $k$ and $d$ be positive integers. We wish to find a positive integer $N$ such that for every odd integer $n > N$, the digits of $n^k$ in base $B = 2n$ are all greater than $d$.
2: 
3: Let the base-$2n$ representation of $n^k$ be
4: \[ n^k = a_m (2n)^m + a_{m-1} (2n)^{m-1} + \dots + a_1 (2n) + a_0 \]
5: where $0 \le a_j < 2n$ for all $j$ and $a_m \neq 0$. The digits $a_j$ are determined by the sequence of quotients $X_j$, where $X_0 = n^k$ and $X_{j+1} = \lfloor X_j / 2n \rfloor$, such that $a_j = X_j \pmod{2n} = X_j - 2n X_{j+1}$.
6: 
7: First, we determine $a_0$. Since $n$ is odd, $n^{k-1}$ is also odd, so $n^{k-1} = 2q + 1$ for some integer $q$. Then
8: \[ n^k = n \cdot n^{k-1} = n(2q + 1) = q(2n) + n. \]
9: Since $0 \le n < 2n$, the remainder of $n^k$ modulo $2n$ is $a_0 = n$. For any $n > d$, we have $a_0 > d$.
10: 
11: Next, we determine the subsequent digits. The first quotient is $X_1 = \lfloor n^k / 2n \rfloor = q = \frac{n^{k-1}-1}{2}$.
12: For $j=1, 2, \dots, k$, let $s_j$ be the remainder of $n^{k-j}$ modulo $2^j$. Since $n$ is odd, $n^{k-j}$ is odd for all $j$, which implies $s_j \in \{1, 3, \dots, 2^j-1\}$. In particular, $1 \le s_j \le 2^j-1$.
13: 
14: We claim that for sufficiently large $n$, $X_j = \frac{n^{k-j}-s_j}{2^j}$ for $j=1, 2, \dots, k-1$.
15: For $j=1$, $X_1 = \frac{n^{k-1}-1}{2}$. Since $s_1 = n^{k-1} \pmod 2 = 1$, the claim holds.
16: Assume the claim holds for some $j < k-1$. Then
17: \[ X_{j+1} = \left\lfloor \frac{X_j}{2n} \right\rfloor = \left\lfloor \frac{n^{k-j}-s_j}{2^j \cdot 2n} \right\rfloor = \left\lfloor \frac{n^{k-j-1}}{2^{j+1}} - \frac{s_j}{2^{j+1}n} \right\rfloor. \]
18: Using the definition of $s_{j+1}$, let $n^{k-j-1} = 2^{j+1} q + s_{j+1}$. Then
19: \[ X_{j+1} = q + \left\lfloor \frac{s_{j+1}}{2^{j+1}} - \frac{s_j}{2^{j+1}n} \right\rfloor = q + \left\lfloor \frac{s_{j+1}n - s_j}{2^{j+1}n} \right\rfloor. \]
20: Since $s_{j+1} \ge 1$ and $s_j \le 2^j-1$, we have $s_{j+1}n - s_j \ge n - (2^j-1)$. For $n \ge 2^j$, this is at least 1. Furthermore, since $s_{j+1} \le 2^{j+1}-1$, we have $s_{j+1}n - s_j \le (2^{j+1}-1)n - 1 < 2^{j+1}n$. Thus, for $n \ge 2^j$, the term inside the floor satisfies $0 < \frac{s_{j+1}n - s_j}{2^{j+1}n} < 1$, so the floor is 0.
21: Thus, $X_{j+1} = q = \frac{n^{k-j-1}-s_{j+1}}{2^{j+1}}$. This completes the induction for $j=1, \dots, k-1$.
22: 
23: Now we calculate the digits $a_j$ for $j=1, \dots, k-1$:
24: For $j=1, \dots, k-2$:
25: \[ a_j = X_j - 2n X_{j+1} = \frac{n^{k-j}-s_j}{2^j} - 2n \left( \frac{n^{k-j-1}-s_{j+1}}{2^{j+1}} \right) = \frac{n^{k-j}-s_j - (n^{k-j}-s_{j+1}n)}{2^j} = \frac{s_{j+1}n - s_j}{2^j}. \]
26: Since $s_{j+1} \ge 1$ and $s_j \le 2^j-1$, we have $a_j \ge \frac{n - (2^j-1)}{2^j}$.
27: For $j=k-1$:
28: $X_k = \lfloor X_{k-1}/2n \rfloor = \lfloor \frac{n-s_{k-1}}{2^{k-1} \cdot 2n} \rfloor = \lfloor \frac{n-s_{k-1}}{2^k n} \rfloor$.
29: Since $0 \le n-s_{k-1} < n$, we have $0 \le \frac{n-s_{k-1}}{2^k n} < \frac{1}{2^k} < 1$. Thus, $X_k = 0$.
30: This implies that the highest power of $2n$ in the representation of $n^k$ is $(2n)^{k-1}$, and the digits are $a_0, a_1, \dots, a_{k-1}$.
31: The last digit is $a_{k-1} = X_{k-1} = \frac{n-s_{k-1}}{2^{k-1}} \ge \frac{n - (2^{k-1}-1)}{2^{k-1}}$.
32: 
33: Finally, we ensure all $a_j > d$. For each $j \in \{1, \dots, k-1\}$, the condition $a_j > d$ is satisfied if
34: \[ \frac{n - (2^j-1)}{2^j} > d \implies n > d 2^j + 2^j - 1. \]
35: By choosing $N = \max \{ d, \max_{1 \le j \le k-1} (d 2^j + 2^j - 1), 2^{k-2} \}$, we guarantee that for all odd $n > N$, the induction condition $n \ge 2^j$ is satisfied and all digits $a_0, a_1, \dots, a_{k-1}$ are greater than $d$.
