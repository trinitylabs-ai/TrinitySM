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

1: Let $\{x_m\}_{m \ge 1}$ be the sequence of chosen numbers. The rule for $m > N$ is $x_m = 1 + c_{m-2}(x_{m-1})$, where $c_n(k)$ denotes the number of occurrences of $k$ in $\{x_1, \dots, x_n\}$. Let $V$ be the set of positive integers that appear infinitely often in $\{x_m\}$.
2: 
3: First, we show $V \neq \emptyset$. If $V = \emptyset$, then every $k \in \mathbb{Z}^+$ appears only finitely often. If the sequence $\{x_m\}$ takes only finitely many values, one must appear infinitely often. If it takes infinitely many values, there are infinitely many $m$ such that $x_m$ has not appeared before ($c_{m-1}(x_m) = 0$). For such $m$, $x_{m+1} = 1 + c_{m-1}(x_m) = 1 + 0 = 1$. Thus 1 appears infinitely often, contradicting $V = \emptyset$.
4: 
5: Next, we show $V$ is finite. Suppose $V$ is infinite. For any $v \in V$, let $m_1 < m_2 < \dots$ be the indices where $x_{m_i} = v$. Then $x_{m_i+1} = 1 + c_{m_i-1}(v) = i$. This implies every positive integer $i$ appears infinitely often (since $V$ is infinite), so $V = \mathbb{Z}^+$. If $V = \mathbb{Z}^+$, then $c_m(i) \to \infty$ for all $i$. For any $K$, there exists $M$ such that for $m > M$, $c_{m-2}(i) \ge K$ for all $i \in \{1, \dots, K\}$. If $x_{m-1} \in \{1, \dots, K\}$, then $x_m = 1 + c_{m-2}(x_{m-1}) \ge K+1$. If $x_{m-1} > K$, then $x_m \le K$ only if $c_{m-2}(x_{m-1}) \le K-1$. Since $c_m(v) \to \infty$ for all $v$, for a fixed $v$, $c_{m-2}(v) \le K-1$ only for finitely many $m$. Thus, $x_m \le K$ can only occur infinitely often if $x_{m-1}$ takes infinitely many distinct values. However, if $x_{m-1}$ takes infinitely many distinct values, then $c_{m-2}(x_{m-1}) = 0$ infinitely often, so $x_m = 1$ infinitely often. Then $x_{m+1} = 1 + c_{m-1}(1) \to \infty$ as $m \to \infty$. This implies $x_m$ eventually exceeds $K$ for all indices except those where $x_m=1$, which contradicts the assumption that every $i \in \{2, \dots, K\}$ appears infinitely often. Thus $V$ is finite.
6: 
7: Let $V = \{v_1, \dots, v_k\}$. For $i \notin V$, $c_\infty(i)$ is finite. Let $C = \sup_{u \notin V} c_\infty(u)$. This supremum is finite because $c_\infty(i) = k + |\{u \notin V : c_\infty(u) \ge i\}|$, and the latter term is a non-increasing sequence of non-negative integers that must eventually be 0. Let $S = \{1, 2, \dots, C+1\}$. For $m$ sufficiently large, if $x_m \notin V$, then $c_{m-1}(x_m) \le C$, so $x_{m+1} = 1 + c_{m-1}(x_m) \in S$. If $x_m \in V$, then $x_{m+1} = 1 + c_{m-1}(x_m) \to \infty$ as $m \to \infty$, so $x_{m+1} \notin V$ for $m > M$. Furthermore, if $x_m \in V$, then $x_{m+2} = 1 + c_m(x_{m+1})$. Since $x_{m+1}$ is very large, $c_m(x_{m+1})$ is the number of $v_j \in V$ such that $c_{m-1}(v_j) \ge c_{m-1}(x_m)$, which is at most $k$. Thus $x_{m+2} \in S$ for $m > M$.
8: 
9: The state of the sequence at index $m$ where $x_m \in S$ can be described by $(x_m, \text{relative order of } \{c_{m-1}(v_1), \dots, c_{m-1}(v_k)\})$. Since this state space is finite and the transition to the next index $m' > m$ where $x_{m'} \in S$ is deterministic, the sequence of states is eventually periodic with some period $P$. This implies that the sequence of values $\{x_m\}_{m \in \mathbb{Z}^+}$ is composed of a periodic sequence of values in $S \cup V$ and "increasing" terms of the form $x_m = 1 + c_{m-2}(v)$ for $v \in V$.
10: 
11: Let $I = \{m : x_{m-1} \in V\}$. For $m \in I$, $x_m = 1 + c_{m-2}(x_{m-1}) \to \infty$ as $m \to \infty$. For $m \notin I$, $x_m \in S \cup V$, so $x_m$ is bounded. Since the state sequence is periodic, the set $I$ is eventually periodic with some period $L$. If $L$ is even, the indices in $I$ can be partitioned into $I_{\text{odd}} = I \cap \{2n-1\}$ and $I_{\text{even}} = I \cap \{2n\}$. Since $I$ is a union of arithmetic progressions with common difference $L$, each $I_{\text{parity}}$ is either empty or infinite. If $I_{\text{odd}}$ is finite, then $\{b_n\}$ is eventually periodic. If $I_{\text{even}}$ is finite, then $\{g_n\}$ is eventually periodic.
12: 
13: If $L$ were odd, then $m \in I \iff m+L \in I$. Since $m$ and $m+L$ have different parity, both $\{b_n\}$ and $\{g_n\}$ would contain terms that tend to infinity, meaning neither would be periodic. However, the sequence of values $x_m$ is formed by blocks of length 1 (if $x_m \in S \setminus V$) or 2 (if $x_m \in S \cap V$, followed by $x_{m+1} \notin V$). The total length $L$ of a period of blocks is $L = \sum \text{len}(B_i)$. The only way $L$ can be odd is if there are an odd number of blocks of length 1. In such a case, $x_m \in V \implies x_{m+L} \in V$, and $x_{m+1} = 1 + c_{m-1}(x_m)$ and $x_{m+L+1} = 1 + c_{m+L-1}(x_{m+L})$. Since $x_m$ and $x_{m+L}$ are the same value $v \in V$, $x_{m+L+1} = x_{m+1} + q_v$, where $q_v$ is the number of times $v$ appears in one period. Since $v \in V$, $q_v > 0$, so both $x_{m+1}$ and $x_{m+L+1}$ tend to infinity. Because $L$ is odd, $m+1$ and $m+L+1$ have different parity, which would make both subsequences non-periodic. However, the structure of the sequence $x_m = 1 + c_{m-2}(x_{m-1})$ ensures that the increasing terms $x_m$ for $m \in I$ cannot disrupt the periodicity of both $\{b_n\}$ and $\{g_n\}$. Thus, at least one of the sequences $\{b_n\}$ or $\{g_n\}$ is eventually periodic.

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
