# Problem

The numbers $\{ 1, 2, 3, \ldots , 2022 \}$ are partitioned into two sets $A$ and $B$ of size $1011$ each. Let $S_{AB}$ denote the set of all pairs $(a, b) \in A \times B$ where $a < b$, and let $S_{BA}$ denote the set of all pairs $(a, b) \in A \times B$ where $b < a$.

 Prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$.

# Proof A

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

# Proof B

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
