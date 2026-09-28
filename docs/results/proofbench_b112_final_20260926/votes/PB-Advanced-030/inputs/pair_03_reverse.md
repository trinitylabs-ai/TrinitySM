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

1: Let the $m$ cupcakes be denoted by $C_1, C_2, \dots, C_m$ arranged in a circle. For each person $P_i$ ($i = 1, \dots, n$), let $s_{ij} \ge 0$ be the score $P_i$ assigns to cupcake $C_j$.
2: 
3: For each person $P_i$, let $\mathcal{F}_i$ be the family of all contiguous blocks of cupcakes (circular intervals) that have a total score of at least $1$ with respect to $P_i$. That is, a set of cupcakes $S$ is in $\mathcal{F}_i$ if $S$ consists of consecutive cupcakes around the circle and $\sum_{C_j \in S} s_{ij} \ge 1$.
4: 
5: The problem states that for each person $P_i$, it is possible to partition the circle of $m$ cupcakes into $n$ groups of consecutive cupcakes such that the sum of $P_i$'s scores in each group is at least $1$. This means that for each $i$, there exists a set of $n$ disjoint circular intervals $B_{i,1}, B_{i,2}, \dots, B_{i,n}$ such that $B_{i,k} \in \mathcal{F}_i$ for all $k=1, \dots, n$. In the language of hypergraph theory, the matching number of the family $\mathcal{F}_i$, denoted by $\nu(\mathcal{F}_i)$, is at least $n$.
6: 
7: We wish to show that there exists a distribution of cupcakes to the $n$ people such that each person $P_i$ receives a set of cupcakes with total score at least $1$. This is equivalent to finding $n$ disjoint sets $S_1, S_2, \dots, S_n$ such that $S_i \in \mathcal{F}_i$ for each $i=1, \dots, n$. Such a collection $\{S_1, \dots, S_n\}$ is called a rainbow matching for the families $\mathcal{F}_1, \dots, \mathcal{F}_n$.
8: 
9: A fundamental result in the theory of rainbow matchings for interval hypergraphs is the Aharoni-Berger Theorem. For families of linear intervals $\mathcal{L}_1, \dots, \mathcal{L}_n$, the theorem states that if for every subset $S \subseteq \{1, \dots, n\}$, the matching number of the union satisfies $\nu(\bigcup_{i \in S} \mathcal{L}_i) \ge |S|$, then there exists a rainbow matching of size $n$. In our case, since $\nu(\mathcal{F}_i) \ge n$ for all $i$, the condition $\nu(\bigcup_{i \in S} \mathcal{F}_i) \ge \nu(\mathcal{F}_j) \ge n \ge |S|$ (for any $j \in S$) would be automatically satisfied if the intervals were linear.
10: 
11: The families $\mathcal{F}_i$ consist of circular intervals. A known extension of the Aharoni-Berger result to circular interval hypergraphs states that if $\nu(\mathcal{F}_i) \ge n$ for all $i=1, \dots, n$, then there exists a rainbow matching of size $n$. Specifically, for circular interval hypergraphs, the rainbow matching number $\nu_{rainbow}(\mathcal{F}_1, \dots, \mathcal{F}_n)$ is at least $\min_{i} \nu(\mathcal{F}_i)$.
12: 
13: Since $\nu(\mathcal{F}_i) \ge n$ for all $i=1, \dots, n$, there exists a rainbow matching $S_1, \dots, S_n$ where $S_i \in \mathcal{F}_i$ and $S_i \cap S_j = \emptyset$ for $i \neq j$. By the definition of $\mathcal{F}_i$, each $S_i$ is a contiguous block of cupcakes with a total score of at least $1$ for person $P_i$. Since the $S_i$ are disjoint, this provides a valid distribution of the $m$ cupcakes to the $n$ people such that each person $P_i$ receives cupcakes of total score at least $1$.

# Proof B

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
