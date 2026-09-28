To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we define the sums and evaluate their difference.

Let $X = \{ 1, 2, 3, \ldots, 2022 \}$. We are given that $X$ is partitioned into two sets $A$ and $B$ of size $n = 1011$ each. The sets of pairs are defined as:
- $S_{AB} = \{ (a, b) \in A \times B : a < b \}$
- $S_{BA} = \{ (a, b) \in A \times B : b < a \}$

Let $L = \sum_{(a, b) \in S_{AB}} (b - a)$ and $R = \sum_{(a, b) \in S_{BA}} (a - b)$. We examine the difference $L - R$:
\[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (a - b) \]
For any pair $(a, b) \in S_{BA}$, we have $b < a$, which means $(a - b) = -(b - a)$. Substituting this into the expression for $R$, we obtain:
\[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} -(b - a) = \sum_{(a, b) \in S_{AB}} (b - a) + \sum_{(a, b) \in S_{BA}} (b - a) \]
Since $A$ and $B$ are disjoint, for every pair $(a, b) \in A \times B$, either $a < b$ or $b < a$. Thus, the union of $S_{AB}$ and $S_{BA}$ is exactly the Cartesian product $A \times B$. We can therefore write the difference as a double sum over all $a \in A$ and $b \in B$:
\[ L - R = \sum_{a \in A} \sum_{b \in B} (b - a) \]
We expand the inner sum:
\[ L - R = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right) \]
Let $\Sigma A = \sum_{a \in A} a$ and $\Sigma B = \sum_{b \in B} b$. Since $|B| = n$, the sum $\sum_{b \in B} a$ is simply $na$. Thus:
\[ L - R = \sum_{a \in A} (\Sigma B - na) = \sum_{a \in A} \Sigma B - n \sum_{a \in A} a \]
Since $|A| = n$, the first term becomes $n \Sigma B$:
\[ L - R = n \Sigma B - n \Sigma A = n (\Sigma B - \Sigma A) \]
For $L$ to equal $R$, we must have $n (\Sigma B - \Sigma A) = 0$. Given $n = 1011 \neq 0$, this requires $\Sigma A = \Sigma B$.

We check if $\Sigma A = \Sigma B$ is possible by calculating the total sum of the elements in $X$:
\[ \Sigma A + \Sigma B = \sum_{k=1}^{2022} k = \frac{2022 \times 2023}{2} = 1011 \times 2023 \]
Both $1011$ and $2023$ are odd integers, and the product of two odd integers is always odd. Thus, $\Sigma A + \Sigma B$ is an odd number.

If $\Sigma A = \Sigma B$, then $\Sigma A + \Sigma B = 2 \Sigma A$, which would mean the total sum must be even. However, we have shown the total sum is odd. This is a contradiction; therefore, $\Sigma A \neq \Sigma B$.

It follows that $\Sigma B - \Sigma A \neq 0$, and consequently $L - R = n (\Sigma B - \Sigma A) \neq 0$. Thus, $L \neq R$.

\(\square\)
