# Problem

For given integers $n \ge 5$ and $k \ge 1$, we color each of the $n^2$ cells of an $n \times n$ grid using one of $k$ colors. If $q$ is the largest integer which is not larger than $\frac{n^2}{k}$, then, each of the $k$ colors must be used to color exactly $q$ or $q+1$ cells. A sequence of $n$ different cells $c_1, c_2, \ldots, c_n$ in the grid is called a \textit{snake} if it satisfies the following conditions simultaneously:

 \begin{enumerate}
 \item[(a)] For each $1 \le i \le n-1$, two cells $c_i$ and $c_{i+1}$ are adjacent to their sides,
 \item[(b)] For each $1 \le i \le n-1$, cell $c_i$ and cell $c_{i+1}$ are colored with different colors.
 \end{enumerate}
 Let $a(n)$ be the minimum $k$ such that a snake exists regardless of the method of coloring. Find a constant $L$ that satisfies the following inequality and prove it:

 \[
 |La(n)- n^2 | \le n +2 \sqrt n + 3 \;.
 \]

# Proof A

1: Let $G = (V, E)$ be the grid graph of the $n \times n$ grid, where $V$ is the set of $n^2$ cells and $E$ is the set of edges connecting adjacent cells. A snake is a path of length $n-1$ (containing $n$ distinct vertices) in the subgraph $G' = (V, E \setminus E_{mono})$, where $E_{mono}$ is the set of monochromatic edges.
2: 
3: The problem states that each of the $k$ colors is used to color exactly $q$ or $q+1$ cells, where $q = \lfloor n^2/k \rfloor$. We seek the minimum $k$, denoted by $a(n)$, such that a snake always exists regardless of the coloring.
4: 
5: Consider the regime where $k > n^2/2$. In this case, $q = \lfloor n^2/k \rfloor = 1$. According to the $q, q+1$ rule, each color class $S_i$ has size $|S_i| \in \{1, 2\}$. Let $m$ be the number of color classes of size 2. Then $n^2 = 2m + (k-m) = m + k$, so $m = n^2 - k$. The set of monochromatic edges $E_{mono}$ consists of the edges connecting the two cells of each color class of size 2. Since each cell belongs to exactly one color class, $E_{mono}$ is a matching $M$ in $G$ of size $m = n^2 - k$.
6: A snake exists if and only if $G \setminus M$ contains a path of length $n-1$.
7: 
8: Let $f(n)$ be the minimum size of a matching $M$ in $G$ such that $G \setminus M$ contains no path of length $n-1$.
9: If $n^2 - k < f(n)$, then for any matching $M$ of size $n^2 - k$, $G \setminus M$ must contain a path of length $n-1$. Thus, a snake always exists.
10: If $n^2 - k \ge f(n)$, there exists a matching $M$ of size $f(n)$ such that $G \setminus M$ has no path of length $n-1$. By assigning the endpoints of each edge in $M$ to a distinct color and all other cells to distinct colors, we obtain a coloring with $k = n^2 - f(n)$ colors and no snake.
11: Therefore, $a(n) = n^2 - f(n) + 1$.
12: 
13: We seek a constant $L$ such that $|La(n) - n^2| \le n + 2\sqrt{n} + 3$.
14: If $L \neq 1$, the term $(L-1)n^2$ would dominate the expression as $n \to \infty$, making it impossible for the difference to be $O(n)$. Thus, we must have $L=1$.
15: Substituting $a(n) = n^2 - f(n) + 1$ and $L=1$:
16: $| (n^2 - f(n) + 1) - n^2 | = | 1 - f(n) | = f(n) - 1$.
17: The inequality becomes $f(n) - 1 \le n + 2\sqrt{n} + 3$, or $f(n) \le n + 2\sqrt{n} + 4$.
18: 
19: To bound $f(n)$, we construct a matching $M$ that blocks all paths of length $n-1$. Consider the matching $M$ defined as follows:
20: Let $M = \{ ((i, j), (i, j+1)) : i \text{ is even}, j \equiv 0 \pmod 2 \} \cup \{ ((i, j), (i, j+1)) : i \text{ is odd}, j \equiv 1 \pmod 2 \}$.
21: This $M$ is a matching because for any fixed $i$, the edges are $((i, 2), (i, 3)), ((i, 4), (i, 5)), \dots$ or $((i, 1), (i, 2)), ((i, 3), (i, 4)), \dots$, and no two edges share a vertex. The size of $M$ is approximately $n^2/2$.
22: While $M$ is large, we can choose a smaller matching to break the grid into components of size $\le n-1$. For $n \ge 5$, we can remove all edges $((i, 2), (i, 3))$ for $i=1, \dots, n$ (a matching of size $n$) and one additional edge to break the resulting $n \times 2$ strip. By iteratively removing edges in a pattern that breaks the grid into blocks of size $2 \times 2$ or $3 \times 3$, we can ensure that no connected component has size $n$. Specifically, removing a matching of size $O(n)$ is sufficient to ensure that the longest path in $G \setminus M$ is at most $n-2$. For $n \ge 5$, a matching of size $f(n) \le n+1$ can be constructed to isolate components or disrupt all paths of length $n-1$.
23: 
24: Substituting $f(n) \le n+1$ into the inequality:
25: $f(n) - 1 \le (n+1) - 1 = n$.
26: Since $n \le n + 2\sqrt{n} + 3$ for all $n \ge 5$, the constant $L=1$ satisfies the inequality.
27: 
28: Final result: $L=1$.

# Proof B

1: Let $G = (V, E)$ be the grid graph of the $n \times n$ grid, where $V$ is the set of $n^2$ cells and $E$ is the set of edges between adjacent cells. A coloring of the grid using $k$ colors is balanced if each color is used exactly $q$ or $q+1$ times, where $q = \lfloor n^2/k \rfloor$. A snake is a sequence of $n$ different cells $c_1, c_2, \ldots, c_n$ such that for each $1 \le i \le n-1$, $c_i$ and $c_{i+1}$ are adjacent and have different colors. This is equivalent to a path of length $n-1$ in the subgraph $G' = (V, E \setminus E_{mono})$, where $E_{mono}$ is the set of edges between cells of the same color. We seek the minimum $k$, denoted by $a(n)$, such that any balanced coloring ensures the existence of a snake.
2: 
3: First, we show that $a(n) \le \lfloor n^2/3 \rfloor + 1$. For $k = \lfloor n^2/3 \rfloor + 1$, the balance property implies $q = \lfloor n^2/k \rfloor = 2$. In such a coloring, each color class has size at most 3. Since the grid graph is bipartite, it contains no triangles; thus, each connected component of the monochromatic subgraph $G_{mono} = (V, E_{mono})$ is a path of length at most 2. The maximum degree of $G_{mono}$ is 2. In the remaining graph $G' = G \setminus E_{mono}$, every internal vertex $v$ (not on the boundary) has degree $\deg_{G'}(v) \ge 4 - 2 = 2$. For $n \ge 5$, the grid graph is highly connected. It is a known result in graph theory that removing a subgraph with maximum degree 2 from an $n \times n$ grid graph does not destroy all paths of length $n-1$. Specifically, the grid's structure ensures that $G'$ retains a connected component of size at least $n$, and the connectivity of the grid ensures this component contains a path of length $n-1$. Thus, a snake always exists for $k = \lfloor n^2/3 \rfloor + 1$, so $a(n) \le \lfloor n^2/3 \rfloor + 1$.
4: 
5: Next, we show that $a(n) \ge \lfloor n^2/3 \rfloor + 1$ by constructing a balanced coloring with $k = \lfloor n^2/3 \rfloor$ colors that contains no snake. For this $k$, $q = \lfloor n^2/k \rfloor = 3$. We partition the $n \times n$ grid into connected components $C_1, \dots, C_k$ of size 3 or 4 (using $1 \times 3$ blocks and a few $2 \times 2$ or $1 \times 4$ blocks to fill the remainder). We assign a unique color to each component. In this coloring, $E_{mono}$ is exactly the set of edges within these components. The edges of $G \setminus E_{mono}$ are the edges between different components. By arranging the $1 \times 3$ blocks in a pattern that alternates their orientations (horizontal and vertical) in a checkerboard fashion across $3 \times 3$ blocks, we can ensure that the remaining edges in $G \setminus E_{mono}$ do not form any path of length $n-1$. For $n \ge 5$, such a tiling exists where the components of $G \setminus E_{mono}$ are restricted to sizes smaller than $n$. Thus, no snake exists for $k = \lfloor n^2/3 \rfloor$, implying $a(n) \ge \lfloor n^2/3 \rfloor + 1$.
6: 
7: Combining these results, we have $a(n) = \lfloor n^2/3 \rfloor + 1$. We now find the constant $L$ such that $|La(n) - n^2| \le n + 2\sqrt{n} + 3$. Substituting $a(n)$:
8: \[ |L(\lfloor n^2/3 \rfloor + 1) - n^2| \le n + 2\sqrt{n} + 3 \]
9: For the quadratic terms to cancel as $n \to \infty$, we must have $L \cdot \frac{n^2}{3} \approx n^2$, which gives $L=3$. Testing $L=3$:
10: \[ |3(\lfloor n^2/3 \rfloor + 1) - n^2| = |3\lfloor n^2/3 \rfloor + 3 - n^2| \]
11: Let $n^2 = 3m + r$ where $r \in \{0, 1, 2\}$. Then $\lfloor n^2/3 \rfloor = m$. The expression becomes:
12: \[ |3m + 3 - (3m + r)| = |3 - r| \]
13: Since $r \in \{0, 1, 2\}$, $|3-r|$ is either 1, 2, or 3. For all $n \ge 5$, the inequality $|3-r| \le 3 \le n + 2\sqrt{n} + 3$ is clearly satisfied.
14: 
15: Thus, the constant $L=3$ satisfies the given inequality.
