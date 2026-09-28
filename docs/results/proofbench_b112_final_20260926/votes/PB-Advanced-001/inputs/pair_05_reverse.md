# Problem

For a positive integer $n$, let $A_{n}$ be the number of perfect powers less than or equal to $n$. Here, a perfect power is a number that can be expressed in the form $a^{b}$, where $a$ is a positive integer and $b$ is an integer greater than or equal to 2. Prove that there are infinitely many $n$ such that $A_{n}$ divides $n+2024$.

# Proof A

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
