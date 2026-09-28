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

1: To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we define the two sums as $\Sigma_{AB}$ and $\Sigma_{BA}$, respectively.
2: 
3: **1. Decomposition of the Sums**
4: The set $A \times B$ is the set of all ordered pairs $(a, b)$ where $a \in A$ and $b \in B$. Since $A$ and $B$ form a partition of the set $\{1, 2, \ldots, 2022\}$, we have $A \cap B = \emptyset$, which implies that for any $a \in A$ and $b \in B$, $a \neq b$.
5: The sets $S_{AB}$ and $S_{BA}$ are defined as:
6: - $S_{AB} = \{ (a, b) \in A \times B \mid a < b \}$
7: - $S_{BA} = \{ (a, b) \in A \times B \mid b < a \}$
8: 
9: Because every pair $(a, b) \in A \times B$ satisfies either $a < b$ or $b < a$, the sets $S_{AB}$ and $S_{BA}$ partition the set $A \times B$.
10: 
11: **2. Algebraic Manipulation of the Difference**
12: We consider the difference $\Delta = \Sigma_{AB} - \Sigma_{BA}$:
13: \[ \Delta = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (a - b) \]
14: For any pair $(a, b) \in S_{BA}$, we have $b < a$, and thus $a - b = -(b - a)$. Substituting this into the expression for $\Delta$:
15: \[ \Delta = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (-(b - a)) = \sum_{(a, b) \in S_{AB}} (b - a) + \sum_{(a, b) \in S_{BA}} (b - a) \]
16: Since $S_{AB} \cup S_{BA} = A \times B$, we can combine these into a single sum over all pairs in $A \times B$:
17: \[ \Delta = \sum_{(a, b) \in A \times B} (b - a) \]
18: Expanding this double sum over the sets $A$ and $B$:
19: \[ \Delta = \sum_{a \in A} \sum_{b \in B} (b - a) = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right) \]
20: Let $m$ denote the size of sets $A$ and $B$, so $m = 1011$. The inner sum $\sum_{b \in B} a$ is simply $m \cdot a$. Thus:
21: \[ \Delta = \sum_{a \in A} \left( \sum_{b \in B} b - m a \right) = \sum_{a \in A} \left( \sum_{b \in B} b \right) - m \sum_{a \in A} a \]
22: Since $\sum_{b \in B} b$ is a constant with respect to $a$, the first term is $m \sum_{b \in B} b$. Therefore:
23: \[ \Delta = m \sum_{b \in B} b - m \sum_{a \in A} a = m \left( \sum_{b \in B} b - \sum_{a \in A} a \right) \]
24: 
25: **3. Parity Analysis**
26: To prove $\Sigma_{AB} \neq \Sigma_{BA}$, we must show that $\Delta \neq 0$. Since $m = 1011 \neq 0$, $\Delta = 0$ if and only if $\sum_{b \in B} b = \sum_{a \in A} a$.
27: Let $S$ be the sum of all integers from 1 to 2022:
28: \[ S = \sum_{i=1}^{2022} i = \frac{2022 \times 2023}{2} = 1011 \times 2023 \]
29: We know that $\sum_{a \in A} a + \sum_{b \in B} b = S$. If $\sum_{a \in A} a = \sum_{b \in B} b$, then $S = 2 \sum_{a \in A} a$, which implies that $S$ must be an even number.
30: However, we calculate the parity of $S$:
31: \[ S = 1011 \times 2023 \equiv 1 \times 1 = 1 \pmod 2 \]
32: Since $S$ is odd, it cannot be expressed as $2 \sum_{a \in A} a$ for any integer $\sum a$. Thus, $\sum_{b \in B} b \neq \sum_{a \in A} a$.
33: 
34: **Conclusion**
35: Since $m \neq 0$ and $\sum_{b \in B} b - \sum_{a \in A} a \neq 0$, the difference $\Delta$ is non-zero. Thus, $\Sigma_{AB} \neq \Sigma_{BA}$, which proves that:
36: \[ \sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b) \]
37: \(\square\)
