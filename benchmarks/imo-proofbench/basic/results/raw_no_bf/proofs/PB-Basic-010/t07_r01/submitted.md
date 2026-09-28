To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we start by defining the two sums and analyzing their difference.

Let $n = 1011$. The set $X = \{1, 2, \ldots, 2n\}$ is partitioned into two sets $A$ and $B$, each of size $n$.
The sets of pairs are defined as:
- $S_{AB} = \{ (a, b) \in A \times B \mid a < b \}$
- $S_{BA} = \{ (a, b) \in A \times B \mid b < a \}$

Let $L$ and $R$ denote the two sums:
$$L = \sum_{(a, b) \in S_{AB}} (b - a), \quad R = \sum_{(a, b) \in S_{BA}} (a - b)$$

We calculate the difference $L - R$:
$$L - R = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (a - b)$$
Since $(a - b) = -(b - a)$, the second term can be rewritten as:
$$R = \sum_{(a, b) \in S_{BA}} -(b - a) = - \sum_{(a, b) \in S_{BA}} (b - a)$$
Substituting this back into the expression for $L - R$:
$$L - R = \sum_{(a, b) \in S_{AB}} (b - a) + \sum_{(a, b) \in S_{BA}} (b - a)$$
Because $A \cap B = \emptyset$, for any pair $(a, b) \in A \times B$, it must be that either $a < b$ or $b < a$. Thus, $S_{AB} \cup S_{BA} = A \times B$ and $S_{AB} \cap S_{BA} = \emptyset$. The sum becomes:
$$L - R = \sum_{(a, b) \in A \times B} (b - a)$$
Expanding this double sum:
$$L - R = \sum_{a \in A} \sum_{b \in B} (b - a) = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right)$$
Let $S_A = \sum_{a \in A} a$ and $S_B = \sum_{b \in B} b$. Since $|B| = n$, the inner sum $\sum_{b \in B} a$ is simply $n a$. Thus:
$$L - R = \sum_{a \in A} (S_B - n a) = \sum_{a \in A} S_B - n \sum_{a \in A} a$$
Since $|A| = n$, the first term is $n S_B$:
$$L - R = n S_B - n S_A = n(S_B - S_A)$$
To prove $L \neq R$, we must show that $L - R \neq 0$. Given $n = 1011 \neq 0$, this is equivalent to showing $S_A \neq S_B$.
We know that the sum of all elements in $X$ is:
$$S_A + S_B = \sum_{i=1}^{2n} i = \frac{2n(2n+1)}{2} = n(2n+1)$$
For $n = 1011$:
$$S_A + S_B = 1011 \times (2 \times 1011 + 1) = 1011 \times 2023$$
Since both $1011$ and $2023$ are odd, their product is odd.
If $S_A = S_B$, then $S_A + S_B = 2 S_A$, which would imply that the total sum is even. However, we have established that the total sum is odd. Therefore, $S_A$ cannot equal $S_B$.

Since $S_A \neq S_B$ and $n \neq 0$, it follows that $L - R = n(S_B - S_A) \neq 0$, and thus $L \neq R$.

$\square$
