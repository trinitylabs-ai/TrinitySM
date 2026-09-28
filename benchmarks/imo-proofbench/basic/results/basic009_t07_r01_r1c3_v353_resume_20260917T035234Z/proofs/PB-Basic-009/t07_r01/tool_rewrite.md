Let $a_1, a_2, \dots, a_{18}$ be 18 real numbers with average $m$. By the definition of the arithmetic mean, we have
$$ \sum_{i=1}^{18} a_i = 18m. $$
Define the centered variables $x_i = a_i - m$ for each $i \in \{1, 2, \dots, 18\}$. Summing these variables yields
$$ \sum_{i=1}^{18} x_i = \sum_{i=1}^{18} (a_i - m) = \sum_{i=1}^{18} a_i - 18m = 18m - 18m = 0. $$
The condition $a_i + a_j + a_k \ge 3m$ for indices $1 \le i < j < k \le 18$ transforms as follows:
$$ (x_i + m) + (x_j + m) + (x_k + m) \ge 3m \iff x_i + x_j + x_k + 3m \ge 3m \iff x_i + x_j + x_k \ge 0. $$
Let $A$ denote the number of triples $\{i, j, k\}$ with $1 \le i < j < k \le 18$ satisfying $x_i + x_j + x_k \ge 0$. We seek the minimum possible value of $A$.

To establish a universal lower bound for $A$, we invoke the following certified result (proof provided in Appendix A):
For any 18 labeled real numbers with nonnegative total sum, at least 136 of their unordered 3-subsets have nonnegative sum.

We now explicitly verify that the hypotheses of this lemma are satisfied by our sequence $x_1, \dots, x_{18}$, and we translate its conclusion back to the original claim.
1. **Input Domain**: The lemma requires 18 labeled real numbers. Our variables $x_1, \dots, x_{18}$ are real by construction, as they are differences of real numbers $a_i$ and $m$.
2. **Sum Guard**: The lemma requires the total sum to be nonnegative. We computed $\sum_{i=1}^{18} x_i = 0$, which satisfies $0 \ge 0$. Thus, the nonnegativity guard holds.
3. **Subset Correspondence**: The lemma counts unordered 3-subsets of the 18 numbers. There is a natural bijection between these subsets and the index triples $1 \le i < j < k \le 18$. The sum of a subset $\{x_i, x_j, x_k\}$ is exactly $x_i + x_j + x_k$.
4. **Conclusion Translation**: The lemma asserts that at least 136 of these 3-subsets have a nonnegative sum. Translating this directly to our count $A$, we obtain $A \ge 136$. This establishes the rigorous lower bound required by the theorem.

Next, we demonstrate that this lower bound is attainable, thereby proving it is the minimum.
Consider the specific configuration:
$$ x_1 = 17, \quad x_i = -1 \text{ for } i = 2, 3, \dots, 18. $$
First, we verify the sum constraint:
$$ \sum_{i=1}^{18} x_i = 17 + \sum_{i=2}^{18} (-1) = 17 + 17(-1) = 0. $$
This configuration corresponds to valid real numbers $a_i = x_i + m$ with average $m$.

We now count the number of triples $\{i, j, k\}$ with $1 \le i < j < k \le 18$ such that $x_i + x_j + x_k \ge 0$. We partition the $\binom{18}{3} = 816$ total triples into two disjoint cases based on membership of the index 1.

**Case 1: Triples containing index 1.**
These triples are of the form $\{1, j, k\}$ with $2 \le j < k \le 18$.
The number of such triples is $\binom{17}{2} = \frac{17 \times 16}{2} = 136$.
For any such triple, the sum is:
$$ x_1 + x_j + x_k = 17 + (-1) + (-1) = 15. $$
Since $15 \ge 0$, all 136 triples in this case satisfy the condition.

**Case 2: Triples not containing index 1.**
These triples are of the form $\{i, j, k\}$ with $2 \le i < j < k \le 18$.
The number of such triples is $\binom{17}{3} = \frac{17 \times 16 \times 15}{6} = 680$.
For any such triple, the sum is:
$$ x_i + x_j + x_k = (-1) + (-1) + (-1) = -3. $$
Since $-3 < 0$, none of the 680 triples in this case satisfy the condition.

Summing the contributions from both cases, the total number of nonnegative-sum triples is:
$$ A = 136 + 0 = 136. $$

Since we have proven $A \ge 136$ for all valid sequences and constructed a sequence achieving $A = 136$, the minimum possible value of $A$ is exactly 136. $\square$

## Checked counting lemma D

For any 18 labeled real numbers with nonnegative total sum, at least 136 of their unordered 3-subsets have nonnegative sum.

Partition the labels into 6 unordered blocks of size 3. Every partition has at least one block of nonnegative sum: otherwise the total would be negative. The number of partitions is T = 18! / ((3!)^6 6!) = 190590400. A fixed block occurs in U = 15! / ((3!)^5 5!) = 1401400 partitions. These formulas follow by ordering all labels, then dividing by the permutations within each block and of the blocks. Count incidences between partitions and their nonnegative blocks. If A is the number of nonnegative blocks, then A U >= T, hence A >= T/U = 136. Labels distinguish equal weights. Blocks of sum zero qualify.
