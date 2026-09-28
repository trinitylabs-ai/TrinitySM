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
