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
