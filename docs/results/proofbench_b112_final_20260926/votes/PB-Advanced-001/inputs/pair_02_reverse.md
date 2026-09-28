# Problem

For a positive integer $n$, let $A_{n}$ be the number of perfect powers less than or equal to $n$. Here, a perfect power is a number that can be expressed in the form $a^{b}$, where $a$ is a positive integer and $b$ is an integer greater than or equal to 2. Prove that there are infinitely many $n$ such that $A_{n}$ divides $n+2024$.

# Proof A

1: Let $A_n$ be the number of perfect powers less than or equal to $n$. A perfect power is an integer of the form $a^b$, where $a \in \mathbb{Z}^+$ and $b \in \mathbb{Z}, b \ge 2$. Note that $1$ is a perfect power for any $b \ge 2$.
2: 
3: For $n \ge 1$, we can express $A_n$ using the principle of inclusion-exclusion. An integer $x > 1$ is a perfect power if and only if $x = a^k$ for some $k \ge 2$. Let $S_k = \{ a^k : a \in \mathbb{Z}, a \ge 2, a^k \le n \}$. Then $|S_k| = \lfloor n^{1/k} \rfloor - 1$. The number of perfect powers in the range $[2, n]$ is the size of the union $\bigcup_{k=2}^{\lfloor \log_2 n \rfloor} S_k$. By the principle of inclusion-exclusion, this size is:
4: \[ \sum_{k=2}^{\lfloor \log_2 n \rfloor} -\mu(k) |S_k| = \sum_{k=2}^{\lfloor \log_2 n \rfloor} -\mu(k) (\lfloor n^{1/k} \rfloor - 1) \]
5: where $\mu$ is the Möbius function. Including the perfect power $1$, we have:
6: \[ A_n = 1 + \sum_{k=2}^{\lfloor \log_2 n \rfloor} -\mu(k) (\lfloor n^{1/k} \rfloor - 1) \]
7: We can separate the term for $k=2$:
8: \[ A_n = 1 - \mu(2)(\lfloor n^{1/2} \rfloor - 1) + \sum_{k=3}^{\lfloor \log_2 n \rfloor} -\mu(k) (\lfloor n^{1/k} \rfloor - 1) = \lfloor \sqrt{n} \rfloor + S_n \]
9: where $S_n = \sum_{k=3}^{\lfloor \log_2 n \rfloor} -\mu(k) (\lfloor n^{1/k} \rfloor - 1)$. Here, $S_n$ represents the number of perfect powers less than or equal to $n$ that are not squares. We can bound $S_n$ as follows:
10: \[ |S_n| \le \sum_{k=3}^{\lfloor \log_2 n \rfloor} (\lfloor n^{1/k} \rfloor - 1) \le \sum_{k=3}^{\lfloor \log_2 n \rfloor} n^{1/k} \le n^{1/3} + (\log_2 n - 3)n^{1/4} \]
11: for $n \ge 8$. Since $\lim_{n \to \infty} \frac{n^{1/3} + (\log_2 n) n^{1/4}}{\sqrt{n}} = 0$, it follows that $S_n = o(\sqrt{n})$ as $n \to \infty$.
12: 
13: Consider the interval $I_k = [k^2, (k+1)^2 - 1]$ for a positive integer $k$. For any $n \in I_k$, we have $\lfloor \sqrt{n} \rfloor = k$. Let $P$ be the set of all perfect powers that are not squares. Then $S_n = |P \cap [1, n]|$. Let $T_k$ be the number of elements of $P$ in the interval $(k^2, (k+1)^2)$. If $T_k = 0$, then for all $n \in I_k$, $P \cap (k^2, n] = \emptyset$, which implies $S_n = S_{k^2}$ for all $n \in I_k$. Consequently, $A_n = k + S_{k^2}$ for all $n \in I_k$.
14: 
15: We now show that $T_k = 0$ for infinitely many $k$. The number of $k \in \{1, \dots, N\}$ such that $T_k > 0$ is at most the total number of elements of $P$ up to $(N+1)^2$:
16: \[ \sum_{k=1}^N \mathbb{1}_{T_k > 0} \le S_{(N+1)^2} \]
17: Since $S_X = o(\sqrt{X})$, we have $S_{(N+1)^2} = o(N+1)$. Thus, $\lim_{N \to \infty} \frac{1}{N} \sum_{k=1}^N \mathbb{1}_{T_k > 0} = 0$, meaning the set of $k$ for which $T_k = 0$ has asymptotic density 1. In particular, there are infinitely many such $k$.
18: 
19: For such a $k$, let $m = A_n = k + S_{k^2}$ for all $n \in I_k$. We wish to find $n \in I_k$ such that $n \equiv -2024 \pmod{m}$. The interval $I_k$ contains $(k+1)^2 - 1 - k^2 + 1 = 2k+1$ consecutive integers. Such an $n$ exists if the number of integers in $I_k$ is at least $m$:
20: \[ 2k+1 \ge k + S_{k^2} \iff k+1 \ge S_{k^2} \]
21: Since $S_{k^2} = o(k)$, this inequality holds for all sufficiently large $k$. Therefore, for every sufficiently large $k$ such that $T_k = 0$, there exists at least one $n \in I_k$ such that $A_n$ divides $n + 2024$. Since the intervals $I_k$ are disjoint and there are infinitely many such $k$, there are infinitely many such $n$.

# Proof B

1: To prove that there are infinitely many positive integers $n$ such that $A_n$ divides $n + 2024$, where $A_n$ is the number of perfect powers less than or equal to $n$, we analyze the growth and distribution of perfect powers.
2: 
3: ### 1. The Structure of $A_n$
4: A perfect power is an integer of the form $a^b$ where $a \in \mathbb{Z}^+$ and $b \in \mathbb{Z}, b \ge 2$. Let the sequence of perfect powers be $x_1, x_2, x_3, \dots$ such that $x_1 < x_2 < x_3 < \dots$. By definition, for any integer $n$, $A_n$ is the number of elements in the set $\{x_k : x_k \le n\}$.
5: Consequently, for any $k \ge 1$, if $n$ lies in the interval $[x_k, x_{k+1}-1]$, then $A_n = k$.
6: 
7: ### 2. The Divisibility Condition
8: We want to find $n$ such that $A_n \mid (n + 2024)$. For $n \in [x_k, x_{k+1}-1]$, this is equivalent to:
9: \[ k \mid (n + 2024) \iff n \equiv -2024 \pmod{k}. \]
10: An integer $n$ satisfying this congruence exists in the interval $[x_k, x_{k+1}-1]$ if the length of the interval is at least $k$. The length is:
11: \[ (x_{k+1}-1) - x_k + 1 = x_{k+1} - x_k. \]
12: Thus, if $x_{k+1} - x_k \ge k$, there is at least one $n \in [x_k, x_{k+1}-1]$ such that $A_n = k$ and $k \mid (n + 2024)$.
13: 
14: ### 3. Analyzing the Gaps Between Perfect Powers
15: The set of perfect powers includes all squares $m^2$ for $m \in \mathbb{Z}^+$. Let $x_k = m^2$ for some large integer $m$. The number of perfect powers up to $m^2$ is:
16: \[ k = A_{m^2} = \lfloor (m^2)^{1/2} \rfloor + f(m^2) = m + f(m^2), \]
17: where $f(N) = A_N - \lfloor \sqrt{N} \rfloor$ is the number of perfect powers up to $N$ that are not squares. Using the Principle of Inclusion-Exclusion, the number of perfect powers in $\{2, \dots, N\}$ is $\sum_{j=2}^{\lfloor \log_2 N \rfloor} -\mu(j) (\lfloor N^{1/j} \rfloor - 1)$. Since $A_N$ includes the number 1, we have $A_N = 1 + \sum_{j=2}^{\lfloor \log_2 N \rfloor} -\mu(j) (\lfloor N^{1/j} \rfloor - 1)$. Thus:
18: \[ f(N) = A_N - \lfloor \sqrt{N} \rfloor = 1 + (\lfloor \sqrt{N} \rfloor - 1) + \sum_{j=3}^{\lfloor \log_2 N \rfloor} -\mu(j) (\lfloor N^{1/j} \rfloor - 1) - \lfloor \sqrt{N} \rfloor = \sum_{j=3}^{\lfloor \log_2 N \rfloor} -\mu(j) (\lfloor N^{1/j} \rfloor - 1). \]
19: We can bound $f(N)$ as:
20: \[ f(N) \le \sum_{j=3}^{\lfloor \log_2 N \rfloor} (\lfloor N^{1/j} \rfloor - 1) \le \sum_{j=3}^{\lfloor \log_2 N \rfloor} N^{1/j} \le N^{1/3} + (\log_2 N) N^{1/4}. \]
21: For $N = m^2$, $f(m^2) \le m^{2/3} + (2 \log_2 m) \sqrt{m}$, so $f(m^2) = O(m^{2/3})$.
22: 
23: Now consider the gap to the next perfect power $x_{k+1}$. The next square is $(m+1)^2$. Thus, $x_{k+1} \le (m+1)^2$. The gap $x_{k+1} - x_k$ is exactly $(m+1)^2 - m^2 = 2m + 1$ if there are no perfect powers in the open interval $(m^2, (m+1)^2)$.
24: Let $S_{non-sq}$ be the set of perfect powers that are not squares. The number of $m \in \{1, \dots, M\}$ such that $(m^2, (m+1)^2)$ contains a perfect power is at most the total number of non-square perfect powers up to $(M+1)^2$, which is $f((M+1)^2) = O(M^{2/3})$.
25: Since $\lim_{M \to \infty} \frac{f((M+1)^2)}{M} = 0$, the set of $m$ for which $(m^2, (m+1)^2)$ contains no perfect powers has density 1, and thus there are infinitely many such $m$.
26: 
27: ### 4. Final Synthesis
28: For such $m$, we have $x_k = m^2$ and $x_{k+1} = (m+1)^2$. The gap is:
29: \[ x_{k+1} - x_k = 2m + 1. \]
30: The condition $x_{k+1} - x_k \ge k$ becomes:
31: \[ 2m + 1 \ge m + f(m^2) \iff m + 1 \ge f(m^2). \]
32: Since $f(m^2) = O(m^{2/3})$, this inequality is true for all sufficiently large $m$. Because there are infinitely many such $m$, there are infinitely many $k$ such that the interval $[x_k, x_{k+1}-1]$ contains an $n$ such that $A_n = k$ and $k \mid (n + 2024)$. Each such $n$ is distinct because the intervals $[m^2, (m+1)^2-1]$ are disjoint for different $m$.
33: 
34: Thus, there are infinitely many $n$ such that $A_n$ divides $n + 2024$.
