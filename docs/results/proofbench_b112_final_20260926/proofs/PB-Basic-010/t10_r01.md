To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, we define the two sums and analyze their difference.

Let $n = 1011$. The set $X = \{1, 2, 3, \ldots, 2n\}$ is partitioned into two sets $A$ and $B$ such that $|A| = |B| = n$. Let $\Sigma_A$ and $\Sigma_B$ denote the sums of the elements of $A$ and $B$, respectively.

Let $L$ and $R$ be the sums defined in the problem:
\[ L = \sum_{(a, b) \in S_{AB}} (b - a) = \sum_{\substack{a \in A, b \in B \\ a < b}} (b - a) \]
\[ R = \sum_{(a, b) \in S_{BA}} (a - b) = \sum_{\substack{a \in A, b \in B \\ b < a}} (a - b) \]

Consider the difference $L - R$:
\[ L - R = \sum_{\substack{a \in A, b \in B \\ a < b}} (b - a) - \sum_{\substack{a \in A, b \in B \\ b < a}} (a - b) \]
Since $(a - b) = -(b - a)$, we can rewrite the second term:
\[ L - R = \sum_{\substack{a \in A, b \in B \\ a < b}} (b - a) + \sum_{\substack{a \in A, b \in B \\ b < a}} (b - a) \]
Because $A$ and $B$ are disjoint, for any pair $(a, b) \in A \times B$, we must have either $a < b$ or $b < a$. Therefore, the two sums together cover all pairs in the Cartesian product $A \times B$:
\[ L - R = \sum_{a \in A} \sum_{b \in B} (b - a) \]
Expanding the inner sum over $b \in B$:
\[ L - R = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right) = \sum_{a \in A} (\Sigma_B - n \cdot a) \]
Distributing the summation over $a \in A$:
\[ L - R = \sum_{a \in A} \Sigma_B - n \sum_{a \in A} a = n \Sigma_B - n \Sigma_A = n (\Sigma_B - \Sigma_A) \]

We now examine whether $\Sigma_B - \Sigma_A$ can be zero. The sum of all elements in the set $\{1, 2, \ldots, 2n\}$ is given by:
\[ \Sigma_A + \Sigma_B = \sum_{k=1}^{2n} k = \frac{2n(2n+1)}{2} = n(2n+1) \]
If $L = R$, then $n(\Sigma_B - \Sigma_A) = 0$, which implies $\Sigma_A = \Sigma_B$. If this were true, then:
\[ 2\Sigma_A = \Sigma_A + \Sigma_B = n(2n+1) \]
Substituting $n = 1011$:
\[ n(2n+1) = 1011 \times (2 \times 1011 + 1) = 1011 \times 2023 \]
The product of two odd numbers is odd. Thus, $n(2n+1)$ is odd. However, $2\Sigma_A$ must be an even number for any integer $\Sigma_A$. An even number cannot equal an odd number, so $\Sigma_A \neq \Sigma_B$.

Since $\Sigma_B - \Sigma_A \neq 0$ and $n = 1011 \neq 0$, we conclude:
\[ L - R = 1011 (\Sigma_B - \Sigma_A) \neq 0 \]
Thus, $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$.

\(\square\)
