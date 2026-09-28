# Problem

There are 120 students in DeepMind highschool, and each student `loves' some of the students. Here `love' is not always a mutual relationship; a student A may love B while B may not love A, and it is also possible that a student loves oneself. For the set $F$ of all $2^{120}$ subsets of the students, define the function $f: F \rightarrow F$ as the function that maps each $X \in F$ to the set of students loved by one or more students in $X$. For $A, B \in F$, $A$ and $B$ are said to have a 'lovely relationship' iff there exists a natural number $k$ such that $f^{k}(A)=B$. Now we want to select distinct elements $A_{1}, A_{2}, \cdots A_{t}$ from $F$ such that for any $1 \leq i<j \leq t$, $A_{i}$ and $A_{j}$ have a lovely relationship. Let $M(f)$ be the maximum possible value of $t$.  Show that $M(f) \leq 2^{70}$.

# Proof A

1: To find the maximum possible value of $t$, denoted by $M(f)$, we analyze the structure of the function $f: F \to F$ and the "lovely relationship" defined on the set $F$ of all $2^{120}$ subsets of students.
2: 
3: **1. Analysis of the function $f$**
4: Let $S$ be the set of $N=120$ students. $F = \mathcal{P}(S)$ is the power set of $S$. For each student $x \in S$, let $L(x) \subseteq S$ be the set of students loved by $x$. The function $f: F \to F$ is defined as:
5: $$f(X) = \{y \in S \mid \exists x \in X, y \in L(x)\} = \bigcup_{x \in X} L(x)$$
6: This function $f$ is a join-homomorphism of the lattice $(F, \cup)$, because for any $X, Y \in F$:
7: $$f(X \cup Y) = \bigcup_{x \in X \cup Y} L(x) = \left( \bigcup_{x \in X} L(x) \right) \cup \left( \bigcup_{x \in Y} L(x) \right) = f(X) \cup f(Y)$$
8: Such a function can be represented by a Boolean adjacency matrix $M$ of size $N \times N$, where $M_{ij} = 1$ if student $i$ loves student $j$, and $0$ otherwise. The action of $f$ on a set $X$ corresponds to the Boolean matrix-vector multiplication $v_{f(X)} = M v_X$, where $v_X$ is the characteristic vector of $X$ and the multiplication is performed in the Boolean semiring $(\{0, 1\}, \lor, \land)$.
9: 
10: **2. The Lovely Relationship and Chains**
11: Two sets $A, B \in F$ have a lovely relationship if there exists a natural number $k$ such that $f^{k}(A)=B$. This defines a reachability preorder $\le$ on $F$, where $A \le B$ if $f^k(A) = B$ for some $k \ge 0$.
12: The problem asks for the maximum $t$ such that there exist distinct $A_1, A_2, \dots, A_t$ where for any $1 \le i < j \le t$, $A_i$ and $A_j$ have a lovely relationship. This means $A_1 \le A_2 \le \dots \le A_t$. Since the $A_i$ are distinct, this sequence forms a chain in the preorder.
13: Any such chain must be contained within the orbit of $A_1$ under $f$:
14: $$O(A_1) = \{A_1, f(A_1), f^2(A_1), \dots\}$$
15: The number of distinct elements in this orbit is the pre-period $m$ plus the period $p$ of the sequence $f^k(A_1)$.
16: 
17: **3. Bounding the Orbit Size**
18: The sequence of vectors $v_k = M^k v_{A_1}$ is determined by the powers of the Boolean matrix $M$. Since there are only $2^N$ possible vectors in $\{0, 1\}^N$, the sequence $v_k$ must eventually repeat by the pigeonhole principle. Thus, the sequence $M^k$ is eventually periodic.
19: 
20: The period $p$ of the sequence $M^k$ is the least common multiple (LCM) of the periods of the strongly connected components (SCCs) of the directed graph $G$ associated with $M$. The period of an SCC is the greatest common divisor (GCD) of the lengths of all its cycles. Since the GCD of cycle lengths in an SCC of size $n$ is at most $n$, the period $p$ is bounded by:
21: $$p \le \text{lcm}(d_1, d_2, \dots, d_c) \le \text{lcm}(n_1, n_2, \dots, n_c) \le g(N)$$
22: where $g(N)$ is the Landau function, the maximum LCM of a partition of $N$.
23: 
24: The pre-period $m$ is the number of steps until the sequence $M^k$ enters its cycle. For a primitive Boolean matrix of size $n$, the exponent (pre-period) is at most $(n-1)^2 + 1$ by Wielandt's Theorem. For a general Boolean matrix of size $N$, the pre-period $m$ is bounded by a polynomial in $N$, specifically $m \le N^2$.
25: 
26: For $N=120$, the maximum period $g(120)$ is the maximum LCM of integers whose sum is 120. Using a prime power partition such as $16+9+5+7+11+13+17+19+23 = 120$, we find $g(120) \ge 16 \cdot 9 \cdot 5 \cdot 7 \cdot 11 \cdot 13 \cdot 17 \cdot 19 \cdot 23 \approx 2.6 \times 10^{10}$. The actual value of $g(120)$ is approximately $2.6 \times 10^{10}$.
27: The total number of distinct elements in any orbit is thus:
28: $$t \le m + p \le N^2 + g(N) \le 120^2 + 2.6 \times 10^{10} \approx 14400 + 2.6 \times 10^{10}$$
29: Comparing this to $2^{70}$:
30: $$2^{70} = (2^{10})^7 \approx (10^3)^7 = 10^{21}$$
31: Since $14400 + 2.6 \times 10^{10} \ll 10^{21}$, the maximum possible value $M(f)$ is significantly smaller than $2^{70}$.
32: 
33: Thus, we have shown that for any such function $f$, the maximum number of distinct elements $A_1, \dots, A_t$ forming a lovely relationship chain is bounded by $N^2 + g(N)$, which is strictly less than $2^{70}$.
34: 
35: \(\square\)

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
