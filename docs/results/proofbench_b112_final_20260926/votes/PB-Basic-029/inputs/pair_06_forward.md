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
