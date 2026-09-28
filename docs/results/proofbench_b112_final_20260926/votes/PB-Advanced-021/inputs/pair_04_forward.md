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
