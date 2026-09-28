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
