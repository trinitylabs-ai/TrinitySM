# Problem

In Shoreline Amphitheatre, 2024 Googlers each hold up to five flags of various colors. Any group of three Googlers will always have at least two people holding flags of the same color. Prove that one specific flag color is held by at least 200 Googlers.

# Proof A

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

# Proof B

1: Let $N = 2024$ be the number of Googlers. For each Googler $i \in \{1, 2, \dots, N\}$, let $C_i$ denote the set of colors of the flags held by Googler $i$. We are given that $|C_i| \le 5$ for all $i$.
2: 
3: We model the problem using a graph $G = (V, E)$, where the vertices $V$ are the Googlers. Two vertices $i$ and $j$ are connected by an edge $(i, j) \in E$ if and only if they share at least one flag color, i.e., $C_i \cap C_j \neq \emptyset$.
4: 
5: The problem states that in any group of three Googlers, at least two must share a flag color. In terms of the graph $G$, this means that for any subset of three vertices $\{i, j, k\} \subseteq V$, there is at least one edge between them. This is equivalent to stating that $G$ contains no independent set of size 3. Therefore, the independence number of the graph is $\alpha(G) \le 2$.
6: 
7: We consider two exhaustive cases for the value of $\alpha(G)$.
8: 
9: Case 1: $\alpha(G) = 1$.
10: If $\alpha(G) = 1$, then no two vertices are non-adjacent. This means $G$ is a complete graph $K_N$, implying that every pair of Googlers shares at least one flag color.
11: If $N > 1$, any Googler $u$ must hold at least one flag (otherwise, $u$ would not share a color with any other Googler $v$, contradicting $\alpha(G)=1$). Let $C_u$ be the set of colors held by Googler $u$. Since every other Googler $v \in V \setminus \{u\}$ shares at least one color with $u$, every set $C_v$ must contain at least one color from $C_u$. Thus, $C_u$ is a hitting set for the collection of all flag sets $\{C_i\}_{i=1}^N$.
12: Let $A_c$ be the set of Googlers holding color $c$. By the union bound:
13: \[ N \le \sum_{c \in C_u} |A_c| \le |C_u| \cdot \max_{c} |A_c| \le 5 \cdot \max_{c} |A_c| \]
14: Substituting $N = 2024$:
15: \[ \max_{c} |A_c| \ge \frac{2024}{5} = 404.8 \]
16: Thus, at least one color is held by at least 405 Googlers.
17: 
18: Case 2: $\alpha(G) = 2$.
19: If $\alpha(G) = 2$, there exists at least one pair of Googlers $u$ and $v$ who share no flag colors, so $C_u \cap C_v = \emptyset$.
20: For any third Googler $x \in V \setminus \{u, v\}$, the set $\{u, v, x\}$ must contain at least one edge. Since $(u, v) \notin E$, it must be that either $(u, x) \in E$ or $(v, x) \in E$. This implies that $C_x \cap C_u \neq \emptyset$ or $C_x \cap C_v \neq \emptyset$, and therefore $C_x \cap (C_u \cup C_v) \neq \emptyset$.
21: 
22: We first address the possibility that some Googlers hold no flags. If $C_u = \emptyset$, then for any $x, y \in V \setminus \{u\}$, the set $\{u, x, y\}$ must have an edge. Since $u$ has no flags, $(u, x) \notin E$ and $(u, y) \notin E$, so we must have $(x, y) \in E$ for all $x, y \in V \setminus \{u\}$. This means $V \setminus \{u\}$ forms a clique of size $N-1 = 2023$. Applying the logic from Case 1 to this clique, we find $\max |A_c| \ge \lceil 2023/5 \rceil = 405$.
23: 
24: If $C_u \neq \emptyset$ and $C_v \neq \emptyset$, let $S = C_u \cup C_v$. As shown above, $S$ is a hitting set for all $C_x$ where $x \in V \setminus \{u, v\}$. Since $C_u \subseteq S$ and $C_v \subseteq S$, and both are non-empty, $S$ is a hitting set for all $N$ Googlers. The size of $S$ is:
25: \[ |S| = |C_u \cup C_v| = |C_u| + |C_v| - |C_u \cap C_v| \le 5 + 5 - 0 = 10 \]
26: Using the union bound:
27: \[ N \le \sum_{c \in S} |A_c| \le |S| \cdot \max_{c} |A_c| \le 10 \cdot \max_{c} |A_c| \]
28: Substituting $N = 2024$:
29: \[ \max_{c} |A_c| \ge \frac{2024}{10} = 202.4 \]
30: Thus, at least one color is held by at least 203 Googlers.
31: 
32: In both possible cases, we have shown that there exists at least one flag color held by at least 203 Googlers. Since $203 \ge 200$, the statement is proved.
