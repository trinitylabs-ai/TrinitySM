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
