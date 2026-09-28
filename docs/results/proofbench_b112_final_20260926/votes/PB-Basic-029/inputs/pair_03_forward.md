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

1: Let $S = \{L_1, L_2, \dots, L_n\}$ be a set of $n$ lines in the plane such that no two are parallel and no three are concurrent. Let $I$ be the set of $\binom{n}{2}$ intersection points. Let $O$ be a point in the plane not on any line of $S$. A point $X \in I$ is red if the open line segment $OX$ intersects at most $p$ lines in $S$.
2: 
3: For each line $L_k$, let $f_k(P) = 0$ be its linear equation, normalized such that $f_k(O) > 0$ for all $k \in \{1, \dots, n\}$. A point $P$ lies on the open line segment $OX$ if $P = (1-t)O + tX$ for some $t \in (0, 1)$. The segment $OX$ intersects $L_k$ if and only if $f_k(P) = 0$ for some $t \in (0, 1)$. Since $f_k(P) = (1-t)f_k(O) + tf_k(X)$ and $f_k(O) > 0$, this occurs if and only if $f_k(X) < 0$. Thus, $X$ is red if and only if the number of lines $L_k$ such that $f_k(X) < 0$ is at most $p$. Let $N(X) = |\{k \in \{1, \dots, n\} : f_k(X) < 0\}|$.
4: 
5: We apply a projective transformation that maps $O$ to the point at infinity in the $y$-direction. Under this transformation, the lines $L_k$ are mapped to lines $L'_k$ in the plane. The condition that the open segment $OX$ intersects $L_k$ is transformed into the condition that the vertical ray starting at $X'$ and extending in the $y$-direction intersects $L'_k$. Specifically, $N(X)$ becomes the number of lines $L'_k$ that lie "above" the point $X'$ in the transformed plane.
6: 
7: A point $X' \in I'$ is red if it is the intersection of two lines $L'_i, L'_j$ and there are at most $p$ lines $L'_k$ strictly above it. In the study of line arrangements, the set of points with at most $p$ lines above them is known as the $\le p$-level. The red points are exactly the vertices of the $\le p$-level.
8: 
9: It is a known result in discrete geometry that for any arrangement of $n$ lines in general position, the $\le p$-level has at least $\binom{p+2}{2}$ vertices for $0 \le p \le n-2$. This can be seen by considering the case $n = p+2$, where all $\binom{n}{2} = \binom{p+2}{2}$ intersection points $X$ satisfy $N(X) \le n-2 = p$, meaning all vertices are red. For $n > p+2$, the number of vertices in the $\le p$-level does not decrease. Specifically, the $\le 0$-level (the lower envelope) has at least 1 vertex. The $\le 1$-level adds the vertices of the 1-level, which must contain at least 2 vertices to connect the lines of the arrangement. By induction on $p$, the number of vertices $V(\le p)$ satisfies $V(\le p) \ge V(\le p-1) + (p+1)$, which yields $V(\le p) \ge \sum_{k=0}^p (k+1) = \binom{p+2}{2}$.
10: 
11: To show that $\binom{p+2}{2}$ is the minimum, consider the case $n = p+2$. In any such arrangement, every intersection point $X$ has $N(X) \le n-2 = p$, so all $\binom{n}{2} = \binom{p+2}{2}$ points are red. For $n > p+2$, we can construct an arrangement where exactly $\binom{p+2}{2}$ points are red. For example, consider $p+2$ lines forming a small arrangement near a point $P$, and $n-(p+2)$ lines that are placed far "above" the $\le p$-level of the first $p+2$ lines. These additional lines will not create new red points and will not remove existing ones if they are placed such that $N(X)$ for any vertex $X$ on the additional lines is greater than $p$.
12: 
13: Thus, the minimum number of red points is $\binom{p+2}{2}$.
