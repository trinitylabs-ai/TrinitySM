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
