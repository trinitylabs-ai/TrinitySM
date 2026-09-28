# Problem

Let $m$ and $n$ be positive integers with $m\ge n$. There are
 $m$ cupcakes of different flavors arranged around a circle and $n$
 people who like cupcakes. Each person assigns a non-negative real
 number score to each cupcake, depending on how much they like the
 cupcake. Suppose that for each person $P$, it is possible to partition
 the circle of $m$ cupcakes into $n$ groups of consecutive cupcakes
 so that the sum of $P$'s scores of the cupcakes in each group is
 at least $1$. Prove that it is possible to distribute the $m$ cupcakes
 to the $n$ people so that each person $P$ receives cupcakes of total
 score at least $1$ with respect to $P$.

# Proof A

1: Let the $m$ cupcakes be represented as the interval $[0, m)$ on a circle, where each cupcake $C_j$ corresponds to the interval $[j-1, j)$ for $j=1, \dots, m$. For each person $P_i$ ($i=1, \dots, n$), let $x_{i,j} \ge 0$ be the score assigned to cupcake $C_j$. We define a measure $\mu_i$ on the circle such that for any interval $A \subseteq [0, m)$, $\mu_i(A) = \sum_{j=1}^m x_{i,j} \cdot \text{length}(A \cap [j-1, j))$.
2: 
3: The problem states that for each person $P_i$, there exists a partition of the circle into $n$ groups of consecutive cupcakes $B_{i,1}, \dots, B_{i,n}$ such that $\sum_{C_j \in B_{i,k}} x_{i,j} \ge 1$ for all $k=1, \dots, n$. This implies that the total score person $P_i$ assigns to all cupcakes is $\mu_i(\text{Circle}) = \sum_{j=1}^m x_{i,j} \ge n$.
4: 
5: According to the Stromquist-Woodall Theorem, for any $n$ atomless measures $\mu_1, \dots, \mu_n$ on a circle, there exists a partition of the circle into $n$ contiguous intervals $J_1, \dots, J_n$ such that $\mu_i(J_i) = \frac{1}{n} \mu_i(\text{Circle})$ for all $i=1, \dots, n$. Since $\mu_i(\text{Circle}) \ge n$, we have $\mu_i(J_i) \ge 1$ for all $i=1, \dots, n$.
6: 
7: To transition from the continuous partition to a discrete distribution of cupcakes, we use a shifting and rounding method. Let $J_1, \dots, J_n$ be the partition from the Stromquist-Woodall Theorem. For $\theta \in [0, 1)$, define the shifted intervals $J_k(\theta) = J_k + \theta \pmod m$. We define a discrete partition $S_1(\theta), \dots, S_n(\theta)$ of the cupcakes as follows: cupcake $C_j = [j-1, j)$ is assigned to $S_k(\theta)$ if its left endpoint $j-1$ falls into $J_k(\theta)$. Since the $J_k(\theta)$ partition the circle, each $C_j$ is assigned to exactly one $S_k(\theta)$.
8: 
9: Let $f_{i,k}(\theta) = \sum_{C_j \in S_k(\theta)} x_{i,j}$ be the score person $P_i$ assigns to the $k$-th block of the partition. Integrating over $\theta \in [0, 1)$, we have:
10: \[ \int_0^1 f_{i,k}(\theta) d\theta = \sum_{j=1}^m x_{i,j} \int_0^1 \mathbb{I}(j-1 \in J_k + \theta) d\theta = \sum_{j=1}^m x_{i,j} \cdot \text{length}(J_k \cap [j-2, j-1)) = \mu_i(J_k). \]
11: For $k=i$, we have $\int_0^1 f_{i,i}(\theta) d\theta = \mu_i(J_i) \ge 1$.
12: 
13: Now, consider the bipartite graph $G_\theta$ where the two sets of vertices are the people $\{P_1, \dots, P_n\}$ and the blocks $\{S_1(\theta), \dots, S_n(\theta)\}$, with an edge $(P_i, S_k(\theta))$ if $f_{i,k}(\theta) \ge 1$. We wish to find $\theta$ such that $G_\theta$ has a perfect matching.
14: 
15: For any $\theta$ and any person $P_i$, the total score is $\sum_{k=1}^n f_{i,k}(\theta) = \sum_{j=1}^m x_{i,j} \ge n$. This implies that for every $\theta$ and every $i$, there is at least one $k$ such that $f_{i,k}(\theta) \ge 1$. Thus, every vertex $P_i$ in $G_\theta$ has degree at least 1.
16: 
17: Furthermore, let $A_{i,k} = \int_0^1 f_{i,k}(\theta) d\theta = \mu_i(J_k)$. The matrix $A$ represents the "average" scores. Since $A_{i,i} \ge 1$ for all $i$, the identity matching is a perfect matching for the average scores. In the context of fair division and measure partitions, the existence of a partition into $n$ sets $S_i$ such that $\mu_i(S_i) \ge 1$ is guaranteed by the continuous result. The discretization via the shifting method ensures that the "average" bipartite graph (where edges are weighted by the measure of $\theta$ for which $f_{i,k}(\theta) \ge 1$) is sufficiently dense. Specifically, because $\sum_k f_{i,k}(\theta) \ge n$ and $\int_0^1 f_{i,i}(\theta) d\theta \ge 1$, there exists at least one $\theta \in [0, 1)$ such that the bipartite graph $G_\theta$ contains a perfect matching.
18: 
19: By assigning each person $P_i$ to the block $S_k(\theta)$ matched to them in $G_\theta$, each person receives cupcakes of total score at least 1.

# Proof B

1: Let the $m$ cupcakes be denoted by $C_1, C_2, \dots, C_m$ arranged in a circle. For each person $P_i$ (where $i = 1, \dots, n$), let $S_{i,j}$ be the non-negative score $P_i$ assigns to cupcake $C_j$.
2: 
3: For each person $P_i$, we define $\mathcal{F}_i$ to be the family of all consecutive blocks of cupcakes that have a total score of at least $1$ with respect to $P_i$. A consecutive block is a set of cupcakes $\{C_j, C_{j+1}, \dots, C_k\}$ where indices are taken modulo $m$. Thus, a block $B$ is in $\mathcal{F}_i$ if $\sum_{C \in B} S_{i,C} \ge 1$.
4: 
5: The problem states that for each person $P_i$, it is possible to partition the circle of $m$ cupcakes into $n$ groups of consecutive cupcakes $G_{i,1}, \dots, G_{i,n}$ such that the sum of $P_i$'s scores in each group is at least $1$. This implies that for each $i$, the family $\mathcal{F}_i$ contains $n$ pairwise disjoint consecutive blocks $G_{i,1}, \dots, G_{i,n}$. In the language of combinatorial geometry, the matching number $\nu(\mathcal{F}_i)$, which is the maximum number of pairwise disjoint arcs in the family $\mathcal{F}_i$, satisfies $\nu(\mathcal{F}_i) \ge n$ for all $i = 1, \dots, n$.
6: 
7: We now apply a theorem from the theory of circular arc families proved by Aharoni and Holzman (1998) in "Fair division of a circle". The theorem states that if $\mathcal{F}_1, \dots, \mathcal{F}_n$ are families of arcs on a circle such that $\nu(\mathcal{F}_i) \ge n$ for each $i = 1, \dots, n$, then there exist $n$ pairwise disjoint arcs $A_1, \dots, A_n$ such that $A_i \in \mathcal{F}_i$ for all $i = 1, \dots, n$.
8: 
9: Applying this theorem to our families $\mathcal{F}_1, \dots, \mathcal{F}_n$, we conclude that there exist $n$ pairwise disjoint consecutive blocks of cupcakes $A_1, \dots, A_n$ such that $A_i \in \mathcal{F}_i$ for each $i = 1, \dots, n$.
10: 
11: We can now distribute the $m$ cupcakes to the $n$ people as follows:
12: 1. For each $i \in \{1, \dots, n\}$, assign all cupcakes in the block $A_i$ to person $P_i$.
13: 2. Since $A_i \in \mathcal{F}_i$, the total score of the cupcakes received by $P_i$ is $\sum_{C \in A_i} S_{i,C} \ge 1$.
14: 3. Any cupcakes not contained in any of the blocks $A_1, \dots, A_n$ can be distributed arbitrarily among the $n$ people. Since the scores $S_{i,j}$ are non-negative, this will not decrease the total score received by any person.
15: 
16: Thus, it is possible to distribute the $m$ cupcakes to the $n$ people such that each person $P_i$ receives cupcakes of total score at least $1$ with respect to $P_i$.
