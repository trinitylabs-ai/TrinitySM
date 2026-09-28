# Problem

The numbers $\{ 1, 2, 3, \ldots , 2022 \}$ are partitioned into two sets $A$ and $B$ of size $1011$ each. Let $S_{AB}$ denote the set of all pairs $(a, b) \in A \times B$ where $a < b$, and let $S_{BA}$ denote the set of all pairs $(a, b) \in A \times B$ where $b < a$.

 Prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$.

# Proof A

1: To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we define the sums and evaluate their difference.
2: 
3: Let $X = \{ 1, 2, 3, \ldots, 2022 \}$. We are given that $X$ is partitioned into two sets $A$ and $B$ of size $n = 1011$ each. The sets of pairs are defined as:
4: - $S_{AB} = \{ (a, b) \in A \times B : a < b \}$
5: - $S_{BA} = \{ (a, b) \in A \times B : b < a \}$
6: 
7: Let $L = \sum_{(a, b) \in S_{AB}} (b - a)$ and $R = \sum_{(a, b) \in S_{BA}} (a - b)$. We examine the difference $L - R$:
8: \[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (a - b) \]
9: For any pair $(a, b) \in S_{BA}$, we have $b < a$, which means $(a - b) = -(b - a)$. Substituting this into the expression for $R$, we obtain:
10: \[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} -(b - a) = \sum_{(a, b) \in S_{AB}} (b - a) + \sum_{(a, b) \in S_{BA}} (b - a) \]
11: Since $A$ and $B$ are disjoint, for every pair $(a, b) \in A \times B$, either $a < b$ or $b < a$. Thus, the union of $S_{AB}$ and $S_{BA}$ is exactly the Cartesian product $A \times B$. We can therefore write the difference as a double sum over all $a \in A$ and $b \in B$:
12: \[ L - R = \sum_{a \in A} \sum_{b \in B} (b - a) \]
13: We expand the inner sum:
14: \[ L - R = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right) \]
15: Let $\Sigma A = \sum_{a \in A} a$ and $\Sigma B = \sum_{b \in B} b$. Since $|B| = n$, the sum $\sum_{b \in B} a$ is simply $na$. Thus:
16: \[ L - R = \sum_{a \in A} (\Sigma B - na) = \sum_{a \in A} \Sigma B - n \sum_{a \in A} a \]
17: Since $|A| = n$, the first term becomes $n \Sigma B$:
18: \[ L - R = n \Sigma B - n \Sigma A = n (\Sigma B - \Sigma A) \]
19: For $L$ to equal $R$, we must have $n (\Sigma B - \Sigma A) = 0$. Given $n = 1011 \neq 0$, this requires $\Sigma A = \Sigma B$.
20: 
21: We check if $\Sigma A = \Sigma B$ is possible by calculating the total sum of the elements in $X$:
22: \[ \Sigma A + \Sigma B = \sum_{k=1}^{2022} k = \frac{2022 \times 2023}{2} = 1011 \times 2023 \]
23: Both $1011$ and $2023$ are odd integers, and the product of two odd integers is always odd. Thus, $\Sigma A + \Sigma B$ is an odd number.
24: 
25: If $\Sigma A = \Sigma B$, then $\Sigma A + \Sigma B = 2 \Sigma A$, which would mean the total sum must be even. However, we have shown the total sum is odd. This is a contradiction; therefore, $\Sigma A \neq \Sigma B$.
26: 
27: It follows that $\Sigma B - \Sigma A \neq 0$, and consequently $L - R = n (\Sigma B - \Sigma A) \neq 0$. Thus, $L \neq R$.
28: 
29: \(\square\)

# Proof B

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
