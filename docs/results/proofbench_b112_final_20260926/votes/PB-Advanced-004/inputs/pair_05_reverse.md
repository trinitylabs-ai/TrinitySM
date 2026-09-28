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

1: To prove that we can choose two diagonals of a convex $18n+2$-gon $P$ divided into $18n$ triangles such that the three resulting parts each contain between $3n$ and $9n$ triangles, we translate the problem into a graph-theoretic context.
2: 
3: ### 1. Dual Graph Representation
4: The triangulation of a convex polygon $P$ can be represented by its dual graph $T$. In $T$, each vertex corresponds to a triangle, and an edge exists between two vertices if the corresponding triangles share a diagonal. Because $P$ is a convex polygon, $T$ is a tree with $V = 18n$ vertices, and each vertex has a degree of at most 3. Removing two edges $e_1, e_2$ in $T$ splits the tree into three components $S_1, S_2, S_3$. The sizes $|S_1|, |S_2|, |S_3|$ correspond to the number of triangles in the three parts of $P$. We must show there exist $e_1, e_2$ such that $3n \le |S_i| \le 9n$ for $i=1, 2, 3$.
5: 
6: ### 2. First Split using the Centroid of $T$
7: Let $v$ be the centroid of $T$. By the property of the centroid, no component of $T \setminus \{v\}$ has more than $V/2 = 9n$ vertices. Let the components of $T \setminus \{v\}$ be $W_1, W_2, \dots, W_k$ with sizes $w_1, w_2, \dots, w_k$, where $k \le 3$. We have $\sum_{i=1}^k w_i = 18n-1$ and $w_i \le 9n$ for all $i$.
8: 
9: Let $w_1$ be the size of the largest component $W_1$. Since there are at most 3 components, the largest must satisfy $w_1 \ge \lceil (18n-1)/3 \rceil = 6n$. Thus, $6n \le w_1 \le 9n$. We choose the first edge $e_1$ to be the edge connecting $v$ to $W_1$. This isolates $S_1 = W_1$, so $|S_1| = w_1 \in [6n, 9n]$.
10: 
11: ### 3. Second Split using the Centroid of the Remaining Tree
12: Let $T' = T \setminus W_1$ be the remaining tree. The number of vertices in $T'$ is $M = 18n - w_1$. Since $6n \le w_1 \le 9n$, we have $9n \le M \le 12n$.
13: 
14: Let $v'$ be the centroid of $T'$. The components $U_1, U_2, \dots, U_m$ of $T' \setminus \{v'\}$ have sizes $u_i \le M/2 \le 6n$. The sum of these sizes is $\sum_{j=1}^m u_j = M-1$. We claim there exists a component $U_j$ such that $u_j \ge 3n$. If all $u_j < 3n$, then because $m \le 3$, we would have:
15: \[ M-1 = \sum_{j=1}^m u_j \le 3(3n-1) = 9n-3 \implies M \le 9n-2. \]
16: However, we know $M \ge 9n$, which is a contradiction. Therefore, there must exist at least one component $U_j$ with $u_j \ge 3n$.
17: 
18: We choose the second edge $e_2$ to be the edge connecting $v'$ to $U_j$. This splits $T'$ into $S_2 = U_j$ and $S_3 = T' \setminus U_j$.
19: 
20: ### 4. Verification of Sizes
21: We now check the sizes of the three components $S_1, S_2, S_3$:
22: 1. $|S_1| = w_1 \in [6n, 9n]$, which is within $[3n, 9n]$.
23: 2. $|S_2| = u_j$. We have $3n \le u_j \le M/2 \le 6n$, which is within $[3n, 9n]$.
24: 3. $|S_3| = M - u_j$.
25:    - The minimum value of $|S_3|$ is $M - M/2 = M/2 \ge 9n/2 = 4.5n \ge 3n$.
26:    - The maximum value of $|S_3|$ is $M - 3n \le 12n - 3n = 9n$.
27:    Thus, $|S_3| \in [4.5n, 9n]$, which is within $[3n, 9n]$.
28: 
29: Since all three parts contain between $3n$ and $9n$ triangles, the proof is complete.
30: \(\square\)
