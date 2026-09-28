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
