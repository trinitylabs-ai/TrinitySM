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

# Proof B

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
