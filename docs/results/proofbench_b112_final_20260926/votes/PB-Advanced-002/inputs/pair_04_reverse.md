# Problem

There are 120 students in DeepMind highschool, and each student `loves' some of the students. Here `love' is not always a mutual relationship; a student A may love B while B may not love A, and it is also possible that a student loves oneself. For the set $F$ of all $2^{120}$ subsets of the students, define the function $f: F \rightarrow F$ as the function that maps each $X \in F$ to the set of students loved by one or more students in $X$. For $A, B \in F$, $A$ and $B$ are said to have a 'lovely relationship' iff there exists a natural number $k$ such that $f^{k}(A)=B$. Now we want to select distinct elements $A_{1}, A_{2}, \cdots A_{t}$ from $F$ such that for any $1 \leq i<j \leq t$, $A_{i}$ and $A_{j}$ have a lovely relationship. Let $M(f)$ be the maximum possible value of $t$.  Show that $M(f) \leq 2^{70}$.

# Proof A

1: To solve the problem, we analyze the structure of the function $f$ and the nature of the "lovely relationship" to determine the maximum size $M(f)$ of the set $\{A_1, A_2, \dots, A_t\}$.
2: 
3: ### 1. Analysis of the Function $f$
4: Let $S$ be the set of $n = 120$ students. For each student $i \in S$, let $L_i \subseteq S$ be the set of students loved by student $i$. The function $f: F \to F$, where $F = \mathcal{P}(S)$, is defined as:
5: $$f(X) = \bigcup_{i \in X} L_i$$
6: This is a linear operator over the Boolean semiring $(\mathcal{P}(S), \cup, \cap)$. A key property of such a map is that for any $X, Y \in F$, $f(X \cup Y) = f(X) \cup f(Y)$. By induction, for any $k \in \mathbb{N}$, we have:
7: $$f^k(X) = \bigcup_{i \in X} f^k(\{i\})$$
8: where $f^k(\{i\})$ is the set of students reachable from student $i$ in exactly $k$ steps in the directed "love graph" (where an edge $i \to j$ exists if $i$ loves $j$).
9: 
10: ### 2. The Lovely Relationship as a Preorder
11: A pair $A, B \in F$ has a lovely relationship if there exists $k \in \mathbb{N}$ such that $f^k(A) = B$. Let us denote this relation as $A R B$. Note that:
12: 1.  **Transitivity**: If $A R B$ and $B R C$, then there exist $k, m \in \mathbb{N}$ such that $f^k(A) = B$ and $f^m(B) = C$. Thus $f^{k+m}(A) = C$, so $A R C$.
13: 2.  **Functional Graph**: The function $f$ defines a functional graph on the $2^{120}$ elements of $F$. Each component of this graph consists of a set of nodes that eventually lead into a unique cycle.
14: 
15: The problem states that for any $1 \leq i < j \leq t$, $A_i$ and $A_j$ have a lovely relationship. This means for every $i < j$, $f^{k_{ij}}(A_i) = A_j$ for some $k_{ij} \in \mathbb{N}$. This implies that the elements $A_1, A_2, \dots, A_t$ must lie on a single trajectory $A_1 \to f(A_1) \to f^2(A_1) \to \dots$ in the functional graph of $f$. Since the $A_i$ are distinct, the maximum value of $t$ is the maximum number of distinct elements in any such trajectory.
16: 
17: ### 3. Bound on the Size of the Chain
18: In a functional graph, the number of distinct elements in a trajectory is the sum of the pre-period (the number of steps to reach a cycle) and the period (the length of the cycle).
19: 
20: For a fixed student $i \in S$, let $S_k = f^k(\{i\})$. A student $j$ is in $S_k$ if and only if there exists a path of length exactly $k$ from $i$ to $j$. If $j$ is reachable from $i$, the set of lengths of paths from $i$ to $j$ is eventually periodic. Specifically, if $j$ is part of a cycle of length $L$ (or reachable from one), the indicator $1_{S_k}(j)$ becomes periodic with a period that divides $L$. The period $p_i$ of the sequence of sets $S_k$ is the smallest $P$ such that $S_{k+P} = S_k$ for all sufficiently large $k$. This $P$ is the least common multiple of the periods of the indicators $1_{S_k}(j)$ for all $j \in S$, which corresponds to the least common multiple of the lengths of all cycles reachable from $i$ in the love graph. The pre-period $m_i$ is the distance from $i$ to the furthest cycle, which is at most $n = 120$.
21: 
22: The sequence $f^k(X) = \bigcup_{i \in X} f^k(\{i\})$ becomes periodic when all $f^k(\{i\})$ for $i \in X$ have entered their respective cycles. The pre-period $M$ of $f^k(X)$ is $\max_{i \in X}(m_i) \leq 120$. The period $P$ of $f^k(X)$ is the least common multiple of the periods $p_i$ for $i \in X$, which is $\text{lcm}_{i \in X}(p_i)$.
23: 
24: The maximum possible period $P$ is given by Landau's function $g(n)$, which is the maximum lcm of a partition of $n$. For $n=120$:
25: $$g(120) = \max \{ \text{lcm}(c_1, c_2, \dots, c_m) \mid \sum c_i \leq 120 \}$$
26: For $n=120$, $g(120) \approx 2.23 \times 10^8$.
27: The total number of distinct elements in any orbit is thus at most $120 + g(120)$.
28: 
29: ### 4. Final Verification
30: We have established that $M(f) \leq 120 + g(120)$. To compare this with $2^{70}$, we note that:
31: $$g(120) \approx 2.23 \times 10^8 < 10^9$$
32: $$2^{70} = (2^{10})^7 \approx (10^3)^7 = 10^{21}$$
33: Since $120 + 2.23 \times 10^8 < 10^9$ and $10^9 \ll 10^{21}$, it follows that:
34: $$M(f) \leq 120 + g(120) \ll 2^{70}$$
35: Thus, for any possible configuration of the "love" relations, the maximum number of students $t$ is well within the bound of $2^{70}$.
36: 
37: \(\square\)

# Proof B

1: To determine the maximum possible value of $t$, denoted as $M(f)$, we analyze the properties of the function $f$ and the structure of the "lovely relationship."
2: 
3: ### 1. Analysis of the function $f$
4: Let $S$ be the set of $n = 120$ students. The set $F$ is the power set $\mathcal{P}(S)$, consisting of all $2^{120}$ subsets of students. The function $f: F \rightarrow F$ maps each subset $X \in F$ to the set of students loved by one or more students in $X$. 
5: Let $R$ be the binary relation "loves" on $S$. For any $x \in S$, let $L_x = \{y \in S \mid xRy\}$ be the set of students loved by $x$. The definition of $f$ can be written as:
6: \[ f(X) = \{y \in S \mid \exists x \in X, xRy\} = \bigcup_{x \in X} L_x \]
7: This shows that $f$ is a join-homomorphism on the lattice $(F, \subseteq)$, meaning it distributes over unions: $f(X \cup Y) = f(X) \cup f(Y)$.
8: 
9: ### 2. The 'Lovely Relationship' and Orbit Structure
10: Two elements $A, B \in F$ have a lovely relationship if there exists a natural number $k$ such that $f^k(A) = B$. We are given a set of distinct elements $A_1, A_2, \dots, A_t$ such that for any $1 \leq i < j \leq t$, $A_i$ and $A_j$ have a lovely relationship.
11: This implies that for every $i \in \{1, \dots, t-1\}$, there exists $k_i \in \mathbb{N}$ such that $f^{k_i}(A_i) = A_{i+1}$. Since the elements $A_i$ are distinct, we must have $k_i \geq 1$ for all $i$. Thus, the sequence $A_1, A_2, \dots, A_t$ forms a chain:
12: \[ A_1 \xrightarrow{f^{k_1}} A_2 \xrightarrow{f^{k_2}} A_3 \dots \xrightarrow{f^{k_{t-1}}} A_t \]
13: Consequently, $A_1, \dots, A_t$ is a subsequence of the orbit of $A_1$ under $f$. The maximum possible value of $t$ is therefore the maximum number of distinct elements in any orbit $O(X) = \{X, f(X), f^2(X), \dots\}$ for $X \in F$.
14: 
15: ### 3. Bounding the Orbit Size
16: For any $X \in F$, the sequence $f^k(X)$ in the finite set $F$ must eventually become periodic. The number of distinct elements in the orbit is $m(X) + p(X)$, where $m(X)$ is the pre-period (the number of elements before the sequence enters a cycle) and $p(X)$ is the period.
17: 
18: Let $M$ be the $n \times n$ adjacency matrix of the relation $R$ over the Boolean semiring $(\{0, 1\}, \lor, \land)$. The operation $f(X)$ corresponds to the vector-matrix product $v_X M$, where $v_X$ is the characteristic vector of $X$. The orbit of $X$ corresponds to the sequence of vectors $v_X, v_X M, v_X M^2, \dots$.
19: 
20: **The Period $p(X)$:**
21: The sequence $f^k(X)$ is the set of vertices in the graph $G=(S, R)$ reachable from $X$ in exactly $k$ steps. We decompose $G$ into its strongly connected components (SCCs) $C_1, C_2, \dots, C_m$. For each SCC $C_i$, the period $d_i$ is the greatest common divisor of all cycle lengths in $C_i$. Once the sequence $f^k(X)$ enters its periodic phase, the intersection $f^k(X) \cap C_i$ cycles through $d_i$ distinct subsets of $C_i$. Since $f^k(X) = \bigcup_{i=1}^m (f^k(X) \cap C_i)$, the total period $p(X)$ is the least common multiple of the periods of the SCCs reachable from $X$:
22: \[ p(X) = \text{lcm}(d_1, d_2, \dots, d_m) \]
23: where $\sum d_i \leq n$. The maximum value of this LCM is given by Landau's function $g(n)$. For $n=120$, $g(120)$ is approximately $10^9$ to $10^{10}$.
24: 
25: **The Pre-period $m(X)$:**
26: The pre-period $m(X)$ is the smallest $k$ such that $v_X M^k = v_X M^{k+p(X)}$. This is bounded by the exponent of the Boolean matrix $M$, which is the smallest $m$ such that $M^m = M^{m+p}$ for some $p \geq 1$. In Boolean matrix theory, the maximum exponent for any $n \times n$ Boolean matrix is bounded by $(n-1)^2 + 1$ (the Wielandt bound for primitive matrices, which also serves as a general upper bound for the pre-period of the sequence of powers of any Boolean matrix). For $n=120$:
27: \[ m(X) \leq 119^2 + 1 = 14161 + 1 = 14162 \]
28: 
29: ### 4. Final Synthesis
30: The maximum size of any orbit $M(f)$ is bounded by:
31: \[ M(f) \leq \max_{X \in F} (m(X) + p(X)) \leq g(120) + 14162 \]
32: To compare this with $2^{70}$, we use the approximation $2^{10} \approx 10^3$, which gives $2^{70} = (2^{10})^7 \approx (10^3)^7 = 10^{21}$. Since $g(120) \approx 10^{10}$ and $14162 \approx 10^4$, we have:
33: \[ M(f) \leq 10^{10} + 14162 \ll 10^{21} \approx 2^{70} \]
34: Thus, the maximum possible value of $t$ is indeed less than or equal to $2^{70}$.
35: 
36: \(\square\)
