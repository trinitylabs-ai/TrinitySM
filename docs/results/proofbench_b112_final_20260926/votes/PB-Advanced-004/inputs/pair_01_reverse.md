# Problem

For a positive integer $n$, a convex $18n+2$-gon $P$ is divided into $18n$ triangles by drawing $18n-1$ diagonals. Prove that we can choose two of these diagonals such that the three parts of $P$ divided by these two diagonals each contain at least $3n$ and at most $9n$ triangles.

# Proof A

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
