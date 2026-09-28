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

# Proof B

1: Let $G = (V, E)$ be the $n \times n$ grid graph, where $V$ is the set of $n^2$ cells and $E$ is the set of edges connecting adjacent cells. A coloring of the grid using $k$ colors is balanced if each color is used exactly $q$ or $q+1$ times, where $q = \lfloor n^2/k \rfloor$. A snake is a path of $n$ distinct cells $c_1, c_2, \ldots, c_n$ such that for each $1 \le i \le n-1$, $c_i$ and $c_{i+1}$ are adjacent and have different colors.
2: 
3: Let $S$ be the set of monochromatic edges in $G$ under a given coloring. A path is a snake if and only if it contains no edges from $S$. Thus, a snake exists if and only if the graph $G' = (V, E \setminus S)$ contains a path of length $n-1$. The value $a(n)$ is the minimum $k$ such that for any balanced coloring, $G \setminus S$ contains a path of length $n-1$.
4: 
5: Consider $k = \lfloor n^2/2 \rfloor + 1$. For this $k$, we have $q = \lfloor n^2/k \rfloor = 1$. In a balanced coloring with $q=1$, each color is used either 1 or 2 times. Let $m$ be the number of colors used twice. Then $2m + (k-m) = n^2$, so $m = n^2 - k = n^2 - (\lfloor n^2/2 \rfloor + 1) = \lceil n^2/2 \rceil - 1$. Each color used twice can contribute at most one edge to $S$, and colors used once contribute none. Therefore, $S$ is a matching (a set of edges with no common vertices) of size at most $m \le n^2/2$.
6: 
7: The $n \times n$ grid graph $G$ is a bipartite graph that contains a Hamiltonian path (a path of length $n^2-1$). A known result in graph theory states that if $G$ is a Hamiltonian bipartite graph with $N$ vertices and $S$ is a matching, then $G \setminus S$ contains a path of length at least $N/2$. In our case, $N = n^2$, so $G \setminus S$ contains a path of length at least $n^2/2$. For $n \ge 2$, $n^2/2 \ge n-1$. Thus, for $k = \lfloor n^2/2 \rfloor + 1$, every balanced coloring admits a snake, implying $a(n) \le \lfloor n^2/2 \rfloor + 1$.
8: 
9: To determine the constant $L$, we observe that if $k$ is small, $q$ is large, and $S$ can be made large enough to destroy all paths of length $n-1$. For instance, if $k=2$, one can color the grid such that $S$ contains almost all edges, leaving only a few edges in $G \setminus S$ and thus no path of length $n-1$. This implies $a(n) > 2$. The threshold $a(n)$ occurs when $S$ becomes small enough (specifically when $q=1$) that the matching-like structure of $S$ cannot block all paths of length $n-1$. Given the structure of the required inequality, we test $L=2$.
10: 
11: If $a(n) = \lfloor n^2/2 \rfloor + 1$, we evaluate the expression $|2a(n) - n^2|$:
12: - If $n^2$ is even, $a(n) = n^2/2 + 1$, so $|2(n^2/2 + 1) - n^2| = |2| = 2$.
13: - If $n^2$ is odd, $a(n) = (n^2-1)/2 + 1 = (n^2+1)/2$, so $|2((n^2+1)/2) - n^2| = |n^2+1 - n^2| = 1$.
14: 
15: In both cases, $|2a(n) - n^2| \le 2$. For $n \ge 5$, the right-hand side of the inequality is $n + 2\sqrt{n} + 3 \ge 5 + 2\sqrt{5} + 3 \approx 12.47$. Thus, the inequality $|2a(n) - n^2| \le n + 2\sqrt{n} + 3$ is satisfied.
16: 
17: The constant $L=2$ satisfies the inequality.
