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
