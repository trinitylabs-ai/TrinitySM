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

# Proof B

1: Let the points $P, Q, R$ and the cities $A, B, C$ be represented by complex numbers $p, q, r, a, b, c$. The condition that $\triangle PQR$ is directly similar to $\triangle ABC$ is equivalent to $\frac{r-p}{q-p} = \frac{c-a}{b-a}$. Let $L = \{ \frac{r-p}{q-p} : r \in S \}$ be the set of ratios associated with Alice's choice of $S$. Then $\triangle PQR$ is directly similar to $\triangle ABC$ if and only if $\frac{c-a}{b-a} \in L$. Similarly, $\triangle PQR$ is directly similar to $\triangle BAC$ if and only if $\frac{c-b}{a-b} \in L$. Note that $\frac{c-b}{a-b} = \frac{c-a+a-b}{a-b} = 1 - \frac{c-a}{b-a}$. Let $L' = L \cup (1-L)$. A road $AB$ exists if and only if for every city $C \notin \{A, B\}$, $\frac{c-a}{b-a} \in L'$. Let $F = \mathbb{C} \setminus L'$. A road $AB$ is "killed" if there exists at least one city $C \notin \{A, B\}$ such that $\frac{c-a}{b-a} \in F$.
2: 
3: Bob wins if the resulting graph is either disconnected or non-planar. We analyze the properties of the set $F$.
4: 
5: Case 1: $F$ has a non-empty interior.
6: Let $U \subset F$ be an open disk. Bob can make the graph disconnected by isolating city $v_1$.
7: 1. Bob picks $v_1$ and $v_2$ such that $d(v_1, v_2) > 1$.
8: 2. Bob picks $v_3$ such that $\frac{v_3 - v_1}{v_2 - v_1} \in U$. This kills the road $v_1 v_2$.
9: 3. For $n \ge 3$, Bob picks $v_{n+1}$ such that $\frac{v_{n+1} - v_1}{v_n - v_1} \in U$. This is equivalent to $v_{n+1} \in v_1 + (v_n - v_1)U$.
10: Since $U$ is an open disk, $v_1 + (v_n - v_1)U$ is also an open disk. Bob can pick $v_{n+1}$ from this disk to ensure $d(v_{n+1}, v_k) > 1$ for all $k \le n$ and to ensure that no three cities are collinear.
11: Under this construction, for every $n \ge 2$, the road $v_1 v_n$ is killed by city $v_{n+1}$ (or $v_3$ for $n=2$). Thus, $v_1$ is not connected to any other city, making the graph disconnected. Bob wins.
12: 
13: Case 2: $F$ has no interior.
14: Subcase 2a: $F$ is dense in $\mathbb{C}$.
15: Bob can kill all roads. He orders all pairs of cities $\{v_i, v_j\}$ as $e_1, e_2, \dots$. He picks cities $v_n$ inductively. At step $n$, Bob identifies the first road $e_k = \{v_i, v_j\}$ in the list that has not yet been killed (where $i, j < n$). He picks $v_n$ such that $\frac{v_n - v_i}{v_j - v_i} \in F$. Since $F$ is dense, the set $v_i + F(v_j - v_i)$ is dense in $\mathbb{C}$. Bob can pick $v_n$ from this set to satisfy $d(v_n, v_k) > 1$ for all $k < n$ and to avoid collinearity. Since every pair $\{v_i, v_j\}$ eventually appears in the list, every road is killed. The resulting graph has no roads and is thus disconnected. Bob wins.
16: 
17: Subcase 2b: $F$ is not dense.
18: Bob can construct a graph $K_\infty$, which is non-planar. He picks cities $v_n$ inductively. For $n=1, 2$, he picks $v_1, v_2$ such that $d(v_1, v_2) > 1$. For $n \ge 3$, Bob must pick $v_n$ such that:
19: (i) $d(v_n, v_k) > 1$ for all $k < n$.
20: (ii) No three cities are collinear.
21: (iii) For all $i, j < n$, the road $v_i v_j$ is not killed by $v_n$: $\frac{v_n - v_i}{v_j - v_i} \notin F$.
22: (iv) For all $i, k < n$ ($i \neq k$), the road $v_i v_n$ is not killed by $v_k$: $\frac{v_k - v_i}{v_n - v_i} \notin F$.
23: 
24: The forbidden sets for $v_n$ are:
25: - Disks $D(v_k, 1)$ and lines $\text{Line}(v_i, v_k)$.
26: - Sets $S_{i,j} = \{ z : \frac{z - v_i}{v_j - v_i} \in F \} = v_i + F(v_j - v_i)$.
27: - Sets $T_{i,k} = \{ z : \frac{v_k - v_i}{z - v_i} \in F \}$.
28: 
29: Since $F$ has no interior, any scaled and translated copy $S_{i,j}$ also has no interior. The map $f(z) = \frac{v_k - v_i}{z - v_i}$ is a Möbius transformation, which is a homeomorphism of the Riemann sphere. Since $F$ has no interior in $\mathbb{C}$, the preimage $T_{i,k} = f^{-1}(F)$ also has no interior in $\mathbb{C}$. A finite union of sets with no interior cannot be the entire plane $\mathbb{C}$. Thus, Bob can always pick $v_n$ to avoid all these sets.
30: The resulting graph is $K_\infty$ because no road is ever killed. Since $K_\infty$ is non-planar, Bob wins.
31: 
32: In all cases, Bob has a winning strategy.
