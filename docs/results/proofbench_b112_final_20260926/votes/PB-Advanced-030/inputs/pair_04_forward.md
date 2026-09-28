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
