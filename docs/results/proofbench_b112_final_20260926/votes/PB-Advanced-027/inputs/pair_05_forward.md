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
