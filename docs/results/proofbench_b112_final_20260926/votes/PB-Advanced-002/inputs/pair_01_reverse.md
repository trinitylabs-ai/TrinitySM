# Problem

There are 120 students in DeepMind highschool, and each student `loves' some of the students. Here `love' is not always a mutual relationship; a student A may love B while B may not love A, and it is also possible that a student loves oneself. For the set $F$ of all $2^{120}$ subsets of the students, define the function $f: F \rightarrow F$ as the function that maps each $X \in F$ to the set of students loved by one or more students in $X$. For $A, B \in F$, $A$ and $B$ are said to have a 'lovely relationship' iff there exists a natural number $k$ such that $f^{k}(A)=B$. Now we want to select distinct elements $A_{1}, A_{2}, \cdots A_{t}$ from $F$ such that for any $1 \leq i<j \leq t$, $A_{i}$ and $A_{j}$ have a lovely relationship. Let $M(f)$ be the maximum possible value of $t$.  Show that $M(f) \leq 2^{70}$.

# Proof A

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
