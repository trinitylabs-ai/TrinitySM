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

1: To prove that there are infinitely many positive integers $n$ such that $A_n$ divides $n + 2024$, where $A_n$ is the number of perfect powers less than or equal to $n$, we proceed as follows.
2: 
3: Let $P$ be the set of all perfect powers, defined as $P = \{ a^b \mid a \in \mathbb{Z}^+, b \in \mathbb{Z}, b \ge 2 \}$. Let the elements of $P$ be listed in increasing order as $p_1 < p_2 < p_3 < \dots$. By definition, for any integer $n$, $A_n = k$ if and only if $p_k \le n < p_{k+1}$.
4: 
5: For a fixed $k$, we seek an $n$ in the interval $[p_k, p_{k+1}-1]$ such that $A_n = k$ and $k$ divides $n + 2024$. This is equivalent to finding an $n \in [p_k, p_{k+1}-1]$ such that $n \equiv -2024 \pmod{k}$. Such an $n$ exists if the length of the interval $[p_k, p_{k+1}-1]$ is at least $k$. The length of this interval is $(p_{k+1} - 1) - p_k + 1 = p_{k+1} - p_k$. Thus, a sufficient condition for the existence of such an $n$ is $p_{k+1} - p_k \ge k$.
6: 
7: We consider the case where $p_k$ is a perfect square. Let $p_k = m^2$ for some positive integer $m$. The next perfect square is $(m+1)^2$. If there are no perfect powers in the open interval $(m^2, (m+1)^2)$, then $p_{k+1} = (m+1)^2$. In this case, the gap is:
8: $$p_{k+1} - p_k = (m+1)^2 - m^2 = 2m + 1.$$
9: The value of $k$ is $A_{m^2}$. The perfect powers $\le m^2$ include the $m$ squares $1^2, 2^2, \dots, m^2$ and some number of non-square perfect powers. Let $\epsilon_m$ be the number of non-square perfect powers $\le m^2$. Then $k = m + \epsilon_m$.
10: A non-square perfect power $x \le m^2$ must be representable as $x = a^b$ for some odd integer $b \ge 3$. The number of $b$-th powers $\le m^2$ is $\lfloor (m^2)^{1/b} \rfloor$. Thus, $\epsilon_m$ can be bounded by the sum of the number of $b$-th powers for odd $b \ge 3$:
11: $$\epsilon_m \le \sum_{b=3, 5, \dots}^{\lfloor 2 \log_2 m \rfloor} \lfloor m^{2/b} \rfloor \le m^{2/3} + \sum_{b=5}^{\lfloor 2 \log_2 m \rfloor} m^{2/b} \le m^{2/3} + (2 \log_2 m) m^{2/5}.$$
12: Since $m^{2/3} + (2 \log_2 m) m^{2/5} = o(m)$, there exists a constant $M$ such that for all $m \ge M$, $\epsilon_m \le m + 1$. Thus, for all $m \ge M$, $k = m + \epsilon_m \le 2m + 1$, and the condition $p_{k+1} - p_k \ge k$ is satisfied whenever $(m^2, (m+1)^2)$ contains no perfect powers.
13: 
14: We now prove that there are infinitely many such $m$. An integer $m$ is "bad" if $(m^2, (m+1)^2)$ contains a perfect power $a^b$. Since the interval contains no squares, we must have $b \ge 3$. The condition $m^2 < a^b < (m+1)^2$ is equivalent to $m < a^{b/2} < m+1$, which implies $m = \lfloor a^{b/2} \rfloor$.
15: For a fixed $b \ge 3$, the number of such $m \le X$ is at most the number of $a$ such that $a^{b/2} < X+1$, which is $\lfloor (X+1)^{2/b} \rfloor$. The total number of bad $m \le X$ is:
16: $$|B \cap [1, X]| \le \sum_{b=3}^{\lfloor 2 \log_2(X+1) \rfloor} (X+1)^{2/b} \le (X+1)^{2/3} + (X+1)^{1/2} + (2 \log_2(X+1)) (X+1)^{2/5}.$$
17: As $X \to \infty$, the ratio $\frac{|B \cap [1, X]|}{X} \to 0$. This implies that the set of "good" $m$ (where $(m^2, (m+1)^2) \cap P = \emptyset$) has density 1 and is therefore infinite. For each such $m \ge M$, there exists at least one $n \in [m^2, (m+1)^2 - 1]$ such that $A_n = A_{m^2}$ and $A_n \mid n + 2024$. Since these intervals are disjoint for different $m$, there are infinitely many such $n$.
