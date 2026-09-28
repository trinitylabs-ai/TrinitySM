# Problem

For a positive integer $n$, a convex $18n+2$-gon $P$ is divided into $18n$ triangles by drawing $18n-1$ diagonals. Prove that we can choose two of these diagonals such that the three parts of $P$ divided by these two diagonals each contain at least $3n$ and at most $9n$ triangles.

# Proof A

1: To prove that we can choose two diagonals such that the three parts of the convex $18n+2$-gon $P$ each contain between $3n$ and $9n$ triangles, we represent the triangulation of $P$ using its dual graph.
2: 
3: **1. Dual Graph Representation**
4: A convex polygon $P$ with $V = 18n+2$ vertices divided into $T = 18n$ triangles by $D = 18n-1$ diagonals has a dual graph $G$ where each node represents a triangle and an edge connects two nodes if the corresponding triangles share a common diagonal. Because the polygon is convex and the division is a triangulation, $G$ is a tree. Furthermore, since each triangle has exactly three sides, each node in $G$ has a degree of at most 3.
5: Choosing a diagonal in $P$ corresponds to removing an edge in $G$. Removing two edges in $G$ splits the tree into three disjoint components. The number of nodes in these components corresponds to the number of triangles in the three resulting parts of $P$. We denote these sizes as $t_1, t_2,$ and $t_3$. We must show there exist two edges such that $3n \le t_i \le 9n$ for $i=1, 2, 3$.
6: 
7: **2. Selection of the First Diagonal**
8: Let $N = 18n$ be the number of nodes in $G$. A centroid $v$ of a tree is a node such that the removal of $v$ splits the tree into components each of size at most $N/2$. Let the components formed by removing $v$ be $C_1, C_2, \dots, C_k$. Since the maximum degree of $v$ is 3, $k \le 3$. Let $s_i$ be the number of nodes in $C_i$. We have:
9: $$\sum_{i=1}^k s_i = N - 1 = 18n - 1, \quad \text{and} \quad s_i \le \frac{N}{2} = 9n \text{ for all } i.$$
10: By the Pigeonhole Principle, at least one component (say $C_1$) must satisfy:
11: $$s_1 \ge \left\lceil \frac{18n-1}{3} \right\rceil = 6n.$$
12: We choose the first diagonal $d_1$ corresponding to the edge connecting $v$ to $C_1$. This splits $G$ into two components: $C_1$ with $t_1 = s_1$ nodes, and a remaining tree $T'$ with $S = 18n - s_1$ nodes. Since $6n \le s_1 \le 9n$, we have $t_1 \in [6n, 9n]$ and $S \in [9n, 12n]$.
13: 
14: **3. Selection of the Second Diagonal**
15: We now seek an edge in $T'$ that splits $T'$ into two components of size $t_2$ and $t_3$ such that $3n \le t_2, t_3 \le 9n$. This is equivalent to finding an edge that cuts off a component of size $t_2$ such that $t_2 \in [3n, S-3n]$.
16: Let $v'$ be the centroid of $T'$. Removing $v'$ splits $T'$ into components $C'_1, \dots, C'_m$ with $m \le 3$ and sizes $s'_j \le S/2$. We have:
17: $$\sum_{j=1}^m s'_j = S - 1.$$
18: By the Pigeonhole Principle, at least one component (say $C'_1$) must satisfy:
19: $$s'_1 \ge \left\lceil \frac{S-1}{3} \right\rceil \ge \left\lceil \frac{9n-1}{3} \right\rceil = 3n.$$
20: We now verify the bounds for $t_2 = s'_1$ and $t_3 = S - s'_1$:
21: - **Lower bounds:** $t_2 \ge 3n$ is proven above. Since $s'_1 \le S/2$, then $t_3 = S - s'_1 \ge S/2$. Since $S \ge 9n$, $t_3 \ge 4.5n \ge 3n$.
22: - **Upper bounds:** Since $s'_1 \le S/2$ and $S \le 12n$, $t_2 \le 6n \le 9n$. For $t_3$, we have $t_3 = S - s'_1$. Since $s'_1 \ge 3n$, $t_3 \le S - 3n$. Given $S \le 12n$, $t_3 \le 12n - 3n = 9n$.
23: 
24: All three parts $t_1, t_2, t_3$ satisfy $3n \le t_i \le 9n$. Thus, the two chosen diagonals divide the polygon into three parts each containing between $3n$ and $9n$ triangles.
25: 
26: \(\square\)

# Proof B

1: Let the $18n$ triangles of the triangulation be the vertices of a dual graph $G$. Two vertices are connected by an edge if the corresponding triangles share a diagonal. Since the triangulation is of a convex polygon, $G$ is a tree with $N = 18n$ vertices and a maximum degree of 3. Removing two edges (diagonals) from $G$ splits the tree into three components of sizes $T_1, T_2, T_3$. We must show there exist two edges such that $3n \le |T_i| \le 9n$ for $i=1, 2, 3$.
2: 
3: Let $v$ be a centroid of $G$. By the properties of a centroid, every component of $G - v$ has size at most $N/2 = 9n$. Let the components be $C_1, C_2, C_3$ with sizes $s_1 \le s_2 \le s_3 \le 9n$. Since $v$ is a vertex, the sum of the sizes of the components is $s_1 + s_2 + s_3 = 18n - 1$ (where some $s_i$ may be 0 if the degree of $v$ is less than 3).
4: 
5: Case 1: $s_1 \ge 3n$.
6: If $s_3 \le 9n - 1$, we remove the edges incident to $v$ that lead to $C_1$ and $C_2$. The resulting components are $C_1$, $C_2$, and $C_3 \cup \{v\}$. Their sizes are $s_1, s_2, s_3 + 1$. Since $s_1 \ge 3n$, $s_2 \ge 3n$, and $s_3 + 1 \le 9n$, all three components satisfy the condition.
7: If $s_3 = 9n$, we remove the edges incident to $v$ that lead to $C_1$ and $C_3$. The resulting components are $C_1$, $C_3$, and $C_2 \cup \{v\}$. Their sizes are $s_1, 9n, s_2 + 1$. We have $s_1 \ge 3n$ and $s_2 + 1 \ge s_1 + 1 \ge 3n + 1$. Also, $s_2 + 1 = (18n - 1 - 9n - s_1) + 1 = 9n - s_1 \le 9n - 3n = 6n$. Thus, all three components are in the range $[3n, 9n]$.
8: 
9: Case 2: $s_1 < 3n$.
10: Since $s_1 \le 3n - 1$ and $s_1 + s_2 + s_3 = 18n - 1$, we have $s_2 + s_3 \ge 15n$. Given $s_3 \ge s_2$, it follows that $2s_3 \ge 15n$, so $s_3 \ge 7.5n$, which implies $s_3 \ge 8n$ for any positive integer $n$. We also know $s_3 \le 9n$.
11: We choose the first diagonal to be the edge $e_1$ incident to $v$ that leads to $C_3$. This splits $G$ into $T_1 = C_3$ and $T' = G \setminus C_3$. The size of $T_1$ is $s_3 \in [8n, 9n]$, which is within $[3n, 9n]$.
12: The remaining part $T'$ is a tree of size $M = 18n - s_3$. Since $s_3 \in [8n, 9n]$, we have $M \in [9n, 10n]$.
13: We now seek a second diagonal $e_2$ in $T'$ that splits $T'$ into $T_2$ and $T_3$ such that $3n \le |T_2| \le 9n$ and $3n \le |T_3| \le 9n$. This is equivalent to finding $e_2$ such that $|T_2| \in [M - 9n, 9n]$.
14: Let $v'$ be a centroid of $T'$. The components of $T' - v'$ each have size at most $M/2 \le 10n/2 = 5n$. Let $S'_{max}$ be the largest component of $T' - v'$. The sum of the sizes of the components is $M - 1$. Since the maximum degree of $v'$ is 3, we have $S'_{max} \ge (M - 1)/3 \ge (9n - 1)/3 = 3n - 1/3$, so $S'_{max} \ge 3n$.
15: Thus, $S'_{max} \in [3n, 5n]$. We choose $e_2$ to be the edge incident to $v'$ that leads to $S'_{max}$.
16: Then $|T_2| = S'_{max} \in [3n, 5n] \subseteq [3n, 9n]$.
17: The size of the third component is $|T_3| = M - S'_{max}$. Since $S'_{max} \le 5n$ and $M \ge 9n$, we have $|T_3| \ge 9n - 5n = 4n \ge 3n$. Since $S'_{max} \ge 3n$ and $M \le 10n$, we have $|T_3| \le 10n - 3n = 7n \le 9n$.
18: Thus, $|T_2|$ and $|T_3|$ both lie in $[3n, 9n]$.
19: 
20: In all cases, we have found two diagonals that divide $P$ into three parts each containing between $3n$ and $9n$ triangles.
