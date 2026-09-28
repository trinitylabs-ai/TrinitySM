To prove that $\sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b)$, let us define the two sums as $\Sigma_{AB}$ and $\Sigma_{BA}$, respectively.

**1. Analysis of the Sums**
The set $A \times B$ consists of all ordered pairs $(a, b)$ where $a \in A$ and $b \in B$. Since $A$ and $B$ form a partition of $\{1, 2, \ldots, 2022\}$, we have $A \cap B = \emptyset$, which implies $a \neq b$ for all $(a, b) \in A \times B$.
The sets $S_{AB}$ and $S_{BA}$ are defined as:
- $S_{AB} = \{ (a, b) \in A \times B \mid a < b \}$
- $S_{BA} = \{ (a, b) \in A \times B \mid b < a \}$

These two sets partition the Cartesian product $A \times B$ because for any pair $(a, b) \in A \times B$, exactly one of the conditions $a < b$ or $b < a$ must hold.

**2. Algebraic Simplification**
We consider the difference between the two sums:
\[ \Sigma_{AB} - \Sigma_{BA} = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (a - b) \]
Observe that for any pair $(a, b) \in S_{BA}$, we have $b < a$, and thus $a - b = -(b - a)$. Substituting this into the expression:
\[ \Sigma_{AB} - \Sigma_{BA} = \sum_{(a, b) \in S_{AB}} (b - a) - \sum_{(a, b) \in S_{BA}} (-(b - a)) = \sum_{(a, b) \in S_{AB}} (b - a) + \sum_{(a, b) \in S_{BA}} (b - a) \]
Since $S_{AB} \cup S_{BA} = A \times B$, the sum is taken over all possible pairs in $A \times B$:
\[ \Sigma_{AB} - \Sigma_{BA} = \sum_{(a, b) \in A \times B} (b - a) \]
Using the properties of summations over sets, we can expand this as:
\[ \sum_{a \in A} \sum_{b \in B} (b - a) = \sum_{a \in A} \left( \sum_{b \in B} b - \sum_{b \in B} a \right) \]
Let $m = |A| = |B| = 1011$. The inner sum $\sum_{b \in B} a$ is simply $m \cdot a$. Thus:
\[ \Sigma_{AB} - \Sigma_{BA} = \sum_{a \in A} \left( \sum_{b \in B} b \right) - \sum_{a \in A} m a = m \sum_{b \in B} b - m \sum_{a \in A} a = m \left( \sum_{b \in B} b - \sum_{a \in A} a \right) \]

**3. Parity Argument**
To show that $\Sigma_{AB} \neq \Sigma_{BA}$, we must show that $\Sigma_{AB} - \Sigma_{BA} \neq 0$. Since $m = 1011 \neq 0$, this is equivalent to showing that $\sum_{b \in B} b \neq \sum_{a \in A} a$.
Let $S$ be the sum of all elements in the set $\{1, 2, \ldots, 2022\}$:
\[ S = \sum_{i=1}^{2022} i = \frac{2022 \times 2023}{2} = 1011 \times 2023 \]
We know that $\sum_{a \in A} a + \sum_{b \in B} b = S$. If $\sum_{a \in A} a = \sum_{b \in B} b$, then $S$ must be equal to $2 \sum_{a \in A} a$, implying that $S$ is an even number.
However, we check the parity of $S$:
\[ 1011 \equiv 1 \pmod 2 \quad \text{and} \quad 2023 \equiv 1 \pmod 2 \implies S = 1011 \times 2023 \equiv 1 \times 1 = 1 \pmod 2 \]
Since $S$ is odd, it cannot be represented as $2 \sum_{a \in A} a$ for any integer sum. Therefore, $\sum_{b \in B} b \neq \sum_{a \in A} a$.

**Conclusion**
Because $m \neq 0$ and $\sum_{b \in B} b - \sum_{a \in A} a \neq 0$, it follows that $\Sigma_{AB} - \Sigma_{BA} \neq 0$. Thus:
\[ \sum_{(a, b) \in S_{AB}} (b - a) \neq \sum_{(a, b) \in S_{BA}} (a - b) \]
\(\square\)
