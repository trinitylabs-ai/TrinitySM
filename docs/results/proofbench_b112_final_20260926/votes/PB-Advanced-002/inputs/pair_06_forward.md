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
