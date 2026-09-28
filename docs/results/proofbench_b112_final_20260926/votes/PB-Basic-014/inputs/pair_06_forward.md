# Problem

In Shoreline Amphitheatre, 2024 Googlers each hold up to five flags of various colors. Any group of three Googlers will always have at least two people holding flags of the same color. Prove that one specific flag color is held by at least 200 Googlers.

# Proof A

1: To prove that one specific flag color is held by at least 200 Googlers, we model the problem using the language of hypergraphs.
2: 
3: ### 1. Formalization
4: Let $N = 2024$ be the number of Googlers. For each Googler $i \in \{1, 2, \dots, N\}$, let $S_i$ be the set of colors of the flags that Googler $i$ holds. Based on the problem statement:
5: - Each Googler holds up to five flags, so $|S_i| \le 5$ for all $i$.
6: - Any group of three Googlers contains at least two people who share a flag color. This means that for any three indices $i, j, k \in \{1, \dots, N\}$, at least one of the intersections $S_i \cap S_j$, $S_i \cap S_k$, or $S_j \cap S_k$ is non-empty.
7: 
8: In hypergraph theory, a matching is a collection of pairwise disjoint sets. The matching number $\nu(\mathcal{F})$ of a family $\mathcal{F} = \{S_1, \dots, S_N\}$ is the size of the largest matching. The condition that no three sets in $\mathcal{F}$ are pairwise disjoint implies that the matching number $\nu(\mathcal{F})$ is at most 2.
9: 
10: ### 2. The Hitting Set Bound
11: A hitting set (or transversal) of a family $\mathcal{F}$ is a set of elements $T$ such that $T \cap S_i \neq \emptyset$ for every $S_i \in \mathcal{F}$. The minimum size of a hitting set is denoted by $\tau(\mathcal{F})$.
12: 
13: We utilize the following theorem: For any family $\mathcal{F}$ of non-empty sets where the maximum size of any set is $k$, the hitting set size $\tau(\mathcal{F})$ is bounded by $k \cdot \nu(\mathcal{F})$.
14: 
15: **Proof:** Let $\mathcal{M} = \{M_1, M_2, \dots, M_\nu\}$ be a maximum matching in $\mathcal{F}$, where $\nu = \nu(\mathcal{F})$. Let $T$ be the union of all sets in this matching:
16: \[ T = \bigcup_{j=1}^\nu M_j \]
17: The size of $T$ is $|T| \le \sum_{j=1}^\nu |M_j| \le \nu \cdot k$. We claim that $T$ is a hitting set. If there existed a set $S \in \mathcal{F}$ such that $S \cap T = \emptyset$, then $S$ would be disjoint from every set $M_j$ in the matching $\mathcal{M}$. This would imply that $\mathcal{M} \cup \{S\}$ is a matching of size $\nu + 1$, contradicting the maximality of $\mathcal{M}$. Thus, $T \cap S \neq \emptyset$ for all $S \in \mathcal{F}$, confirming that $T$ is a hitting set of size at most $k\nu$. $\square$
18: 
19: ### 3. Analysis of Googlers with Flags
20: If a Googler holds no flags ($S_i = \emptyset$), they cannot share a color with anyone. If two Googlers $i$ and $j$ both hold no flags, then for any third Googler $k$, the group $\{i, j, k\}$ would have no two people sharing a color (since $S_i \cap S_j = \emptyset$, $S_i \cap S_k = \emptyset$, and $S_j \cap S_k = \emptyset$), violating the problem condition. Thus, at most one Googler can hold no flags.
21: 
22: **Case 1: All Googlers hold at least one flag.**
23: In this case, the family $\mathcal{F}$ consists of non-empty sets. With $k = 5$ and $\nu(\mathcal{F}) \le 2$, the theorem implies:
24: \[ \tau(\mathcal{F}) \le 5 \cdot 2 = 10 \]
25: There exists a set of colors $T = \{c_1, c_2, \dots, c_m\}$ with $m \le 10$ such that every Googler holds at least one color from $T$. Let $x_j$ be the number of Googlers who hold a flag of color $c_j$ for $j = 1, \dots, m$. Then:
26: \[ \sum_{j=1}^m x_j \ge N = 2024 \]
27: By the Pigeonhole Principle, there exists at least one color $c_j \in T$ such that:
28: \[ x_j \ge \frac{2024}{m} \ge \frac{2024}{10} = 202.4 \]
29: Since $x_j$ must be an integer, $x_j \ge 203$.
30: 
31: **Case 2: Exactly one Googler holds no flags.**
32: Let Googler 1 be the one with $S_1 = \emptyset$. For any two other Googlers $j, k \in \{2, \dots, N\}$, the group $\{1, j, k\}$ must contain at least two people sharing a color. Since $S_1 \cap S_j = \emptyset$ and $S_1 \cap S_k = \emptyset$, it must be that $S_j \cap S_k \neq \emptyset$.
33: Thus, any two Googlers in the remaining group of $N-1 = 2023$ share a color, meaning the matching number of the subfamily $\mathcal{F}' = \{S_2, \dots, S_N\}$ is $\nu(\mathcal{F}') = 1$. Applying the theorem to $\mathcal{F}'$:
34: \[ \tau(\mathcal{F}') \le 5 \cdot 1 = 5 \]
35: There exists a set of colors $T$ with $|T| \le 5$ such that every Googler in $\mathcal{F}'$ holds at least one color from $T$. Let $x_j$ be the number of Googlers who hold color $c_j \in T$. Then:
36: \[ \sum_{j=1}^m x_j \ge 2023 \]
37: By the Pigeonhole Principle, there exists at least one color $c_j \in T$ such that:
38: \[ x_j \ge \frac{2023}{5} = 404.6 \implies x_j \ge 405 \]
39: 
40: In both cases, there exists a specific flag color held by at least 203 Googlers, which is $\ge 200$.

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
