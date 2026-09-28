# Problem

Infinitely many boys and girls stand in a line alternatingly. For
 a given positive integer $N$, they choose positive integers according
 to the following rules:

 (1) The first $N$ people in the line choose any positive integers
 they want.

 (2) For each $m>N$, the $m$-th person chooses the number that is
 one more than the number of appearances of the number chosen by the
 $(m-1)$-th person appears among the numbers chosen by the first $m-2$
 people.

 Let $b_{i}$ be the number chosen by the $i$-th boy, and $g_{i}$
 be the number chosen by the $i$-th girl. Prove that at least one
 of the following holds:

 (i) There exists a sufficiently large integer $M$ such that $\{b_{n}\}_{n\ge M}$
 is a periodic sequence.

 (ii) There exists a sufficiently large integer $M$ such that $\{g_{n}\}_{n\ge M}$
 is a periodic sequence.

# Proof A

1: Let $\{x_m\}_{m \ge 1}$ be the sequence of numbers chosen by the people. For $m > N$, the recurrence is $x_m = 1 + c_{m-2}(x_{m-1})$, where $c_k(v)$ denotes the number of times $v$ appears in the sequence $x_1, \dots, x_k$.
2: 
3: 1. The Set of Infinitely Occurring Values
4: Let $S$ be the set of positive integers that appear infinitely often in the sequence $\{x_m\}$.
5: First, $S$ is non-empty. If $S = \emptyset$, then for every $v \in \mathbb{Z}^+$, $c_m(v)$ is eventually constant. If the sequence $\{x_m\}$ is bounded, it must take some value infinitely often, so $S \neq \emptyset$. If $\{x_m\}$ is unbounded, then $x_m$ must take infinitely many distinct values. Whenever $x_{m-1}$ takes a value $v$ for the first time, $c_{m-2}(v) = 0$, so $x_m = 1 + 0 = 1$. Since $x_{m-1}$ takes infinitely many distinct values, the value 1 appears infinitely often, so $1 \in S$.
6: 
7: Second, we analyze the size of $S$. Let $n_k$ be the number of times the integer $k$ appears in the sequence. A value $k$ is produced at index $m$ if and only if $x_{m-1}$ is the $k$-th occurrence of some value $v$. Thus, $n_k = \#\{v \in \mathbb{Z}^+ \mid c_\infty(v) \ge k\}$.
8: If $S$ is infinite, then for all $v \in S$, $c_\infty(v) = \infty$. Thus $n_k \ge |S| = \infty$ for all $k$, which implies $S = \mathbb{Z}^+$.
9: If $S$ is finite, let $s = |S|$. Then for any $k \notin S$, $n_k$ must be finite. From the formula $n_k = s + \#\{v \notin S \mid c_\infty(v) \ge k\}$, this implies that for any $k \notin S$, only finitely many $v \notin S$ appear at least $k$ times.
10: 
11: 2. Parity and Periodicity
12: Case 1: $S = \mathbb{Z}^+$.
13: Consider the indices $m$ where $x_m = 1$. These occur whenever $x_{m-1}$ is the first occurrence of some value $v$. Since $S = \mathbb{Z}^+$, there are infinitely many such $v$. Let $m_1 < m_2 < \dots$ be these indices. Then $x_{m_j} = 1$.
14: The next term is $x_{m_j+1} = 1 + c_{m_j-1}(1)$. As $j \to \infty$, $c_{m_j-1}(1) \to \infty$, so $x_{m_j+1} \to \infty$.
15: The indices $m_j$ and $m_j+1$ have opposite parity. One subsequence (say $\{g_n\}$) contains the values $x_{m_j} = 1$ infinitely often, while the other ($\{b_n\}$) contains the values $x_{m_j+1} \to \infty$.
16: If $x_m$ is eventually periodic, we are done. If not, we examine the structure. For large $j$, $x_{m_j} = 1$ and $x_{m_j+1} = j + C$. Then $x_{m_j+2} = 1 + c_{m_j}(j+C)$. Since $j+C$ is large, it has appeared very few times. In fact, $c_{m_j}(j+C)$ is the number of $v \in S$ that have already produced the value $j+C$. Since $S = \mathbb{Z}^+$, every $v$ produces $j+C$ exactly once. Thus $c_{m_j}(j+C)$ is the number of $v$ such that $c_{i-2}(v) = j+C-1$ for some $i \le m_j$.
17: As $j \to \infty$, the number of such $v$ is the number of $v$ that have appeared at least $j+C$ times. But for any fixed $m_j$, only finitely many $v$ have appeared that many times. Thus $x_{m_j+2}$ is bounded.
18: Since the sequence returns to bounded values on one parity, and the transitions are deterministic, the subsequence on that parity is eventually periodic.
19: 
20: Case 2: $S$ is finite.
21: Let $S = \{v_1, \dots, v_s\}$. For large $m$, if $x_{m-1} \in S$, then $c_{m-2}(x_{m-1}) \to \infty$, so $x_m = 1 + c_{m-2}(x_{m-1}) \to \infty$. Thus $x_m \notin S$.
22: Then $x_{m+1} = 1 + c_{m-1}(x_m)$. As $x_m$ is large, $c_{m-1}(x_m)$ is the number of $v \in S$ such that $c_{i-2}(v) = x_m - 1$ for some $i \le m$.
23: This count is exactly the number of $v \in S$ such that $c_{m-1}(v) \ge x_m$.
24: Since $x_m$ is produced by $x_{m-1} \in S$, and each $v \in S$ produces any large value $L$ exactly once, $c_{m-1}(x_m) \le s$.
25: Thus $x_{m+1} \le s+1$. Since $S$ is the set of values appearing infinitely often, the sequence must return to $S$.
26: For large $m$, if $x_{m-1} \in S$, then $x_m \notin S$ and $x_{m+1} \in S \cup \{1, \dots, s+1\}$.
27: This implies that all elements of $S$ eventually appear on indices of the same parity.
28: Let this parity be $p$. The subsequence $\{x_m\}_{m \equiv p \pmod 2}$ takes values in the finite set $S \cup \{1, \dots, s+1\}$.
29: The transition $x_{m-1} \to x_{m+1}$ is $x_{m+1} = 1 + \#\{v \in S \mid c_{m-1}(v) \ge 1 + c_{m-2}(x_{m-1})\}$.
30: As $m \to \infty$, the counts $c_{m-1}(v)$ for $v \in S$ all grow. The value $x_{m+1}$ depends only on the relative ranks of the counts of the elements of $S$.
31: Since there are only $s!$ possible rankings of the counts of $S$, the state $(x_{m-1}, \text{rankings})$ is finite.
32: Thus, the subsequence on parity $p$ is eventually periodic.
33: 
34: In all cases, at least one of $\{b_n\}$ or $\{g_n\}$ is eventually periodic.

# Proof B

1: To prove that at least one of the sequences $\{b_n\}$ or $\{g_n\}$ is eventually periodic, we analyze the behavior of the sequence $a_m$ defined by $a_m = 1 + C(a_{m-1}, m-2)$ for $m > N$, where $C(x, m)$ is the number of times $x$ appears in $\{a_1, \dots, a_m\}$.
2: 
3: **1. Existence of the value 1**
4: First, we show that the value 1 must appear in the sequence for $m > N$. Suppose $a_m \neq 1$ for all $m > N$. Then $a_m = 1 + C(a_{m-1}, m-2) \ge 2$ for all $m > N$. This implies that $C(a_{m-1}, m-2) \ge 1$, so $a_{m-1}$ must have appeared at least once in the first $m-2$ terms. By induction, this means every $a_m$ for $m > N$ must be a value already present in the set $\{a_1, \dots, a_N\}$. Let this finite set be $V$. Since the sequence is infinite and only takes values from $V$, at least one value $v \in V$ must appear infinitely often. Then $C(v, m) \to \infty$ as $m \to \infty$. However, whenever $a_{m-1} = v$, we have $a_m = 1 + C(v, m-2)$, which also tends to infinity. This contradicts the assumption that $a_m$ only takes values from the finite set $V$. Thus, $a_m = 1$ for some $m > N$.
5: 
6: **2. The "1 $\to$ Large $\to$ 1" Cycle**
7: Suppose $a_m = 1$ for some sufficiently large $m$. Then $a_{m+1} = 1 + C(1, m-1)$. Let $K = 1 + C(1, m-1)$. We examine $a_{m+2} = 1 + C(K, m)$.
8: $C(K, m)$ is the number of times $K$ appeared in $\{a_1, \dots, a_m\}$. For $a_i = K$ to occur for $i \le m$, we must have $C(a_{i-1}, i-2) = K-1 = C(1, m-1)$.
9: 
10: We observe that $a_j = 1$ whenever $a_{j-1}$ is a "new" value (one that has not appeared in the first $j-2$ terms). Conversely, whenever $a_{j-1} = 1$, the next term $a_j = 1 + C(1, j-2)$ is a value that grows as $j$ increases. For sufficiently large $j$, $a_j$ will be larger than any value previously appearing in the sequence. This creates a feedback loop where 1s and new large values appear in alternating fashion. Consequently, $C(1, m)$ grows linearly with $m$, while any value $x > \max(a_1, \dots, a_N)$ appears at most once because the values $1 + C(1, j-2)$ are strictly increasing for $j$ where $a_{j-1}=1$.
11: 
12: Now consider $i \le m$. The count $C(a_{i-1}, i-2)$ is bounded by the maximum frequency of any element in the first $i-2$ terms. For sufficiently large $m$, $C(1, m-1)$ will exceed the frequency of any element $x \neq 1$ in the first $m-2$ terms. Specifically, if $a_{i-1} \neq 1$, then $C(a_{i-1}, i-2)$ is small (bounded by a constant or growing much slower than $C(1, m)$). If $a_{i-1} = 1$, then $C(1, i-2) \le C(1, m-2)$. If $a_{m-1} = 1$, then $C(1, m-2) < C(1, m-1)$. If $a_{m-1} \neq 1$, then $C(1, m-2) = C(1, m-1)$, but we can choose $m$ large enough such that $C(1, m-1)$ is strictly greater than any $C(a_{i-1}, i-2)$ for $i \le m$ where $a_{i-1} \neq 1$.
13: 
14: Therefore, $C(a_{i-1}, i-2) < C(1, m-1)$ for all $i \le m$, which implies $C(K, m) = 0$. Thus, $a_{m+2} = 1 + 0 = 1$.
15: 
16: **3. Periodicity of Boys or Girls**
17: We have shown that if $a_m = 1$ for a sufficiently large $m$, then $a_{m+2} = 1$. By induction, $a_m = a_{m+2} = a_{m+4} = \dots = 1$.
18: The sequence $a_n$ consists of alternating boys and girls. If $m$ is odd, then $a_m, a_{m+2}, a_{m+4}, \dots$ are the numbers chosen by the boys $b_k, b_{k+1}, b_{k+2}, \dots$ for some $k$. If $m$ is even, they are the numbers chosen by the girls $g_k, g_{k+1}, g_{k+2}, \dots$.
19: In either case, one of the sequences $\{b_n\}_{n \ge M}$ or $\{g_n\}_{n \ge M}$ is eventually constant 1. A constant sequence is periodic with period 1.
20: 
21: Thus, at least one of the sequences $\{b_n\}_{n \ge M}$ or $\{g_n\}_{n \ge M}$ is periodic.
22: 
23: \(\square\)
