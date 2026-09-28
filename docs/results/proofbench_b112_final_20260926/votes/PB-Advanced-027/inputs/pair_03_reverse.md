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

# Proof B

1: To determine which player has a winning strategy, we analyze the condition under which a road is constructed between two cities. Let the points $P, Q, R$ and the cities $A, B, C$ be represented by complex numbers $p, q, r$ and $a, b, c$, respectively.
2: 
3: A triangle $\triangle PQR$ is directly similar to $\triangle ABC$ if there exists a direct similarity transformation $f(z) = \alpha z + \beta$ ($\alpha \neq 0$) such that $f(p) = a, f(q) = b$, and $f(r) = c$. This implies:
4: \[ a = \alpha p + \beta, \quad b = \alpha q + \beta, \quad c = \alpha r + \beta \]
5: Solving for $\alpha$ and $\beta$ gives $\alpha = \frac{b-a}{q-p}$ and $\beta = a - \frac{b-a}{q-p}p$. Substituting these into the expression for $c$:
6: \[ c = \frac{b-a}{q-p}(r-p) + a \implies \frac{c-a}{b-a} = \frac{r-p}{q-p} \]
7: Similarly, $\triangle PQR$ is directly similar to $\triangle BAC$ if $\frac{c-b}{a-b} = \frac{r-p}{q-p}$. Let $\Omega = \left\{ \frac{r-p}{q-p} : r \in S \right\}$. The condition for a road between cities $A$ and $B$ is that for every city $C \neq A, B$:
8: \[ \frac{c-a}{b-a} \in \Omega \quad \text{or} \quad \frac{c-b}{a-b} \in \Omega \]
9: Let $z = \frac{c-a}{b-a}$. Then $\frac{c-b}{a-b} = \frac{c-a+a-b}{a-b} = 1 - z$. Thus, the road condition is $z \in \Omega \cup (1-\Omega)$. Let $K = \Omega \cup (1-\Omega)$ and $W = \mathbb{C} \setminus K$. A road exists between $A$ and $B$ if and only if for all cities $C \neq A, B$, $\frac{c-a}{b-a} \notin W$.
10: Let $Z_{AB} = \{ a + (b-a)w : w \in W \}$ be the "killing zone" for the road $AB$. A road exists between $A$ and $B$ if and only if no city $C$ (other than $A, B$) lies in $Z_{AB}$.
11: 
12: Bob has a winning strategy. We consider two cases based on the interior of the closure of $W$.
13: 
14: Case 1: $\text{int}(\text{cl}(W)) = \emptyset$.
15: In this case, $\text{cl}(W)$ is a nowhere dense set. Bob aims to construct a $K_5$ subgraph. He picks five cities $z_1, \dots, z_5$ greedily such that $|z_i - z_j| > 1$, no three are collinear, and for all $1 \le i < j \le 5$, no other city $z_k$ ($k \in \{1, \dots, 5\} \setminus \{i, j\}$) lies in $Z_{z_i z_j}$. This is possible because the conditions $z_k \notin Z_{z_i z_j}$ are requirements that $z_k$ avoid a nowhere dense set.
16: For $n > 5$, Bob must pick $z_n$ such that for all $1 \le i < j \le 5$, the road $z_i z_j$ is not killed. This requires $z_n \notin Z_{z_i z_j}$. Additionally, Bob must satisfy the game's constraints: $|z_n - z_k| > 1$ for all $k < n$, and $z_n$ is not collinear with any $z_j, z_k$ for $j, k < n$.
17: The forbidden set for $z_n$ is $F_n = \left( \bigcup_{1 \le i < j \le 5} Z_{z_i z_j} \right) \cup \left( \bigcup_{k, m < n} L_{km} \right) \cup \left( \bigcup_{k < n} D(z_k, 1) \right)$, where $L_{km}$ is the line through $z_k, z_m$ and $D(z_k, 1)$ is the closed disk of radius 1.
18: Since $\text{cl}(W)$ is nowhere dense, each $Z_{z_i z_j}$ is nowhere dense. Lines $L_{km}$ are also nowhere dense. By the Baire Category Theorem, the finite union of nowhere dense sets is nowhere dense, so $\text{int}(\bigcup Z_{z_i z_j} \cup \bigcup L_{km}) = \emptyset$. Thus, its complement is dense in $\mathbb{C}$. The set $U_n = \mathbb{C} \setminus \bigcup_{k < n} D(z_k, 1)$ is a non-empty open set. The intersection of a dense set and a non-empty open set is non-empty, so Bob can always pick $z_n \in (\mathbb{C} \setminus (\bigcup Z_{z_i z_j} \cup \bigcup L_{km})) \cap U_n$.
19: The resulting graph contains a $K_5$ subgraph. Since any embedding of $K_5$ in the plane with straight edges contains at least one crossing, Alice fails condition (ii).
20: 
21: Case 2: $\text{int}(\text{cl}(W)) \neq \emptyset$.
22: In this case, $\text{cl}(W)$ contains an open disk $D(w_0, \epsilon)$, meaning $W$ is dense in $D(w_0, \epsilon)$. Bob aims to make the graph totally disconnected. He picks $z_1, z_2$ such that $|z_1 - z_2| > 1$. He then kills all roads $z_i z_j$ sequentially.
23: For any pair $(i, j)$, the killing zone $Z_{z_i z_j}$ contains the set $Z'_{z_i z_j} = \{ z_i + (z_j - z_i)w : w \in W \cap D(w_0, \epsilon) \}$, which is dense in the open disk $D_{ij} = D(z_i + (z_j - z_i)w_0, \epsilon |z_j - z_i|)$.
24: Bob can kill roads in batches. Suppose he has cities $z_1, \dots, z_m$. For each $i < m$, he picks a new city $z_{m+k}$ to kill the road $z_i z_m$ by ensuring $z_{m+k} \in Z_{z_i z_m}$. To satisfy the game rules, $z_{m+k}$ must avoid the forbidden set $S = (\bigcup_{n < m+k} D(z_n, 1)) \cup (\bigcup L_{uv})$.
25: The set $S$ is a finite union of closed disks and lines. Its complement $\mathbb{C} \setminus S$ is an open dense set. Since $Z'_{z_i z_j}$ is dense in the open disk $D_{ij}$, the intersection $Z'_{z_i z_j} \cap (\mathbb{C} \setminus S)$ is non-empty. Thus, Bob can always pick $z_{m+k} \in Z_{z_i z_m} \setminus S$. By picking $z_m$ to be sufficiently far from the origin, he ensures that the cities can be placed to satisfy all distance and collinearity constraints.
26: Since every pair of cities $(i, j)$ is eventually killed by some city $z_k$, no roads exist in the final graph. Thus, Alice fails condition (i).
27: 
28: In both cases, Bob has a winning strategy.
