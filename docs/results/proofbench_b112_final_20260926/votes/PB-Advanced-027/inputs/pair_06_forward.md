# Problem

Alice the architect and Bob the builder play a game. First, Alice
 chooses two points $P$ and $Q$ in the plane and a subset $S$ of
 the plane, which are announced to Bob. Next, Bob marks infinitely
 many points in the plane, designating each a city. He may not place
 two cities within distance at most one unit of each other, and no
 three cities he places may be collinear. Finally, roads are constructed
 between the cities as follows: for each pair $A,B$ of cities, they
 are connected with a road along the line segment $AB$ if and only
 if the following condition holds: For every city $C$ distinct from
 $A$ and $B$, there exists $R\in S$ such that $\triangle PQR$ is
 directly similar to either $\triangle ABC$ or $\triangle BAC$. Alice
 wins the game if

 \noindent (i) the resulting roads allow for travel between any pair
 of cities via a finite sequence of roads and

 \noindent (ii) no two roads cross.

 \noindent Otherwise, Bob wins. Determine, with proof, which player
 has a winning strategy. (Note: $\triangle UVW$ is directly similar
 to $\triangle XYZ$ if there exists a sequence of rotations, translations,
 and dilations sending $U$ to $X$, $V$ to $Y$, and $W$ to $Z$.)

# Proof A

1: To determine which player has a winning strategy, we analyze the condition for the existence of a road between two cities $A$ and $B$. Let the positions of the cities be represented by complex numbers $a, b, c, \dots$. Alice chooses points $P$ and $Q$ and a subset $S$ of the plane. Let $p, q$ be the complex numbers for $P$ and $Q$. We assume $P \neq Q$. Let $S' = \{ \frac{r-p}{q-p} : r \in S \}$.
2: 
3: A road is constructed between cities $A$ and $B$ if and only if for every city $C$ distinct from $A$ and $B$, $\triangle PQR$ is directly similar to either $\triangle ABC$ or $\triangle BAC$ for some $R \in S$. In terms of complex numbers, $\triangle PQR \sim_{dir} \triangle ABC$ if $\frac{r-p}{q-p} = \frac{c-a}{b-a}$, and $\triangle PQR \sim_{dir} \triangle BAC$ if $\frac{r-p}{q-p} = \frac{c-b}{a-b}$.
4: Note that $\frac{c-b}{a-b} = \frac{c-a+a-b}{a-b} = 1 - \frac{c-a}{b-a}$. Let $z = \frac{c-a}{b-a}$. Then $\frac{c-b}{a-b} = 1-z$.
5: Let $U = S' \cup \{1-s : s \in S'\}$. A road $AB$ exists if and only if for every city $C \in \mathcal{C} \setminus \{A, B\}$, the ratio $\frac{c-a}{b-a}$ belongs to $U$. Let $V = \mathbb{C} \setminus U$ be the set of "forbidden" ratios. A road $AB$ exists if and only if for all $C \in \mathcal{C} \setminus \{A, B\}$, $\frac{c-a}{b-a} \notin V$.
6: 
7: Bob wins if the resulting graph is either disconnected or non-planar. We consider two cases based on whether $V$ is meager in the complex plane $\mathbb{C}$.
8: 
9: Case 1: $V$ is meager.
10: Bob can ensure the graph is $K_\infty$, which is non-planar. He places cities $C_1, C_2, \dots$ iteratively. For $k=1, 2$, he picks any two points such that $|c_1-c_2| > 1$. For $k \ge 3$, he chooses $c_k$ to avoid the following sets:
11: 1. To ensure $C_k$ does not destroy any existing road $C_i C_j$ ($i, j < k$), he requires $\frac{c_k-c_i}{c_j-c_i} \notin V$, so $c_k \notin c_i + V(c_j-c_i)$.
12: 2. To ensure no existing city $C_m$ ($m < k$) destroys a potential road $C_i C_k$ ($i < k$), he requires $\frac{c_m-c_i}{c_k-c_i} \notin V$. This implies $c_k-c_i \notin \frac{1}{V}(c_m-c_i)$, so $c_k \notin c_i + V^{-1}(c_m-c_i)$, where $V^{-1} = \{1/v : v \in V, v \neq 0\}$.
13: 3. To satisfy the game constraints, $c_k \notin \bigcup_{m < k} D(C_m, 1)$ and $c_k \notin \bigcup_{i < j < k} \text{Line}(C_i, C_j)$.
14: 
15: Since $V$ is meager, $V^{-1}$ is also meager (as $z \mapsto 1/z$ is a homeomorphism on $\mathbb{C} \setminus \{0\}$). The forbidden set for $c_k$ is a finite union of meager sets, lines, and disks. By the Baire Category Theorem, a meager set cannot cover a non-empty open set. The complement of the finite union of disks is a non-empty open set. Thus, Bob can always pick $c_k$. The resulting graph is $K_\infty$, which is non-planar, so Bob wins.
16: 
17: Case 2: $V$ is not meager.
18: Bob can ensure the graph is disconnected by destroying every potential road. He enumerates all pairs of indices $(i, j)$ as a sequence $P_1, P_2, \dots$. He picks cities $C_k$ inductively. For each pair $P_m = (i, j)$, he assigns a unique index $k_m$ to a city $C_{k_m}$ that will be used to destroy the road $C_i C_j$.
19: 
20: Since $V$ is non-meager, $V$ is not nowhere dense. Thus, its closure $\text{cl}(V)$ contains a non-empty open ball $B(z, \rho)$. This implies $V$ is dense in $B(z, \rho)$. When picking city $C_j$, Bob ensures that for all $i < j$, if $(i, j) = P_m$, then $|c_j - c_i|$ is chosen sufficiently large such that the scaled ball $B_{i,j} = B(c_i + (c_j - c_i)z, |c_j - c_i|\rho)$ has area $\pi(|c_j - c_i|\rho)^2 > (k_m-1)\pi$.
21: 
22: When Bob picks $C_k$ (where $k = k_m$) to destroy the road $P_m = (i, j)$, he considers the set $S_{i,j} = c_i + V(c_j - c_i)$. $S_{i,j}$ is dense in $B_{i,j}$. The union of existing disks $\bigcup_{n < k} D(C_n, 1)$ has area at most $(k-1)\pi$. Since $\text{Area}(B_{i,j}) > (k-1)\pi$, the set $U = B_{i,j} \setminus \bigcup_{n < k} D(C_n, 1)$ is a non-empty open set.
23: Since $S_{i,j}$ is dense in $B_{i,j}$, the intersection $S_{i,j} \cap U$ is dense in $U$. A dense subset of a non-empty open set cannot be contained in a nowhere dense set. The union of lines $\bigcup \text{Line}$ is a finite union of lines, which is nowhere dense. If $S_{i,j} \cap U$ were contained in the union of lines, then $U$ would be contained in the closure of the union of lines, which is the union of lines itself. However, a non-empty open set cannot be contained in a finite union of lines. Therefore, $S_{i,j} \cap U \setminus \bigcup \text{Line}$ is non-empty. Bob picks $c_k$ from this set.
24: 
25: Since every pair $(i, j)$ is eventually destroyed, the resulting graph has no edges and is disconnected. Bob wins.
26: 
27: In all cases, Bob has a winning strategy.

# Proof B

1: To determine which player has a winning strategy, we represent the points in the plane as complex numbers. Alice chooses points $P$ and $Q$ and a subset $S$ of the plane. Let $\rho(R) = \frac{r-p}{q-p}$ for $R \in S$, and let $S' = \{ \rho(R) : R \in S \}$.
2: 
3: A road is constructed between two cities $A$ and $B$ if and only if for every city $C \in \mathcal{C} \setminus \{A, B\}$, $\triangle PQR$ is directly similar to either $\triangle ABC$ or $\triangle BAC$ for some $R \in S$.
4: Direct similarity $\triangle PQR \sim \triangle ABC$ implies $\frac{c-a}{b-a} = \rho(R)$.
5: Direct similarity $\triangle PQR \sim \triangle BAC$ implies $\frac{c-b}{a-b} = \rho(R)$.
6: Note that $\frac{c-b}{a-b} = \frac{c-a+a-b}{a-b} = 1 - \frac{c-a}{b-a}$.
7: Let $T = S' \cup (1 - S')$. The condition for a road to exist between $A$ and $B$ is:
8: For every $C \in \mathcal{C} \setminus \{A, B\}$, $\frac{c-a}{b-a} \in T$.
9: Let $U = \mathbb{C} \setminus T$. A road $AB$ exists if and only if for every $C \in \mathcal{C} \setminus \{A, B\}$, $\frac{c-a}{b-a} \notin U$.
10: This is equivalent to saying that for all $C \in \mathcal{C} \setminus \{A, B\}$, $C \notin L_{AB}(U)$, where $L_{AB}(U) = \{ a + (b-a)u : u \in U \}$.
11: 
12: Bob wins if he can ensure the resulting graph is either disconnected or non-planar. We consider two cases for the set $U$.
13: 
14: Case 1: $U$ is contained in a finite union of lines and disks.
15: Bob wins by constructing a $K_5$ subgraph. He picks five cities $C_1, \dots, C_5$ greedily. For each $n \in \{1, \dots, 5\}$, Bob picks $C_n$ to avoid:
16: 1. $\bigcup_{i < j < n} L_{C_i C_j}(U)$, ensuring $C_n$ does not destroy roads between existing cities.
17: 2. $\bigcup_{i < n, j < n, i \neq j} V_{C_i C_j}(U)$, where $V_{C_i C_j}(U) = \{ C_i + \frac{C_j - C_i}{u} : u \in U \}$, ensuring $C_n$ does not destroy potential roads between $C_i$ and $C_n$.
18: 3. $\bigcup_{i < j < n} \text{line}(C_i, C_j)$, to ensure no three cities are collinear.
19: 4. $\bigcup_{i < n} D(C_i, 1)$, to ensure the distance between any two cities is greater than 1.
20: 
21: Since $U$ is a finite union of lines and disks, $L_{C_i C_j}(U)$ is also a finite union of lines and disks. The set $V_{C_i C_j}(U)$ is the image of $U$ under a Möbius transformation $u \mapsto C_i + \frac{C_j - C_i}{u}$. Möbius transformations map lines and circles to lines and circles. Thus, $V_{C_i C_j}(U)$ is a finite union of lines, disks, or complements of disks.
22: To avoid the complements of disks, Bob can pick $C_1, C_2$ such that $|C_1 - C_2|$ is very large. This ensures that the radii of the disks whose complements form the forbidden sets in $V$ are also very large. He can then pick $C_3, C_4, C_5$ within the intersection of these large disks. Since the intersection of finitely many open disks is a non-empty open set, and he only needs to avoid a finite union of lines and disks within it, a valid $C_n$ always exists.
23: 
24: For all subsequent cities $C_n$ ($n > 5$), Bob avoids $\bigcup_{1 \le i < j \le 5} L_{C_i C_j}(U)$, along with collinearity and distance constraints. This ensures the roads between $C_1, \dots, C_5$ are never destroyed. The resulting graph contains a $K_5$ subgraph, making it non-planar. Bob wins.
25: 
26: Case 2: $U$ is not contained in any finite union of lines and disks.
27: Bob wins by ensuring no roads are constructed. He enumerates all pairs of cities as $P_1, P_2, \dots$ and picks cities $C_n$ greedily to destroy each road.
28: 1. Pick $C_1, C_2$ such that $|C_1 - C_2| > 1$.
29: 2. For $n = 3, 4, \dots$, let $(C_i, C_j)$ be the first pair of cities that is not yet "destroyed" (i.e., no city $C_k$ has been placed such that $\frac{C_k - C_i}{C_j - C_i} \in U$). Bob picks $C_n$ such that:
30:    - $C_n \in L_{C_i C_j}(U)$.
31:    - $C_n \notin \bigcup_{a < b < n} \text{line}(C_a, C_b)$ to ensure no three cities are collinear.
32:    - $C_n \notin \bigcup_{a < n} D(C_a, 1)$ to ensure distance $> 1$.
33: 
34: Since $U$ is not contained in a finite union of lines and disks, $L_{C_i C_j}(U)$ is also not. A set not contained in a finite union of lines and disks cannot be covered by a finite union of lines and disks. Thus, Bob can always find such a $C_n$. By this construction, every pair of cities is eventually destroyed. The resulting graph has no edges and is therefore disconnected. Bob wins.
35: 
36: In all cases, Bob has a winning strategy.
