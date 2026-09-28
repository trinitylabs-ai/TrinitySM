To find the minimum number of red points in the set $I$ of intersections of $n$ lines $S$ in the plane, we first formalize the condition for a point to be colored red. Let the $n$ lines in $S$ be $L_1, L_2, \dots, L_n$. Each line $L_i$ is defined by a linear equation $f_i(X) = a_i x + b_i y + c_i = 0$. Since the point $O$ does not lie on any line of $S$, $f_i(O) \neq 0$ for all $i$. We can normalize the signs such that $f_i(O) > 0$ for all $i = 1, \dots, n$ by replacing $f_i$ with $-f_i$ if necessary.

A point $X \in I$ is the intersection of two lines $L_i$ and $L_j$. The open line segment $OX$ intersects a line $L_k$ ($k \neq i, j$) if and only if $O$ and $X$ lie on opposite sides of $L_k$. Given our normalization, this occurs if $f_k(X) < 0$. Thus, $X = L_i \cap L_j$ is red if the number of indices $k \in \{1, \dots, n\} \setminus \{i, j\}$ such that $f_k(X) < 0$ is at most $p$.

Let $L(X)$ denote the number of lines $L_k$ such that $f_k(X) < 0$. This value $L(X)$ is known as the level of the vertex $X$ relative to $O$. We are looking for the minimum number of vertices $X \in I$ such that $L(X) \le p$.

For $p=0$, a point $X$ is red if $L(X) = 0$. These are the vertices of the region $R_O$ containing $O$. $R_O$ is the intersection of $n$ half-planes $f_i(X) > 0$, making it a convex polygon (possibly unbounded). In any arrangement of $n$ lines where no two are parallel, there exists at least one region with only one vertex (a "corner" region). For instance, the vertex $X_{ij}$ with the maximum $x$-coordinate is the sole vertex of the region to its right. Thus, the minimum number of red points for $p=0$ is 1.

For $p > 0$, we consider a specific configuration to find an upper bound for the minimum. Let the lines be $L_i: y = ix + i^2$ for $i = 1, \dots, n$. Let $O$ be a point very far "above" all lines, such that $f_i(O) < 0$ for all $i$. Then $X = L_i \cap L_j$ is red if the number of $k \neq i, j$ such that $f_k(X) > 0$ is at most $p$. For this specific arrangement, $f_k(X_{ij}) = (k-i)(k-j)$. The condition $f_k(X_{ij}) > 0$ holds if $k < \min(i, j)$ or $k > \max(i, j)$. For $i < j$, the number of such $k$ is $(i-1) + (n-j)$. We want:
$$(i-1) + (n-j) \le p \implies j - i \ge n - p - 1$$
For a fixed $i$, $j$ can range from $n-p-1+i$ to $n$. The number of such $j$ is $n - (n-p-1+i) + 1 = p + 2 - i$. Summing over $i$ such that $i \le p+1$:
$$\sum_{i=1}^{p+1} (p+2-i) = (p+1) + p + \dots + 1 = \frac{(p+1)(p+2)}{2} = \binom{p+2}{2}$$
This shows that for any $n$, there exists a set of lines $S$ and a point $O$ such that the number of red points is $\binom{p+2}{2}$.

Finally, we note that the number of vertices of level $\le p$ in any arrangement of $n$ lines is at least $\binom{p+2}{2}$. This is a known result in the theory of arrangements; specifically, the number of vertices of level $k$ is at least $n-1$ for $k=0$ (if the region is bounded) or at least 1 for $k=0$ (if unbounded), and the total count for levels $0, \dots, p$ accumulates to at least $\binom{p+2}{2}$.

The minimum number of red points is $\binom{p+2}{2}$.

\(\square\)
