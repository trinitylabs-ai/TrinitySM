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

1: Let $k$ and $d$ be positive integers. We wish to show that there exists a positive integer $N$ such that for every odd integer $n > N$, the digits of $n^k$ in base $B = 2n$ are all greater than $d$.
2: 
3: Case 1: $k = 1$.
4: In this case, $n^k = n$. Since $n < 2n$, the base-$2n$ representation of $n$ consists of a single digit $a_0 = n$. For any $n > d$, we have $a_0 > d$. Thus, for $k=1$, we may take $N = d$.
5: 
6: Case 2: $k \ge 2$.
7: Let $B = 2n$. The base-$B$ representation of $n^k$ is $n^k = a_m B^m + a_{m-1} B^{m-1} + \dots + a_0$, where $0 \le a_i < B$.
8: For $n > 2^{k-1}$, we have $B^{k-1} = (2n)^{k-1} = 2^{k-1} n^{k-1} < n \cdot n^{k-1} = n^k$. Also, $n^k < (2n)^k = B^k$. Thus, the number of digits is exactly $k$, and the highest power is $m = k-1$.
9: 
10: The digits $a_i$ are determined by the recursive process:
11: $R_k = n^k$
12: $a_{k-1} = \lfloor R_k / B^{k-1} \rfloor = \lfloor n^k / (2n)^{k-1} \rfloor = \lfloor n / 2^{k-1} \rfloor$
13: $R_{k-1} = R_k \pmod{B^{k-1}} = n^k - \lfloor n/2^{k-1} \rfloor 2^{k-1} n^{k-1} = (n \pmod{2^{k-1}}) n^{k-1}$
14: 
15: Let $r_{k-1} = n \pmod{2^{k-1}}$. Since $k \ge 2$, $2^{k-1}$ is even. Since $n$ is odd, $r_{k-1}$ must be odd.
16: We now show by induction that for $j = k-1, k-2, \dots, 1$, the remainder is $R_j = r_j n^j$ with $r_j$ being an odd integer.
17: The base case $j = k-1$ is established: $R_{k-1} = r_{k-1} n^{k-1}$ and $r_{k-1}$ is odd.
18: Suppose $R_j = r_j n^j$ for some $j \in \{k-1, \dots, 1\}$ with $r_j$ odd. Then:
19: $a_{j-1} = \lfloor R_j / B^{j-1} \rfloor = \lfloor r_j n^j / (2n)^{j-1} \rfloor = \lfloor r_j n / 2^{j-1} \rfloor$
20: $R_{j-1} = R_j \pmod{B^{j-1}} = r_j n^j \pmod{2^{j-1} n^{j-1}} = (r_j n \pmod{2^{j-1}}) n^{j-1}$
21: Let $r_{j-1} = r_j n \pmod{2^{j-1}}$. Since $r_j$ and $n$ are both odd, their product $r_j n$ is odd. For $j-1 \ge 1$, any odd number modulo $2^{j-1}$ is odd. Thus, $r_{j-1}$ is odd.
22: This completes the induction, showing $r_j \ge 1$ for all $j \in \{1, \dots, k-1\}$.
23: 
24: Now we evaluate the digits $a_i$:
25: 1. For $i = k-1$, $a_{k-1} = \lfloor n / 2^{k-1} \rfloor$.
26: 2. For $i \in \{0, \dots, k-2\}$, let $j = i+1$. Then $a_i = \lfloor r_j n / 2^{j-1} \rfloor$. Since $r_j \ge 1$, we have $a_i \ge \lfloor n / 2^{j-1} \rfloor$.
27: 3. For $i = 0$, $a_0 = \lfloor r_1 n / 2^0 \rfloor = r_1 n$. Since $r_1$ is odd and $0 \le r_1 < 2^1$, we must have $r_1 = 1$, so $a_0 = n$.
28: 
29: Comparing the lower bounds, since $2^{j-1} \le 2^{k-2}$ for $j \le k-1$, we have $\lfloor n / 2^{j-1} \rfloor \ge \lfloor n / 2^{k-2} \rfloor$. Thus, the smallest digit is $a_{k-1} = \lfloor n / 2^{k-1} \rfloor$.
30: To ensure all digits are greater than $d$, we require $a_{k-1} \ge d+1$:
31: $\lfloor n / 2^{k-1} \rfloor \ge d+1 \iff n / 2^{k-1} \ge d+1 \iff n \ge (d+1) 2^{k-1}$.
32: 
33: Let $N = (d+1) 2^{k-1}$. For any odd integer $n > N$, we have $n \ge (d+1) 2^{k-1} + 1$ (since $(d+1) 2^{k-1}$ is even for $k \ge 2$). Then:
34: $a_{k-1} = \lfloor n / 2^{k-1} \rfloor \ge \lfloor ((d+1) 2^{k-1} + 1) / 2^{k-1} \rfloor = d+1 > d$.
35: Since $a_{k-1}$ is the minimum digit, all digits are greater than $d$.
36: Finally, we verify that $n > N$ ensures the number of digits is $k$:
37: $N = (d+1) 2^{k-1} \ge 2 \cdot 2^{k-1} = 2^k > 2^{k-1}$.
38: Thus $n > N \implies n > 2^{k-1}$, which guarantees $n^k$ has exactly $k$ digits in base $2n$.
39: 
40: Combining both cases, $N = (d+1) 2^{k-1}$ suffices for all $k \ge 1$.
