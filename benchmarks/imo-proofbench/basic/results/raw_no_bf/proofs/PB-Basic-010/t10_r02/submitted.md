To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we begin by defining the two sums and simplifying their difference.

Let $n = 1011$. The set $X = \{1, 2, \ldots, 2n\}$ is partitioned into two sets $A$ and $B$ of size $n$ each. We are given:
$S_{AB} = \{ (a, b) \in A \times B : a < b \}$
$S_{BA} = \{ (a, b) \in A \times B : b < a \}$

Let $L$ be the first sum and $R$ be the second sum:
\[ L = \sum_{(a, b) \in S_{AB}} (b - a), \quad R = \sum_{(a, b) \in S_{BA}} (a - b) \]

We examine the difference $L - R$:
\[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (a - b) \]
\[ L - R = \sum_{(a, b) \in S_{AB}} (b - a) + \sum_{(a, b) \in S_{BA}} (b - a) \]

Notice that for any pair $(a, b) \in A \times B$, either $a < b$ or $b < a$ must hold (since $A$ and $B$ are disjoint, $a \neq b$). Therefore, the union of $S_{AB}$ and $S_{BA}$ is exactly the Cartesian product $A \times B$. Thus, we can combine the sums:
\[ L - R = \sum_{(a, b) \in A \times B} (b - a) \]

Using the properties of summation, we expand this as:
\[ L - R = \sum_{a \in A} \sum_{b \in B} (b - a) \]
\[ L - R = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right) \]
\[ L - R = \sum_{a \in A} \left( \sum_{b \in B} b - |B| \cdot a \right) \]
\[ L - R = |A| \left( \sum_{b \in B} b \right) - |B| \left( \sum_{a \in A} a \right) \]

Since $|A| = |B| = n = 1011$, we have:
\[ L - R = n \left( \sum_{b \in B} b - \sum_{a \in A} a \right) \]

For $L$ to equal $R$, it must be that $L - R = 0$, which implies:
\[ n \left( \sum_{b \in B} b - \sum_{a \in A} a \right) = 0 \implies \sum_{b \in B} b = \sum_{a \in A} a \]

Let $S$ be the sum of all elements in $X$:
\[ S = \sum_{k=1}^{2n} k = \frac{2n(2n+1)}{2} = n(2n+1) \]
Substituting $n = 1011$:
\[ S = 1011 \times (2 \times 1011 + 1) = 1011 \times 2023 \]

Since both 1011 and 2023 are odd, their product $S$ is also odd. 
If $\sum_{a \in A} a = \sum_{b \in B} b$, then the total sum $S$ would be:
\[ S = \sum_{a \in A} a + \sum_{b \in B} b = 2 \sum_{a \in A} a \]
This would imply that $S$ is an even number. However, we have already determined that $S$ is odd. This is a contradiction.

Thus, $\sum_{a \in A} a \neq \sum_{b \in B} b$, which means $L - R \neq 0$, and consequently:
\[ \sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b) \]

$\square$
