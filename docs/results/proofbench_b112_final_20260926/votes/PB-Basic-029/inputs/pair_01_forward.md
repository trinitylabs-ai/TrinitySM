# Problem

Let $p$ and $n$ be integers with $0\le p\le n-2$. Consider a set
 $S$ of $n$ lines in the plane such that no two of them are parallel
 and no three have a common point. Denote by $I$ the set of intersections
 of lines in $S$. Let $O$ be a point in the plane not lying on any
 line of $S$. A point $X\in I$ is colored red if the open line segment
 $OX$ intersects at most $p$ lines in $S$. What is the minimum number
 of red points that is contained in $I$?

# Proof A

1: Let the $n$ lines in $S$ be $L_1, L_2, \dots, L_n$. Since no two lines are parallel and no three are concurrent, there are exactly $|I| = \binom{n}{2}$ intersection points. Let $O$ be a point in the plane not lying on any line of $S$. A point $X \in I$ is colored red if the open line segment $OX$ intersects at most $p$ lines in $S$.
2: 
3: We apply a projective transformation that maps the point $O$ to the point at infinity in the $y$-direction. Under this transformation, lines remain lines, and the open line segment $OX$ becomes a vertical ray starting at $X$ and extending upwards. Thus, a point $X \in I$ is red if and only if there are at most $p$ lines of $S$ lying strictly above $X$. In the theory of line arrangements, the set of points with at most $p$ lines above them is known as the $(\le p)$-level of the arrangement. The red points are exactly the vertices of this $(\le p)$-level.
4: 
5: To find the minimum number of red points, we use a duality mapping where each line $L_i: y = a_i x + b_i$ corresponds to a point $P_i: (a_i, b_i)$. An intersection point $X_{ij}$ of lines $L_i$ and $L_j$ corresponds to the edge $e_{ij}$ connecting $P_i$ and $P_j$ in the dual plane. The number of lines of $S$ lying strictly above $X_{ij}$ is equal to the number of points $P_k$ lying in the open half-plane $H^+(e_{ij})$ defined by the line $P_i P_j$ (specifically, the half-plane containing points $(a, b)$ such that the line $y = ax+b$ is above $X_{ij}$).
6: 
7: A point $X \in I$ is red if and only if its dual edge $e = \{P_i, P_j\}$ has $|H^+(e)| \le p$. Let $f(n, p)$ be the minimum number of such red edges for any set of $n$ points in general position. We prove by induction on $n$ that $f(n, p) \ge \binom{p+2}{2}$ for $n \ge p+2$.
8: 
9: Base Case: For $n = p+2$, any pair of points $\{P_i, P_j\}$ defines a line with at most $n-2 = p$ points in either open half-plane. Thus, all $\binom{n}{2} = \binom{p+2}{2}$ edges are red.
10: 
11: Inductive Step: Assume $f(n, p) \ge \binom{p+2}{2}$. Consider a set $\mathcal{P}_{n+1}$ of $n+1$ points. Let $P$ be a vertex of the convex hull of $\mathcal{P}_{n+1}$, and let $\mathcal{P}_n = \mathcal{P}_{n+1} \setminus \{P\}$.
12: 1. New Edges: Consider edges of the form $\{P, P_i\}$ for $P_i \in \mathcal{P}_n$. Sorting $P_i$ by angle around $P$, the number of points in $H^+(\{P, P_i\})$ takes all values from $0$ to $n-1$. Exactly $p+1$ of these edges have $\le p$ points in $H^+$.
13: 2. Existing Edges: An edge $e \in \mathcal{P}_n$ is red in $\mathcal{P}_{n+1}$ if $|H^+_{\mathcal{P}_{n+1}}(e)| \le p$. If $e$ was red in $\mathcal{P}_n$, it remains red in $\mathcal{P}_{n+1}$ unless $|H^+_{\mathcal{P}_n}(e)| = p$ and $P \in H^+(e)$. If $e$ was not red in $\mathcal{P}_n$, it cannot become red.
14: 3. Loss Calculation: The number of red edges in $\mathcal{P}_{n+1}$ is $|Red(\mathcal{P}_{n+1})| \ge |Red(\mathcal{P}_n)| + (p+1) - |\{e \in E_p(\mathcal{P}_n) : P \in H^+(e)\}|$, where $E_p(\mathcal{P}_n)$ is the set of edges with exactly $p$ points in $H^+$.
15: The edges $E_p(\mathcal{P}_n)$ form the $p$-level of the arrangement, which is a x-monotone polygonal chain. A point $P$ outside the convex hull of $\mathcal{P}_n$ can lie in the $H^+$ half-plane of at most $p+1$ edges of this chain. Thus, $|Red(\mathcal{P}_{n+1})| \ge \binom{p+2}{2} + (p+1) - (p+1) = \binom{p+2}{2}$.
16: 
17: To show the bound is tight, consider the lines $L_i: y = ix + i^2$ for $i=1, \dots, n$. The intersection $X_{ij}$ of $L_i$ and $L_j$ (for $i < j$) is $x = -(i+j), y = -ij$. A line $L_k$ is above $X_{ij}$ if $k(-(i+j)) + k^2 > -ij \iff (k-i)(k-j) > 0$, which holds if $k < i$ or $k > j$. The number of such $k \in \{1, \dots, n\} \setminus \{i, j\}$ is $(i-1) + (n-j)$.
18: $X_{ij}$ is red if $i-1 + n-j \le p \iff j-i \ge n-p-1$.
19: Let $m = n-p-1$. The number of pairs $(i, j)$ with $1 \le i < j \le n$ and $j-i \ge m$ is:
20: $\sum_{i=1}^{n-m} (n - (i+m) + 1) = \sum_{k=1}^{n-m} k = \frac{(n-m)(n-m+1)}{2} = \frac{(p+1)(p+2)}{2} = \binom{p+2}{2}$.
21: 
22: The minimum number of red points is $\binom{p+2}{2}$.

# Proof B

1: Let $S = \{L_1, \dots, L_n\}$ be a set of $n$ lines in the plane such that no two are parallel and no three are concurrent. Let $I$ be the set of $\binom{n}{2}$ intersection points. For a point $O$ not on any line of $S$, a point $X \in I$ is colored red if the open line segment $OX$ intersects at most $p$ lines in $S$. Let $d(X, O)$ denote the number of lines in $S$ that separate $X$ from $O$. A point $X$ is red if $d(X, O) \le p$.
2: 
3: First, we establish a lower bound on the number of red points. We use the concept of levels in a line arrangement. By applying a projective transformation, we can map the point $O$ to a point at infinity in the direction of the negative $y$-axis. Under this transformation, lines remain lines, and the property that a line $L$ separates $X$ from $O$ is equivalent to the property that $L$ passes below the point $X$ (i.e., the $y$-coordinate of $L$ at the $x$-coordinate of $X$ is less than the $y$-coordinate of $X$).
4: 
5: In this transformed plane, $d(X, O)$ is the number of lines lying strictly below $X$. The set of red points is the union of the vertices of levels $0, 1, \dots, p$. A vertex $X$ is of level $k$ if exactly $k$ lines lie strictly below it. Let $v_k$ be the number of vertices of level $k$. It is a known result in the theory of line arrangements that for $n$ lines in general position, the number of vertices of level $k$ is at least $k+1$ for $0 \le k < n/2$. Consequently, the total number of red points is:
6: $$N_p = \sum_{k=0}^p v_k \ge \sum_{k=0}^p (k+1) = \frac{(p+1)(p+2)}{2} = \binom{p+2}{2}$$
7: This holds for $p \le n-2$, as the condition $k < n/2$ is satisfied for $k \le p$ when $p$ is small relative to $n$. Even if $p \ge n/2$, the total number of vertices in the arrangement is $\binom{n}{2}$, and for $p=n-2$, all $\binom{n}{2}$ points are red, which is $\ge \binom{p+2}{2} = \binom{n}{2}$.
8: 
9: To show that $\binom{p+2}{2}$ is achievable for any $n \ge p+2$, we construct a specific configuration. Let $S_0 = \{L_1, \dots, L_{p+2}\}$ be a set of $p+2$ lines tangent to a circle $\mathcal{C}$ at points $T_1, \dots, T_{p+2}$ ordered counter-clockwise along a small arc of the circle. Let $O$ be the center of $\mathcal{C}$. For any two lines $L_i, L_j \in S_0$ with $i < j$, their intersection point $X_{ij}$ is outside the circle. A line $L_k \in S_0$ separates $O$ from $X_{ij}$ if and only if the tangency point $T_k$ lies on the minor arc $T_i T_j$. Thus, the number of lines in $S_0$ separating $O$ from $X_{ij}$ is $d_{S_0}(X_{ij}, O) = j - i - 1$. The maximum value is $(p+2) - 1 - 1 = p$. Hence, all $\binom{p+2}{2}$ intersection points of $S_0$ are red.
10: 
11: Now we add the remaining $n - (p+2)$ lines $S_{rest} = \{L_{p+3}, \dots, L_n\}$. We place these lines very far from $O$ and the intersections $X_{ij}$ such that they are nearly parallel to each other and have very large slopes. Specifically, we place them such that for any $L_k \in S_{rest}$ and any $L_i \in S_0$, the intersection $X_{ik} = L_i \cap L_k$ is positioned such that the segment $OX_{ik}$ crosses at least $p+1$ lines of $S_0$. This can be achieved by placing $L_k$ such that $X_{ik}$ lies "beyond" the fan of lines $S_0$. Similarly, for any two lines $L_k, L_m \in S_{rest}$, their intersection $X_{km}$ is placed such that $OX_{km}$ crosses all $p+2$ lines of $S_0$, ensuring $d(X_{km}, O) \ge p+2 > p$.
12: 
13: Under this construction, the only red points are the $\binom{p+2}{2}$ intersections of the lines in $S_0$. Thus, the minimum number of red points is $\binom{p+2}{2}$.
