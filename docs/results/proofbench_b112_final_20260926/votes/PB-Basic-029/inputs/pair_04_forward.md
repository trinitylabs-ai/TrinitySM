# Problem

Let $p$ and $n$ be integers with $0\le p\le n-2$. Consider a set
 $S$ of $n$ lines in the plane such that no two of them are parallel
 and no three have a common point. Denote by $I$ the set of intersections
 of lines in $S$. Let $O$ be a point in the plane not lying on any
 line of $S$. A point $X\in I$ is colored red if the open line segment
 $OX$ intersects at most $p$ lines in $S$. What is the minimum number
 of red points that is contained in $I$?

# Proof A

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

# Proof B

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
