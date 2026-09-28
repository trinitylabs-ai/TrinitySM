# Problem

Let $k$ and $d$ be positive integers. Prove that there exists a
 positive integer $N$ such that for every odd integer $n>N$, the
 digits in the base-$2n$ representation of $n^{k}$ are all greater
 than $d$.

# Proof A

1: To prove that there exists a positive integer $N$ such that for every odd integer $n > N$, the digits in the base-$2n$ representation of $n^k$ are all greater than $d$, we analyze the process of finding the digits of $n^k$ in base $2n$.
2: 
3: Let the base-$2n$ representation of $n^k$ be $n^k = a_m(2n)^m + a_{m-1}(2n)^{m-1} + \dots + a_1(2n) + a_0$, where $0 \le a_i < 2n$. These digits are determined by the sequence $X_0, X_1, \dots, X_m$ defined by $X_0 = n^k$, $a_i = X_i \pmod{2n}$, and $X_{i+1} = \frac{X_i - a_i}{2n}$.
4: 
5: First, we determine $a_0$. Since $n$ is odd, $n^{k-1}$ is also odd, so $n^{k-1} = 2q + 1$ for some integer $q$. Then $n^k = n(2q + 1) = 2qn + n$. Since $0 \le n < 2n$, we have $a_0 = n$. For $n > d$, it is clear that $a_0 > d$.
6: 
7: Next, we find $X_1$:
8: $X_1 = \frac{n^k - n}{2n} = \frac{n^{k-1} - 1}{2}$.
9: The digit $a_1$ is $X_1 \pmod{2n}$, which implies $2a_1 = 2X_1 \pmod{4n} = (n^{k-1} - 1) \pmod{4n}$.
10: Thus, $2a_1 = m_1 n - 1$ for some integer $m_1$. Since $0 \le a_1 < 2n$, we have $0 \le 2a_1 < 4n$, implying $1 \le m_1 n < 4n + 1$, so $m_1 \in \{1, 2, 3, 4\}$. Because $m_1 n = 2a_1 + 1$ is odd and $n$ is odd, $m_1$ must be odd, so $m_1 \in \{1, 3\}$.
11: Then $X_2 = \frac{X_1 - a_1}{2n} = \frac{\frac{n^{k-1}-1}{2} - \frac{m_1 n - 1}{2}}{2n} = \frac{n^{k-1} - m_1 n}{4n} = \frac{n^{k-2} - m_1}{4}$.
12: 
13: We proceed by induction. Assume $X_i = \frac{n^{k-i} - m_{i-1}}{2^i}$ for some odd integer $m_{i-1}$. Then:
14: $2^i a_i = 2^i X_i \pmod{2^{i+1} n} = (n^{k-i} - m_{i-1}) \pmod{2^{i+1} n}$.
15: Thus, $2^i a_i = m_i n - m_{i-1}$ for some integer $m_i$. Since $0 \le a_i < 2n$, we have $0 \le 2^i a_i < 2^{i+1} n$, which means $m_{i-1} \le m_i n < 2^{i+1} n + m_{i-1}$. Since $m_i n = 2^i a_i + m_{i-1}$ and $m_{i-1}$ is odd, $m_i n$ must be odd, so $m_i$ is odd.
16: Then $X_{i+1} = \frac{X_i - a_i}{2n} = \frac{\frac{n^{k-i} - m_{i-1}}{2^i} - \frac{m_i n - m_{i-1}}{2^i}}{2n} = \frac{n^{k-i} - m_i n}{2^{i+1} n} = \frac{n^{k-i-1} - m_i}{2^{i+1}}$.
17: This inductive step holds for $i = 1, 2, \dots, k-1$.
18: 
19: For $i = k-1$, we have $X_{k-1} = \frac{n - m_{k-2}}{2^{k-1}}$. For $n$ sufficiently large, $0 < X_{k-1} < 2n$, so $a_{k-1} = X_{k-1}$ and $X_k = 0$. The digits are $a_0, a_1, \dots, a_{k-1}$.
20: From $m_i n < 2^{i+1} n + m_{i-1}$, we have $m_i < 2^{i+1} + \frac{m_{i-1}}{n}$. For $n > 2^k$, we can show by induction that $m_i \le 2^{i+1} - 1$ for all $i$.
21: Now we bound the digits $a_i$:
22: 1. $a_0 = n$.
23: 2. For $1 \le i \le k-2$, $a_i = \frac{m_i n - m_{i-1}}{2^i} \ge \frac{n - (2^i - 1)}{2^i} = \frac{n+1}{2^i} - 1$.
24: 3. For $i = k-1$, $a_{k-1} = \frac{n - m_{k-2}}{2^{k-1}} \ge \frac{n - (2^{k-1} - 1)}{2^{k-1}} = \frac{n+1}{2^{k-1}} - 1$.
25: 
26: All digits $a_i$ are greater than $d$ if $\frac{n+1}{2^{k-1}} - 1 > d$, which simplifies to $n > 2^{k-1}(d+1) - 1$.
27: Choosing $N = \max(2^k, 2^{k-1}(d+1))$, for every odd integer $n > N$, all digits in the base-$2n$ representation of $n^k$ are greater than $d$. \(\square\)

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
