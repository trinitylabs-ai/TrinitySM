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

1: Let $a_m$ be the sequence of integers chosen by the people in the line. The rule for $m > N$ is $a_m = 1 + c_{m-2}(a_{m-1})$, where $c_m(x)$ denotes the number of times $x$ appears in the set $\{a_1, \dots, a_m\}$.
2: 
3: First, we prove that $a_m$ is unbounded. Suppose $a_m \le K$ for all $m$. Then for any $x \in \{1, \dots, K\}$, the count $c_m(x)$ must also be bounded by $K$. Indeed, if $c_m(x) \ge K$ for some $m$, then the next time $x$ is chosen as $a_{m+1}$, the following term $a_{m+2} = 1 + c_m(x) \ge K+1$, contradicting the bound. However, since $\sum_{x=1}^K c_m(x) = m$, at least one $c_m(x)$ must tend to infinity as $m \to \infty$. This contradiction proves that $a_m$ is unbounded.
4: 
5: Whenever $a_m$ is a value that has not appeared before (a "new" value), $c_{m-1}(a_m) = 0$, so $a_{m+1} = 1 + 0 = 1$. Since $a_m$ is unbounded, it takes infinitely many distinct values, and thus the value 1 appears infinitely often. Let $k_j$ be the index of the $j$-th occurrence of 1 in the sequence $\{a_m\}$. Then $a_{k_j} = 1$. The next term is $a_{k_j+1} = 1 + c_{k_j-1}(a_{k_j}) = 1 + c_{k_j-1}(1)$. Since $a_{k_j}$ is the $j$-th occurrence of 1, $c_{k_j-1}(1) = j-1$. Thus, $a_{k_j+1} = j$.
6: 
7: Now consider $a_{k_j+2} = 1 + c_{k_j}(a_{k_j+1}) = 1 + c_{k_j}(j)$. We examine when the value $j$ appears in the sequence. According to the rule, $a_m = j$ if and only if $a_{m-1}$ is the $(j-1)$-th occurrence of some value $v$. Let $T(v, i)$ be the index of the $i$-th occurrence of $v$. Then $a_m = j$ if and only if $m = T(v, j-1) + 1$ for some $v$.
8: 
9: We claim that for sufficiently large $j$, $c_{k_j}(j) = 0$. Note that if $a_m$ is the $i$-th occurrence of any value $v$, then $a_{m+1} = 1 + c_{m-1}(v) = 1 + (i-1) = i$. This means that every $i$-th occurrence of any value $v$ creates an occurrence of the value $i$ at the very next index. Consequently, if $T(v, i)$ is the index of the $i$-th occurrence of $v$, then $T(v, i) + 1$ is the index of some occurrence of $i$. Since $T(v, i) \ge T(1, i) = k_i$ for all $v$ and $i$, it follows that any occurrence of the value $j$ must occur at an index $m \ge k_j + 1$. Therefore, in the set $\{a_1, \dots, a_{k_j}\}$, the value $j$ cannot appear, so $c_{k_j}(j) = 0$.
10: 
11: It follows that $a_{k_j+2} = 1 + 0 = 1$ for all sufficiently large $j$. This implies that $k_{j+1} = k_j + 2$ for all sufficiently large $j$. The sequence $a_m$ for $m \ge M$ (where $M$ is some sufficiently large integer) thus follows the pattern:
12: $a_{k_j} = 1, a_{k_j+1} = j, a_{k_j+2} = 1, a_{k_j+3} = j+1, a_{k_j+4} = 1, \dots$
13: 
14: The boys' and girls' sequences are formed by taking every other element of $\{a_m\}$. One of these sequences will pick the elements $a_{k_j}, a_{k_j+2}, a_{k_{j+1}}, \dots$, which corresponds to the sequence $1, 1, 1, \dots$. This sequence is constant and therefore periodic. The other sequence will pick the growing terms $j, j+1, j+2, \dots$, which is not periodic. Thus, at least one of the sequences $\{b_n\}$ or $\{g_n\}$ is eventually periodic.
