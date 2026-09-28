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
