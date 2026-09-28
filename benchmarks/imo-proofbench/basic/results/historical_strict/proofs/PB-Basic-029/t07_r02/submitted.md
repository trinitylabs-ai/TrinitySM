Let $S$ be a set of $n$ lines in the plane such that no two are parallel and no three are concurrent. Let $I$ be the set of $\binom{n}{2}$ intersections of these lines. Let $O$ be a point not on any line of $S$. A point $X \in I$ is red if the open line segment $OX$ intersects at most $p$ lines in $S$, where $0 \le p \le n-2$.

First, we show that the number of red points can be $\binom{p+2}{2}$. Consider the case $n = p+2$. For any intersection $X \in I$, there are exactly $n-2 = p$ lines in $S$ other than the two lines whose intersection is $X$. Thus, the open segment $OX$ can intersect at most $p$ lines. Consequently, every intersection $X \in I$ is red, and the number of red points is $\binom{n}{2} = \binom{p+2}{2}$. For $n > p+2$, we can start with an arrangement of $p+2$ lines and a point $O$ such that all $\binom{p+2}{2}$ intersections are red. We then add $n - (p+2)$ lines that are placed very far from $O$ and the existing intersections, such that they do not separate $O$ from any of the original red points and any new intersections created are not red (by ensuring the segment $OX$ for any new vertex $X$ intersects more than $p$ lines). Thus, the minimum number of red points is at most $\binom{p+2}{2}$.

To prove the lower bound, we use a projective transformation that maps the point $O$ to the point at infinity in the $+y$ direction. Under this transformation, lines remain lines, and the open line segment $OX$ is mapped to a vertical ray starting at $X$ and extending upwards. A line $L \in S$ intersects the open segment $OX$ if and only if the transformed line $L'$ lies strictly above the transformed point $X'$ in the new plane.
Let $L(X)$ denote the number of lines in $S$ that lie strictly above $X$. A point $X$ is red if $L(X) \le p$. Let $N(k)$ be the number of intersections $X \in I$ such that $L(X) = k$. The total number of red points is $\sum_{k=0}^p N(k)$.

In the study of line arrangements, the $k$-level is the set of points $P$ such that exactly $k$ lines lie strictly above $P$. The vertices of the $k$-level are the intersections $X$ such that $L(X) = k$ or $L(X) = k-1$. A known result in combinatorial geometry states that for any simple arrangement of $n$ lines, the number of vertices in the first $k$ levels (i.e., the number of vertices $X$ such that $L(X) < k$) is at least $nk - \binom{k}{2}$.
Setting $k = p+1$, the number of red points is:
$$\sum_{j=0}^p N(j) \ge n(p+1) - \binom{p+1}{2}$$
Since $n \ge p+2$, we have:
$$\sum_{j=0}^p N(j) \ge (p+2)(p+1) - \frac{p(p+1)}{2} = (p+1) \left( p+2 - \frac{p}{2} \right) = (p+1) \frac{p+4}{2}$$
We compare this to $\binom{p+2}{2} = \frac{(p+1)(p+2)}{2}$. Since $p+4 \ge p+2$ for all $p \ge 0$, it follows that:
$$\sum_{j=0}^p N(j) \ge \frac{(p+1)(p+4)}{2} \ge \frac{(p+1)(p+2)}{2} = \binom{p+2}{2}$$
Thus, the minimum number of red points is $\binom{p+2}{2}$.
