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

1: Let $S = \{s_1, s_2, s_3, \dots\}$ be the set of all perfect powers listed in strictly increasing order. A perfect power is defined as an integer of the form $a^b$, where $a$ is a positive integer and $b$ is an integer $\ge 2$. Let $A_n$ denote the number of perfect powers less than or equal to $n$. By definition, for any positive integer $k$, $A_n = k$ if and only if $s_k \le n < s_{k+1}$.
2: 
3: We wish to show that there are infinitely many $n$ such that $A_n$ divides $n+2024$. For a fixed $k$, this requires finding $n \in [s_k, s_{k+1}-1]$ such that:
4: \[ n \equiv -2024 \pmod{k}. \]
5: Such an $n$ exists if and only if the interval $[s_k, s_{k+1}-1]$ contains an integer congruent to $-2024 \pmod{k}$. An interval of $L$ consecutive integers contains at least one representative of every residue class modulo $k$ if $L \ge k$. The number of integers in the interval $[s_k, s_{k+1}-1]$ is:
6: \[ (s_{k+1}-1) - s_k + 1 = s_{k+1} - s_k. \]
7: Thus, if $s_{k+1} - s_k \ge k$, there exists at least one $n \in [s_k, s_{k+1}-1]$ such that $A_n \mid n+2024$.
8: 
9: Let $P_2 = \{a^2 : a \in \mathbb{Z}^+\}$ be the set of perfect squares and $P_{>2} = S \setminus P_2$ be the set of perfect powers that are not squares. Let $E_n$ denote the number of elements of $P_{>2}$ that are less than or equal to $n$. We can bound $E_n$ by summing the number of $b$-th powers for $b \ge 3$:
10: \[ E_n \le \sum_{b=3}^{\lfloor \log_2 n \rfloor} \lfloor n^{1/b} \rfloor \le n^{1/3} + (\log_2 n - 2)n^{1/4}. \]
11: Now, consider $k = A_{m^2}$ for some positive integer $m$. Since $m^2$ is a perfect square, the number of perfect powers up to $m^2$ is the sum of the number of squares and the number of non-square perfect powers:
12: \[ k = A_{m^2} = \lfloor \sqrt{m^2} \rfloor + E_{m^2} = m + E_{m^2}. \]
13: The next perfect power $s_{k+1}$ is the smallest element of $S$ strictly greater than $m^2$. If there are no non-square perfect powers in the interval $(m^2, (m+1)^2)$, then the next perfect power is the next square, so $s_{k+1} = (m+1)^2$. In this case, the gap is:
14: \[ s_{k+1} - s_k = (m+1)^2 - m^2 = 2m + 1. \]
15: The condition $s_{k+1} - s_k \ge k$ then becomes:
16: \[ 2m + 1 \ge m + E_{m^2} \implies m + 1 \ge E_{m^2}. \]
17: Using our bound for $E_n$, we have $E_{m^2} \le (m^2)^{1/3} + \log_2(m^2)(m^2)^{1/4} = m^{2/3} + 2m^{1/2} \log_2 m$. Since $m$ grows faster than $m^{2/3}$ and $m^{1/2} \log_2 m$, the inequality $m + 1 \ge E_{m^2}$ holds for all $m \ge M_0$ for some constant $M_0$.
18: 
19: Finally, we show that the condition $(m^2, (m+1)^2) \cap P_{>2} = \emptyset$ occurs for infinitely many $m$. Let $N$ be a large integer. The number of $m \in \{1, 2, \dots, N\}$ such that the interval $(m^2, (m+1)^2)$ contains at least one non-square perfect power is at most the total number of non-square perfect powers up to $(N+1)^2$, which is $E_{(N+1)^2}$.
20: We have $E_{(N+1)^2} \le (N+1)^{2/3} + 2(N+1)^{1/2} \log_2(N+1)$. As $N \to \infty$, the ratio $\frac{E_{(N+1)^2}}{N} \to 0$.
21: This implies that for almost all $m$, the interval $(m^2, (m+1)^2)$ contains no non-square perfect powers. Thus, there are infinitely many $m \ge M_0$ such that $s_{k+1} - s_k \ge k$ for $k = A_{m^2}$.
22: 
23: Each such $m$ yields a distinct $k$, and each $k$ yields at least one $n \in [s_k, s_{k+1}-1]$ such that $A_n \mid n+2024$. Since $s_k = m^2 \to \infty$ as $m \to \infty$, these values of $n$ are distinct. Thus, there are infinitely many such $n$.
