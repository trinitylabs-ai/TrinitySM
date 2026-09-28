# Problem

In Shoreline Amphitheatre, 2024 Googlers each hold up to five flags of various colors. Any group of three Googlers will always have at least two people holding flags of the same color. Prove that one specific flag color is held by at least 200 Googlers.

# Proof A

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

# Proof B

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
