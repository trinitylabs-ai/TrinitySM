# Problem

For a positive integer $n$, a convex $18n+2$-gon $P$ is divided into $18n$ triangles by drawing $18n-1$ diagonals. Prove that we can choose two of these diagonals such that the three parts of $P$ divided by these two diagonals each contain at least $3n$ and at most $9n$ triangles.

# Proof A

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

# Proof B

1: To prove that we can choose two diagonals of a convex $(18n+2)$-gon $P$ such that the three resulting parts each contain at least $3n$ and at most $9n$ triangles, we utilize the properties of the dual graph of the polygon's triangulation.
2: 
3: ### 1. The Dual Graph Construction
4: Let the convex $(18n+2)$-gon $P$ be divided into $18n$ triangles by $18n-1$ diagonals. We construct the dual graph $T$ of this triangulation as follows:
5: - Each triangle in $P$ is represented by a node in $T$.
6: - Two nodes are connected by an edge if the corresponding triangles share a common diagonal.
7: 
8: Since $P$ is a convex polygon, the dual graph $T$ is a tree. Because each triangle has exactly three sides, each node in $T$ has a degree of at most 3. The tree $T$ contains $N = 18n$ nodes and $N-1 = 18n-1$ edges. Each edge in $T$ corresponds to a unique diagonal of the polygon $P$. Removing two edges from $T$ splits the tree into three connected components; this corresponds to choosing two diagonals in $P$ that divide the polygon into three parts. The number of triangles in each part is equal to the number of nodes in each corresponding component.
9: 
10: ### 2. Finding the First Diagonal
11: A centroid of a tree is a node $v$ such that every connected component of $T \setminus \{v\}$ has at most $N/2$ nodes. For $N=18n$, let $v$ be a centroid of $T$. The removal of $v$ splits $T$ into at most three components $T_1, T_2, T_3$ with sizes $s_1, s_2, s_3$. We have:
12: $$s_1 + s_2 + s_3 = N-1 = 18n-1, \quad \text{and} \quad 0 \le s_i \le 9n \text{ for } i=1, 2, 3.$$
13: We claim that at least one $s_i$ must satisfy $6n \le s_i \le 9n$. If $s_i < 6n$ for all $i$, then $s_1 + s_2 + s_3 \le (6n-1) + (6n-1) + (6n-1) = 18n-3$, which contradicts $s_1 + s_2 + s_3 = 18n-1$. Thus, there exists an index $i$ such that $6n \le s_i \le 9n$.
14: Let $e_1$ be the edge in $T$ connecting $v$ to the subtree $T_i$. Removing $e_1$ splits $T$ into two components: $T_A$ of size $k_1 = s_i \in [6n, 9n]$ and $T_B$ of size $M = 18n - s_i \in [9n, 12n]$.
15: 
16: ### 3. Finding the Second Diagonal
17: We now seek an edge $e_2$ within the subtree $T_B$ to split it into two components $T_j$ and $T_k$ of sizes $k_2$ and $k_3$. We require $k_2, k_3 \in [3n, 9n]$. Since $k_2 + k_3 = M \le 12n$, if both $k_2, k_3 \ge 3n$, then $k_2 = M - k_3 \le 12n - 3n = 9n$ and $k_3 = M - k_2 \le 12n - 3n = 9n$. Thus, it suffices to find $e_2$ such that $k_2, k_3 \ge 3n$.
18: 
19: Let $v_M$ be the centroid of $T_B$. The components of $T_B \setminus \{v_M\}$ have sizes $s'_1, s'_2, s'_3$ such that $s'_1 + s'_2 + s'_3 = M-1$ and $s'_j \le M/2$. By the same logic used for $T$, at least one $s'_j$ must satisfy:
20: $$s'_j \ge \left\lceil \frac{M-1}{3} \right\rceil$$
21: Given $M \ge 9n$, we have $s'_j \ge \lceil (9n-1)/3 \rceil = 3n$. Let $e_2$ be the edge connecting $v_M$ to the subtree of size $s'_j$. The two components of $T_B \setminus \{e_2\}$ have sizes:
22: - $k_2 = s'_j \ge 3n$. Since $s'_j \le M/2 \le 12n/2$, we have $k_2 \le 6n$.
23: - $k_3 = M - s'_j \ge M - M/2 = M/2 \ge 9n/2 = 4.5n$. Since $s'_j \ge 3n$, we have $k_3 \le 12n - 3n = 9n$.
24: 
25: ### 4. Final Verification
26: The two edges $e_1$ and $e_2$ divide the tree $T$ into three components with sizes:
27: 1. $k_1 \in [6n, 9n]$
28: 2. $k_2 \in [3n, 6n]$
29: 3. $k_3 \in [4.5n, 9n]$
30: All three sizes are within the range $[3n, 9n]$. Since each edge in $T$ corresponds to a diagonal in $P$, choosing the diagonals corresponding to $e_1$ and $e_2$ divides $P$ into three parts each containing between $3n$ and $9n$ triangles.
31: 
32: \(\square\)
