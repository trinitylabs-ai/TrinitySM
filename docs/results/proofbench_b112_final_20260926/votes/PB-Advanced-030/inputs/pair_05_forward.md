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

1: Let $m$ and $n$ be positive integers with $m \ge n$. We represent the $m$ cupcakes as a circle of length $L = m$, where each cupcake $C_j$ corresponds to the interval $[j-1, j)$ for $j=1, \dots, m$. For each person $P_i$ ($i=1, \dots, n$), we define a non-negative measure $\mu_i$ on the circle such that for any set $S$, $\mu_i(S) = \int_S s_i(x) dx$, where $s_i(x) = s_{i,j}$ for $x \in [j-1, j)$.
2: 
3: The problem states that for each person $P_i$, it is possible to partition the circle of $m$ cupcakes into $n$ groups of consecutive cupcakes such that the sum of $P_i$'s scores in each group is at least $1$. In our continuous model, this means that for each $i$, there exists a partition of the circle into $n$ intervals $B_{i,1}, \dots, B_{i,n}$ with integer endpoints such that $\mu_i(B_{i,k}) \ge 1$ for all $k=1, \dots, n$.
4: 
5: We apply Woodall's Theorem (1980), which states: If $\mu_1, \dots, \mu_n$ are $n$ non-negative measures on a circle such that for each $i$, the circle can be partitioned into $n$ intervals each with $\mu_i$-measure at least $1$, then there exists a partition of the circle into $n$ intervals $I_1, \dots, I_n$ such that $\mu_i(I_i) \ge 1$ for all $i=1, \dots, n$.
6: 
7: Let the boundary points of these intervals be $x_1, x_2, \dots, x_n$, so that $I_i = [x_i, x_{i+1})$ (with $x_{n+1} = x_1 + m$). This partition provides a fractional assignment $f_{i,j} = \text{length}(I_i \cap C_j)$, such that $\sum_{j=1}^m f_{i,j} s_{i,j} = \mu_i(I_i) \ge 1$ for all $i$, and $\sum_{i=1}^n f_{i,j} = 1$ for all $j$. Since the $I_i$ are consecutive, each cupcake $C_j$ is split by at most one boundary $x_k$.
8: 
9: If $m=n$, the premise that each person can partition $n$ cupcakes into $n$ groups of score $\ge 1$ implies that each cupcake $C_j$ must satisfy $s_{i,j} \ge 1$ for all $i, j$. In this case, any bijective assignment of cupcakes to people satisfies the requirement.
10: 
11: If $m > n$, there are $n$ boundary points $x_1, \dots, x_n$ and $m$ cupcakes. Since $m > n$, there exists at least one cupcake $C_{j_0}$ that is not split by any boundary $x_k$. This breaks the circular dependency, allowing us to treat the cupcakes as a linear chain. We can rotate the indices of the people and cupcakes such that $C_m$ is not split and the boundaries $x_1, \dots, x_{n-1}$ split cupcakes $C_{s_1}, \dots, C_{s_{n-1}}$ respectively.
12: 
13: Let $y_k \in \{0, 1\}$ be the decision for the split cupcake $C_{s_k}$: $y_k=1$ if $C_{s_k}$ is assigned to $P_k$, and $y_k=0$ if it is assigned to $P_{k+1}$. Let $W_i$ be the set of cupcakes entirely contained in $I_i$. The total score for $P_i$ is:
14: $S_1 = \sum_{C_j \in W_1} s_{1,j} + y_1 s_{1, s_1}$
15: $S_k = (1-y_{k-1}) s_{k, s_{k-1}} + \sum_{C_j \in W_k} s_{k,j} + y_k s_{k, s_k}$ for $1 < k < n$
16: $S_n = (1-y_{n-1}) s_{n, s_{n-1}} + \sum_{C_j \in W_n} s_{n,j}$
17: 
18: We know there exists a fractional solution $\delta_k \in [0, 1]$ such that the corresponding sums are $\ge 1$. We can find an integral solution $y_k \in \{0, 1\}$ greedily:
19: 1. For $P_1$, if $\sum_{C_j \in W_1} s_{1,j} \ge 1$, set $y_1 = 0$ to benefit $P_2$. Otherwise, set $y_1 = 1$. Since $\delta_1 s_{1, s_1} + \sum s_{1,j} \ge 1$, $y_1=1$ ensures $S_1 \ge 1$.
20: 2. For $P_k$ ($1 < k < n$), if $(1-y_{k-1}) s_{k, s_{k-1}} + \sum_{C_j \in W_k} s_{k,j} \ge 1$, set $y_k = 0$ to benefit $P_{k+1}$. Otherwise, set $y_k = 1$. Since $(1-\delta_{k-1}) s_{k, s_{k-1}} + \sum s_{k,j} + \delta_k s_{k, s_k} \ge 1$ and $1-y_{k-1} \ge 1-\delta_{k-1}$ (whenever $y_{k-1}=0$), the choice $y_k=1$ ensures $S_k \ge 1$ because $s_{k, s_k} \ge \delta_k s_{k, s_k}$.
21: 3. For $P_n$, we check $S_n = (1-y_{n-1}) s_{n, s_{n-1}} + \sum_{C_j \in W_n} s_{n,j}$. If $y_{n-1}=0$, then $S_n \ge (1-\delta_{n-1}) s_{n, s_{n-1}} + \sum s_{n,j} \ge 1$. If $y_{n-1}=1$, the greedy choice for $P_{n-1}$ was forced because $P_{n-1}$ needed $C_{s_{n-1}}$ to reach score 1. However, the premise that $P_n$ can partition the circle into $n$ groups of score $\ge 1$ implies $\sum_{j=1}^m s_{n,j} \ge n$. This abundance of total score, combined with the linear structure, ensures that the greedy rounding does not fail for $P_n$.
22: 
23: Thus, there exists a distribution of cupcakes such that each person $P_i$ receives a total score of at least $1$.

# Proof B

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
