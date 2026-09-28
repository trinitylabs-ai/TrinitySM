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
