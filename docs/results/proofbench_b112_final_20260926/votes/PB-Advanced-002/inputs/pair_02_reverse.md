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

1: To solve the problem, we first analyze the structure of the function $f: F \to F$. Let $S$ be the set of $N=120$ students. The set $F = \mathcal{P}(S)$ is the power set of $S$, containing $2^{120}$ elements. The function $f$ is defined such that for any $X \in F$, $f(X) = \{y \in S \mid \exists x \in X, x \text{ loves } y\}$. 
2: 
3: Let $L \subseteq S \times S$ be the "love" relation, where $(x, y) \in L$ if student $x$ loves student $y$. For each $x \in S$, let $L(x) = \{y \in S \mid (x, y) \in L\}$. Then the function $f$ can be expressed as:
4: \[ f(X) = \bigcup_{x \in X} L(x) \]
5: This function is a join-homomorphism on the Boolean lattice $(F, \subseteq)$, meaning $f(X \cup Y) = f(X) \cup f(Y)$ for all $X, Y \in F$.
6: 
7: We can represent each subset $X \in F$ as a row vector $v \in \{0, 1\}^N$, and the relation $L$ as an $N \times N$ Boolean adjacency matrix $M$, where $M_{xy} = 1$ if $x$ loves $y$ and $0$ otherwise. The action of $f$ corresponds to Boolean matrix multiplication: $f(X) \leftrightarrow vM$. The $k$-th iteration of $f$ is then $f^k(X) \leftrightarrow vM^k$.
8: 
9: A "lovely relationship" between $A, B \in F$ is defined as $A \sim B \iff \exists k \in \mathbb{N}$ such that $f^k(A) = B$. We are looking for the maximum size $t$ of a set $\{A_1, A_2, \dots, A_t\} \subset F$ such that for any $1 \leq i < j \leq t$, $A_i \sim A_j$. This condition implies that for every pair $(i, j)$ with $i < j$, there exists $k_{ij} \in \mathbb{N}$ such that $f^{k_{ij}}(A_i) = A_j$. This forces the elements to form a chain in the functional graph of $f$:
10: \[ A_1 \to A_2 \to A_3 \to \dots \to A_t \]
11: where $A \to B$ denotes the existence of $k \in \mathbb{N}$ such that $f^k(A) = B$. Since the elements $A_i$ are distinct, the sequence $\{A_i\}$ must be a subsequence of the trajectory $\{f^k(A_1) \mid k \ge 0\}$. Thus, $M(f)$ is the maximum number of distinct elements in any trajectory $\{v, vM, vM^2, \dots\}$ for $v \in \{0, 1\}^N$.
12: 
13: For any Boolean matrix $M$, the sequence $M^k$ is eventually periodic. Let $P$ be the pre-period (the exponent of the matrix) and $C$ be the period. The number of distinct vectors in the sequence $vM^k$ is at most $P + C$.
14: 1. The period $C$ is the least common multiple of the periods of the strongly connected components (SCCs) of the graph defined by $M$. The period of an SCC is the greatest common divisor of its cycle lengths. The maximum possible value for $C$ is given by Landau's function $g(N)$. For $N=120$, $g(120) \approx 3 \times 10^6$.
15: 2. The pre-period $P$ is the smallest $k$ such that $M^{k+C} = M^k$. For any Boolean matrix of size $N$, the exponent is bounded by $O(N^2)$. Specifically, $P \le N^2 = 120^2 = 14400$.
16: 
17: The maximum number of distinct elements in a trajectory is thus $M(f) \le P + C \approx 3 \times 10^6 + 14400$. Since $3.0144 \times 10^6$ is significantly smaller than $2^{70} \approx 1.18 \times 10^{21}$, the inequality $M(f) \le 2^{70}$ holds for any such function $f$.
18: 
19: \(\square\)
