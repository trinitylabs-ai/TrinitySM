# Problem

In Shoreline Amphitheatre, 2024 Googlers each hold up to five flags of various colors. Any group of three Googlers will always have at least two people holding flags of the same color. Prove that one specific flag color is held by at least 200 Googlers.

# Proof A

1: To prove that one specific flag color is held by at least 200 Googlers, we model the problem using the properties of intersection graphs and intersecting families of sets.
2: 
3: **1. Mathematical Formulation**
4: Let $V = \{1, 2, \dots, N\}$ be the set of $N = 2024$ Googlers. For each Googler $i \in V$, let $S_i$ be the set of colors of the flags they hold. We are given that $|S_i| \le 5$ for all $i$.
5: Let $C$ be the set of all flag colors used. For any color $c \in C$, let $C_c = \{i \in V : c \in S_i\}$ be the set of Googlers who hold a flag of color $c$. We wish to prove that there exists some $c \in C$ such that $|C_c| \ge 200$.
6: Let $M = \max_{c \in C} |C_c|$ be the maximum number of Googlers holding any single color.
7: 
8: **2. The Intersection Graph**
9: Consider the intersection graph $G = (V, E)$, where an edge $(i, j) \in E$ exists if and only if $S_i \cap S_j \neq \emptyset$. The problem states that any group of three Googlers will always have at least two people holding flags of the same color. In terms of the graph $G$, this means that for any three vertices $i, j, k \in V$, at least one pair among them must be connected by an edge. This is equivalent to saying that the independence number $\alpha(G)$ (the size of the largest set of vertices with no edges between them) is at most 2.
10: 
11: **3. Analysis of Neighborhoods**
12: Pick an arbitrary Googler $v \in V$. Let $N(v) = \{u \in V : (u, v) \in E\}$ be the set of neighbors of $v$, and let $K_v = V \setminus (N(v) \cup \{v\})$ be the set of non-neighbors of $v$.
13: If $u, w \in K_v$, then by definition, $(u, v) \notin E$ and $(w, v) \notin E$. Because $\alpha(G) \le 2$, the triple $\{v, u, w\}$ cannot be an independent set. Therefore, the pair $\{u, w\}$ must be connected by an edge, meaning $S_u \cap S_w \neq \emptyset$. Since this holds for all pairs in $K_v$, the set $K_v$ is a clique in $G$.
14: 
15: **4. Bounding the Maximum Color Size**
16: The neighborhood $N(v)$ is the set of all Googlers who share at least one color with $v$. Thus, $N(v) = \bigcup_{c \in S_v} (C_c \setminus \{v\})$. The size of this union is bounded by:
17: \[ |N(v)| \le \sum_{c \in S_v} (|C_c| - 1) \le |S_v|(M - 1) \le 5(M - 1) \]
18: The size of the clique $K_v$ is then:
19: \[ |K_v| = N - 1 - |N(v)| \ge 2024 - 1 - 5(M - 1) = 2023 - 5M + 5 = 2028 - 5M \]
20: 
21: **5. Applying the Intersecting Family Lemma**
22: A known result in extremal set theory states that if $\mathcal{F}$ is an intersecting family of sets (meaning any two sets in $\mathcal{F}$ have a non-empty intersection) and each set in $\mathcal{F}$ has size at most $k$, then there exists an element $c$ contained in at least $|\mathcal{F}|/k$ sets.
23: Proof: Pick any set $S_0 \in \mathcal{F}$. Since every $S \in \mathcal{F}$ intersects $S_0$, we have $\mathcal{F} = \bigcup_{c \in S_0} \{S \in \mathcal{F} : c \in S\}$. By the pigeonhole principle, at least one of these sets must have size $\ge |\mathcal{F}|/|S_0| \ge |\mathcal{F}|/k$.
24: 
25: Applying this to the clique $K_v$ (where $k=5$), there exists a color $c^*$ such that:
26: \[ |C_{c^*} \cap K_v| \ge \frac{|K_v|}{5} \]
27: Since $|C_{c^*}| \ge |C_{c^*} \cap K_v|$ and $M$ is the maximum size of any color set, we have:
28: \[ M \ge \frac{|K_v|}{5} \ge \frac{2028 - 5M}{5} \]
29: Multiplying by 5 gives:
30: \[ 5M \ge 2028 - 5M \implies 10M \ge 2028 \implies M \ge 202.8 \]
31: Since $M$ must be an integer, $M \ge 203$. Thus, there is a flag color held by at least 203 Googlers, which satisfies the requirement of being at least 200.
32: 
33: \(\square\)

# Proof B

1: To prove that one specific flag color is held by at least 200 Googlers, we model the problem using graph theory.
2: 
3: **1. Graph Construction**
4: Let the $n = 2024$ Googlers be represented as vertices $V = \{1, 2, \dots, n\}$ of a graph $G$. For each Googler $i$, let $S_i$ denote the set of colors of the flags they hold. We are given that $|S_i| \le 5$ for all $i \in V$. We define an edge between two vertices $i$ and $j$ if and only if they share at least one flag color, i.e., $S_i \cap S_j \neq \emptyset$.
5: 
6: The problem states that any group of three Googlers will always have at least two people holding flags of the same color. In terms of our graph $G$, this means that among any three vertices, there must be at least one edge. This is equivalent to saying that the graph $G$ contains no independent set of size 3. Therefore, the independence number of the graph is $\alpha(G) \le 2$.
7: 
8: **2. Analysis of the Independence Number**
9: Consider an arbitrary vertex $v \in V$. Let $N(v)$ be the set of neighbors of $v$ (those who share a color with $v$) and let $M(v)$ be the set of non-neighbors of $v$ (those who share no color with $v$).
10: We claim that $M(v)$ must be a clique. Suppose there exist two vertices $u, w \in M(v)$ such that $(u, w)$ is not an edge. Then the set $\{v, u, w\}$ forms an independent set of size 3, because $(v, u) \notin E$, $(v, w) \notin E$, and $(u, w) \notin E$. This contradicts the fact that $\alpha(G) \le 2$. Thus, every pair of vertices in $M(v)$ must be connected by an edge.
11: 
12: **3. Intersecting Families and the Pigeonhole Principle**
13: Since $M(v)$ is a clique, any two Googlers $u, w \in M(v)$ share at least one flag color. This means the collection of sets $\mathcal{F} = \{S_u : u \in M(v)\}$ is an intersecting family of sets, where each set has a cardinality of at most 5.
14: 
15: Let $\omega$ be the maximum number of Googlers holding any one specific color, $\omega = \max_c |X_c|$, where $X_c$ is the set of all Googlers who hold color $c$.
16: If $M(v)$ is empty, then $|M(v)| = 0 \le 5\omega$.
17: If $M(v)$ is not empty, pick any $u_0 \in M(v)$.
18: - If $S_{u_0} = \emptyset$, then for $M(v)$ to be a clique, $M(v)$ can only contain $u_0$ (since no other set $S_w$ can intersect the empty set). Thus $|M(v)| = 1$. Since $n=2024$ and $\alpha(G) \le 2$, at least one person must hold a flag, so $\omega \ge 1$, and $|M(v)| \le 5\omega$ holds.
19: - If $S_{u_0} \neq \emptyset$, every other $S_w$ for $w \in M(v)$ must intersect $S_{u_0}$. We can write:
20: $$M(v) = \bigcup_{c \in S_{u_0}} \{ w \in M(v) : c \in S_w \}$$
21: Since $|S_{u_0}| \le 5$, by the Pigeonhole Principle, there must be at least one color $c \in S_{u_0}$ such that:
22: $$|\{ w \in M(v) : c \in S_w \}| \ge \frac{|M(v)|}{|S_{u_0}|} \ge \frac{|M(v)|}{5}$$
23: Since $\{ w \in M(v) : c \in S_w \} \subseteq X_c$, we have $|X_c| \ge \frac{|M(v)|}{5}$, which implies $\omega \ge \frac{|M(v)|}{5}$, or $|M(v)| \le 5\omega$.
24: 
25: **4. Final Bound**
26: Now we bound the number of neighbors $|N(v)|$. A Googler $j$ is a neighbor of $v$ if they share at least one color $c \in S_v$. Thus:
27: $$N(v) = \bigcup_{c \in S_v} (X_c \setminus \{v\})$$
28: Using the union bound and the fact that $|S_v| \le 5$:
29: $$|N(v)| \le \sum_{c \in S_v} (|X_c| - 1) \le 5(\omega - 1)$$
30: The total number of Googlers is the sum of $v$, its neighbors, and its non-neighbors:
31: $$n = 1 + |N(v)| + |M(v)| \le 1 + 5(\omega - 1) + 5\omega = 10\omega - 4$$
32: Substituting $n = 2024$:
33: $$2024 \le 10\omega - 4 \implies 10\omega \ge 2028 \implies \omega \ge 202.8$$
34: Since $\omega$ must be an integer, we have $\omega \ge 203$.
35: 
36: Thus, there exists at least one flag color held by at least 203 Googlers, which satisfies the requirement of at least 200.
