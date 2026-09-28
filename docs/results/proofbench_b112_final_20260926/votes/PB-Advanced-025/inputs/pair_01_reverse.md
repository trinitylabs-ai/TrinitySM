# Problem

Let $k$ and $d$ be positive integers. Prove that there exists a
 positive integer $N$ such that for every odd integer $n>N$, the
 digits in the base-$2n$ representation of $n^{k}$ are all greater
 than $d$.

# Proof A

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
