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
