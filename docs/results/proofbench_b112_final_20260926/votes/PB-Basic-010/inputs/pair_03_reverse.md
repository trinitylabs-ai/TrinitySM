# Problem

The numbers $\{ 1, 2, 3, \ldots , 2022 \}$ are partitioned into two sets $A$ and $B$ of size $1011$ each. Let $S_{AB}$ denote the set of all pairs $(a, b) \in A \times B$ where $a < b$, and let $S_{BA}$ denote the set of all pairs $(a, b) \in A \times B$ where $b < a$.

 Prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$.

# Proof A

1: To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we define the given sets and sums and analyze their relationship.
2: 
3: Let $n = 1011$. The set $X = \{1, 2, 3, \ldots, 2n\}$ is partitioned into two sets $A$ and $B$ such that $|A| = |B| = n$. We are given:
4: - $S_{AB} = \{ (a, b) \in A \times B \mid a < b \}$
5: - $S_{BA} = \{ (a, b) \in A \times B \mid b < a \}$
6: 
7: Let $L$ be the sum over $S_{AB}$ and $R$ be the sum over $S_{BA}$:
8: \[ L = \sum_{(a, b) \in S_{AB}} (b - a), \quad R = \sum_{(a, b) \in S_{BA}} (a - b) \]
9: 
10: Since $A$ and $B$ are a partition of $X$, they are disjoint ($A \cap B = \emptyset$). Thus, for any pair $(a, b) \in A \times B$, it is impossible for $a$ to equal $b$. Consequently, every pair $(a, b) \in A \times B$ must satisfy either $a < b$ or $b < a$. This implies that $S_{AB} \cup S_{BA} = A \times B$ and $S_{AB} \cap S_{BA} = \emptyset$.
11: 
12: We examine the difference $L - R$:
13: \[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (a - b) \]
14: Using the fact that $-(a - b) = b - a$, we can rewrite the second sum:
15: \[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) + \sum_{(a, b) \in S_{BA}} (b - a) \]
16: Since $S_{AB}$ and $S_{BA}$ partition the set $A \times B$, the two sums combine into a single sum over all pairs in $A \times B$:
17: \[ L - R = \sum_{(a, b) \in A \times B} (b - a) \]
18: Expanding this sum, we have:
19: \[ L - R = \sum_{a \in A} \sum_{b \in B} b - \sum_{b \in B} \sum_{a \in A} a \]
20: Let $\Sigma_A = \sum_{a \in A} a$ and $\Sigma_B = \sum_{b \in B} b$. The double sums simplify as follows:
21: \[ L - R = |A| \Sigma_B - |B| \Sigma_A \]
22: Since $|A| = |B| = n = 1011$, we obtain:
23: \[ L - R = n(\Sigma_B - \Sigma_A) \]
24: 
25: The condition $L = R$ holds if and only if $n(\Sigma_B - \Sigma_A) = 0$, which, since $n \neq 0$, requires $\Sigma_A = \Sigma_B$. We check if this equality is possible by calculating the total sum $S$ of the set $X$:
26: \[ S = \Sigma_A + \Sigma_B = \sum_{k=1}^{2022} k = \frac{2022 \times 2023}{2} = 1011 \times 2023 \]
27: Since $1011$ and $2023$ are both odd, their product $S$ is odd. If $\Sigma_A = \Sigma_B$, then $S = 2\Sigma_A$, which would imply that $S$ is even. This is a contradiction. Therefore, $\Sigma_A \neq \Sigma_B$.
28: 
29: Since $n \neq 0$ and $\Sigma_B - \Sigma_A \neq 0$, it follows that $L - R \neq 0$. Thus, we have proven that:
30: \[ \sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b) \]
31: 
32: \(\square\)

# Proof B

1: To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we define the two sums and analyze their difference.
2: 
3: Let $n = 1011$. The set $X = \{1, 2, 3, \ldots, 2n\}$ is partitioned into two sets $A$ and $B$ such that $|A| = |B| = n$. Let $\Sigma_A$ and $\Sigma_B$ denote the sums of the elements of $A$ and $B$, respectively.
4: 
5: Let $L$ and $R$ be the sums defined in the problem:
6: \[ L = \sum_{(a, b) \in S_{AB}} (b - a) = \sum_{\substack{a \in A, b \in B \\ a < b}} (b - a) \]
7: \[ R = \sum_{(a, b) \in S_{BA}} (a - b) = \sum_{\substack{a \in A, b \in B \\ b < a}} (a - b) \]
8: 
9: Consider the difference $L - R$:
10: \[ L - R = \sum_{\substack{a \in A, b \in B \\ a < b}} (b - a) - \sum_{\substack{a \in A, b \in B \\ b < a}} (a - b) \]
11: Since $(a - b) = -(b - a)$, we can rewrite the second term:
12: \[ L - R = \sum_{\substack{a \in A, b \in B \\ a < b}} (b - a) + \sum_{\substack{a \in A, b \in B \\ b < a}} (b - a) \]
13: Because $A$ and $B$ are disjoint, for any pair $(a, b) \in A \times B$, we must have either $a < b$ or $b < a$. Therefore, the two sums together cover all pairs in the Cartesian product $A \times B$:
14: \[ L - R = \sum_{a \in A} \sum_{b \in B} (b - a) \]
15: Expanding the inner sum over $b \in B$:
16: \[ L - R = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right) = \sum_{a \in A} (\Sigma_B - n \cdot a) \]
17: Distributing the summation over $a \in A$:
18: \[ L - R = \sum_{a \in A} \Sigma_B - n \sum_{a \in A} a = n \Sigma_B - n \Sigma_A = n (\Sigma_B - \Sigma_A) \]
19: 
20: We now examine whether $\Sigma_B - \Sigma_A$ can be zero. The sum of all elements in the set $\{1, 2, \ldots, 2n\}$ is given by:
21: \[ \Sigma_A + \Sigma_B = \sum_{k=1}^{2n} k = \frac{2n(2n+1)}{2} = n(2n+1) \]
22: If $L = R$, then $n(\Sigma_B - \Sigma_A) = 0$, which implies $\Sigma_A = \Sigma_B$. If this were true, then:
23: \[ 2\Sigma_A = \Sigma_A + \Sigma_B = n(2n+1) \]
24: Substituting $n = 1011$:
25: \[ n(2n+1) = 1011 \times (2 \times 1011 + 1) = 1011 \times 2023 \]
26: The product of two odd numbers is odd. Thus, $n(2n+1)$ is odd. However, $2\Sigma_A$ must be an even number for any integer $\Sigma_A$. An even number cannot equal an odd number, so $\Sigma_A \neq \Sigma_B$.
27: 
28: Since $\Sigma_B - \Sigma_A \neq 0$ and $n = 1011 \neq 0$, we conclude:
29: \[ L - R = 1011 (\Sigma_B - \Sigma_A) \neq 0 \]
30: Thus, $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$.
31: 
32: \(\square\)
