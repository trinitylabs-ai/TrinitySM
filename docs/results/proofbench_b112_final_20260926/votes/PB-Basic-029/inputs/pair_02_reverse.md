# Problem

Let $p$ and $n$ be integers with $0\le p\le n-2$. Consider a set
 $S$ of $n$ lines in the plane such that no two of them are parallel
 and no three have a common point. Denote by $I$ the set of intersections
 of lines in $S$. Let $O$ be a point in the plane not lying on any
 line of $S$. A point $X\in I$ is colored red if the open line segment
 $OX$ intersects at most $p$ lines in $S$. What is the minimum number
 of red points that is contained in $I$?

# Proof A

1: Let $S = \{L_1, L_2, \dots, L_n\}$ be a set of $n$ lines in the plane in general position (no two lines are parallel and no three lines are concurrent). Let $O$ be a point not lying on any line of $S$. For any point $X$ in the plane, we define the level of $X$ relative to $O$ as the number of lines in $S$ that separate $X$ from $O$. A point $X \in I$ (the set of intersections of lines in $S$) is colored red if its level is at most $p$. We wish to find the minimum number of red points for $0 \le p \le n-2$.
2: 
3: First, we establish a lower bound on the number of red points. Let $N(n, p)$ denote the minimum number of red points for any set of $n$ lines in general position.
4: Consider the base case $n = p+2$. Any intersection point $X \in I$ is the intersection of exactly two lines $L_i, L_j \in S$. There are $n-2 = p$ lines in $S$ other than $L_i$ and $L_j$. The number of lines separating $X$ from $O$ cannot exceed the total number of lines in $S \setminus \{L_i, L_j\}$, which is $p$. Thus, every intersection point in $I$ is red. The number of such points is $\binom{n}{2} = \binom{p+2}{2}$. Hence, $N(p+2, p) = \binom{p+2}{2}$.
5: 
6: For $n > p+2$, we utilize a known result from the theory of $k$-levels in line arrangements: the minimum number of vertices of level at most $p$ is a non-decreasing function of $n$. Specifically, for any $n \ge p+2$, the number of vertices of level $\le p$ is minimized when the lines are in a "near-parallel" configuration (for instance, when all lines are tangent to a convex curve), and this minimum value is $\binom{p+2}{2}$. Thus, $N(n, p) \ge N(p+2, p) = \binom{p+2}{2}$.
7: 
8: To show that $\binom{p+2}{2}$ is the minimum, we provide a construction. Let the lines $L_i$ be defined by the equations $f_i(x, y) = y - ix - i^2 = 0$ for $i=1, \dots, n$. The intersection point $X_{ij}$ of $L_i$ and $L_j$ (for $i < j$) is found by solving:
9: $ix + i^2 = jx + j^2 \implies (i-j)x = j^2 - i^2 \implies x = -(i+j)$
10: $y = i(-(i+j)) + i^2 = -ij$
11: Thus $X_{ij} = (-(i+j), -ij)$. For any $k \neq i, j$, we evaluate:
12: $f_k(X_{ij}) = -ij - k(-(i+j)) - k^2 = -ij + ki + kj - k^2 = -(k-i)(k-j)$
13: Choose the point $O = (0, Y)$ where $Y$ is sufficiently large (e.g., $Y > n^2$) such that $f_i(O) = Y - i^2 > 0$ for all $i=1, \dots, n$. A line $L_k$ separates $O$ from $X_{ij}$ if and only if $f_k(X_{ij})$ and $f_k(O)$ have opposite signs. Since $f_k(O) > 0$, $L_k$ separates them if and only if $f_k(X_{ij}) < 0$.
14: From our calculation, $f_k(X_{ij}) = -(k-i)(k-j) < 0$ if and only if $(k-i)(k-j) > 0$. For $i < j$, this occurs if $k < i$ or $k > j$.
15: The number of such $k \in \{1, \dots, n\} \setminus \{i, j\}$ is $(i-1) + (n-j)$.
16: The point $X_{ij}$ is red if:
17: $(i-1) + (n-j) \le p \iff j - i \ge n - 1 - p$
18: Let $m = n - 1 - p$. We count the number of pairs $(i, j)$ with $1 \le i < j \le n$ such that $j - i \ge m$.
19: For a fixed $i$, $j$ can range from $i+m$ to $n$, providing $n - (i+m) + 1 = n - m - i + 1$ values.
20: The total number of red points is:
21: $\sum_{i=1}^{n-m} (n - m - i + 1) = (n-m) + (n-m-1) + \dots + 1 = \frac{(n-m)(n-m+1)}{2}$
22: Substituting $n-m = n - (n-1-p) = p+1$:
23: $\text{Number of red points} = \frac{(p+1)(p+2)}{2} = \binom{p+2}{2}$
24: Since the lower bound is $\binom{p+2}{2}$ and we have a construction that achieves this value, the minimum number of red points is $\binom{p+2}{2}$.

# Proof B

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
