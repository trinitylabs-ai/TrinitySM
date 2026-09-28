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
