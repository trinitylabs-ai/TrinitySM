# Problem

Each of 8 boxes contains 6 balls. Each ball has been colored with one of 22 colors. If no two balls in the same box are the same color, prove that there are two colors that occur together in more than one box.

# Proof A

1: To prove that there are two colors that occur together in more than one box, we employ a combinatorial counting argument based on the number of pairs of boxes that share a common color.
2: 
3: **1. Definitions and Notation**
4: Let $n = 8$ be the number of boxes and $k = 6$ be the number of balls in each box. Let $m = 22$ be the total number of available colors. Let $B_1, B_2, \dots, B_8$ denote the sets of colors present in each box. Since no two balls in the same box are the same color, each $B_i$ is a set of $k = 6$ distinct colors chosen from the set of $m = 22$ colors.
5: 
6: We wish to prove that there exist two colors $c_1, c_2$ and two distinct boxes $B_i, B_j$ such that $\{c_1, c_2\} \subseteq B_i$ and $\{c_1, c_2\} \subseteq B_j$. This is logically equivalent to proving that there exist $i \neq j$ such that $|B_i \cap B_j| \ge 2$.
7: 
8: **2. Counting Pairs of Boxes**
9: Suppose, for the sake of contradiction, that no two colors occur together in more than one box. This means that any two distinct boxes share at most one color:
10: $$|B_i \cap B_j| \le 1 \quad \text{for all } 1 \le i < j \le 8.$$
11: Let $S$ be the set of triples $(c, i, j)$ such that color $c$ is present in both box $B_i$ and box $B_j$, where $i < j$. We can determine the size of $S$ in two different ways.
12: 
13: First, we sum over all pairs of boxes. For each pair $\{i, j\}$, the number of colors they share is $|B_i \cap B_j|$. Thus:
14: $$|S| = \sum_{1 \le i < j \le 8} |B_i \cap B_j|$$
15: Given our assumption that $|B_i \cap B_j| \le 1$, and noting that there are $\binom{8}{2} = \frac{8 \times 7}{2} = 28$ pairs of boxes, we have:
16: $$|S| \le \sum_{1 \le i < j \le 8} 1 = 28.$$
17: 
18: Second, we sum over the colors. Let $x_c$ be the number of boxes that contain color $c$ for $c = 1, 2, \dots, 22$. For a fixed color $c$, the number of pairs of boxes that both contain $c$ is $\binom{x_c}{2}$. Thus:
19: $$|S| = \sum_{c=1}^{22} \binom{x_c}{2}$$
20: 
21: **3. Minimizing the Sum of Pairs**
22: The total number of balls across all boxes is $n \times k = 8 \times 6 = 48$. Therefore:
23: $$\sum_{c=1}^{22} x_c = 48$$
24: To find the minimum possible value of $\sum_{c=1}^{22} \binom{x_c}{2}$, we use the fact that the function $f(x) = \binom{x}{2} = \frac{x(x-1)}{2}$ is strictly convex. The sum is minimized when the $x_c$ values are as nearly equal as possible. 
25: Dividing the total balls by the number of colors, we have $48 = 22 \times 2 + 4$. Thus, the sum is minimized when 4 colors appear in 3 boxes and 18 colors appear in 2 boxes. The minimum value is:
26: $$|S| \ge 4 \binom{3}{2} + 18 \binom{2}{2} = 4(3) + 18(1) = 12 + 18 = 30.$$
27: 
28: **4. Conclusion**
29: Comparing the results from our two counting methods, we obtain:
30: $$30 \le |S| \le 28$$
31: This is a contradiction. Therefore, our initial assumption that $|B_i \cap B_j| \le 1$ for all $i < j$ must be false. There must exist at least one pair of boxes $B_i, B_j$ such that $|B_i \cap B_j| \ge 2$, meaning there are at least two colors that occur together in more than one box.
32: 
33: \(\square\)

# Proof B

1: To prove that there are two colors that occur together in more than one box, we will use a counting argument based on the distribution of colors across the boxes.
2: 
3: ### 1. Definitions and Notation
4: Let $B = \{B_1, B_2, \dots, B_8\}$ be the set of 8 boxes. Each box $B_i$ contains 6 balls of distinct colors chosen from a total set of 22 available colors $C = \{c_1, c_2, \dots, c_{22}\}$. We can represent each box as a set of 6 colors, so $|B_i| = 6$ for all $i \in \{1, \dots, 8\}$.
5: 
6: The problem asks us to prove that there exist two distinct colors $c_j, c_k \in C$ and two distinct boxes $B_m, B_n \in B$ such that both colors are present in both boxes. In set notation, this means we must prove there exist $m, n \in \{1, \dots, 8\}$ with $m \neq n$ such that $|B_m \cap B_n| \geq 2$.
7: 
8: ### 2. Double Counting Pairs of Boxes
9: Assume, for the sake of contradiction, that no two colors occur together in more than one box. This implies that for any two distinct boxes $B_m$ and $B_n$, they can share at most one color. That is, $|B_m \cap B_n| \leq 1$ for all $m \neq n$.
10: 
11: Let $x_i$ be the number of boxes in which color $c_i$ appears, for $i = 1, 2, \dots, 22$. The total number of balls across all 8 boxes is:
12: $$\sum_{i=1}^{22} x_i = 8 \times 6 = 48$$
13: 
14: We consider the number of triples $(c_i, \{B_m, B_n\})$, where $m \neq n$ and the color $c_i$ is present in both box $B_m$ and box $B_n$. We can count these triples in two different ways:
15: 
16: **Method A: Summing over colors**
17: For a fixed color $c_i$ that appears in $x_i$ boxes, there are $\binom{x_i}{2}$ pairs of boxes that both contain $c_i$. The total number of such triples $S$ is:
18: $$S = \sum_{i=1}^{22} \binom{x_i}{2}$$
19: 
20: **Method B: Summing over pairs of boxes**
21: For a fixed pair of boxes $\{B_m, B_n\}$, the number of colors they share is exactly $|B_m \cap B_n|$. The total number of such triples $S$ is:
22: $$S = \sum_{1 \le m < n \le 8} |B_m \cap B_n|$$
23: 
24: ### 3. Evaluating the Bounds of $S$
25: From our contradiction hypothesis, we know that $|B_m \cap B_n| \leq 1$ for all $m \neq n$. There are $\binom{8}{2}$ possible pairs of boxes. Therefore:
26: $$S = \sum_{1 \le m < n \le 8} |B_m \cap B_n| \leq \binom{8}{2} \times 1 = \frac{8 \times 7}{2} = 28$$
27: 
28: Now we determine the minimum possible value for $S$ using the color distribution $\sum_{i=1}^{22} x_i = 48$. The function $f(x) = \binom{x}{2} = \frac{x(x-1)}{2}$ is strictly convex for $x \geq 1$. By the properties of convex functions (or Jensen's Inequality), the sum $\sum \binom{x_i}{2}$ is minimized when the $x_i$ values are as nearly equal as possible.
29: 
30: Dividing the total number of balls by the number of colors:
31: $$48 = 22 \times 2 + 4$$
32: The sum is minimized when 4 colors appear in 3 boxes ($x_i = 3$) and 18 colors appear in 2 boxes ($x_i = 2$). Calculating the minimum value:
33: $$S \geq 4 \times \binom{3}{2} + 18 \times \binom{2}{2}$$
34: $$S \geq 4(3) + 18(1) = 12 + 18 = 30$$
35: 
36: ### 4. Conclusion
37: We have derived two bounds for $S$:
38: 1. From the assumption that no two colors occur together in more than one box: $S \leq 28$.
39: 2. From the distribution of balls among colors: $S \geq 30$.
40: 
41: Since it is impossible for $S$ to be both $\leq 28$ and $\geq 30$, our initial assumption must be false. Therefore, there must exist at least two colors that occur together in more than one box.
42: 
43: \(\square\)
