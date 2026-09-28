# Problem

Each of 8 boxes contains 6 balls. Each ball has been colored with one of 22 colors. If no two balls in the same box are the same color, prove that there are two colors that occur together in more than one box.

# Proof A

1: To prove that there are two colors that occur together in more than one box, we use a double-counting argument and the property of convexity.
2: 
3: **1. Definitions and Notation**
4: Let $n = 8$ be the number of boxes and $k = 6$ be the number of balls in each box. Let $m = 22$ be the total number of colors available. Let $B_1, B_2, \dots, B_8$ be the sets of colors of the balls in each box. Since no two balls in the same box have the same color, each $B_i$ is a set of 6 distinct colors, so $|B_i| = 6$ for all $i \in \{1, \dots, 8\}$.
5: Let $r_c$ be the number of boxes in which color $c$ appears, for $c \in \{1, \dots, 22\}$.
6: 
7: **2. Total Number of Color Occurrences**
8: The total number of balls across all boxes is the sum of the number of times each color appears:
9: \[ \sum_{c=1}^{22} r_c = \sum_{i=1}^{8} |B_i| = 8 \times 6 = 48 \]
10: 
11: **3. Double Counting Pairs of Boxes Sharing a Color**
12: Let $S$ be the sum of the sizes of the intersections of all pairs of boxes:
13: \[ S = \sum_{1 \le i < j \le 8} |B_i \cap B_j| \]
14: We can compute $S$ in two different ways:
15: - **Summing over pairs of boxes:** $S$ is the total number of colors shared by every pair of boxes.
16: - **Summing over colors:** Each color $c$ appears in $r_c$ boxes. This color $c$ contributes exactly $\binom{r_c}{2}$ to the sum $S$, as it is shared by every pair of boxes it belongs to. Thus, $S = \sum_{c=1}^{22} \binom{r_c}{2}$.
17: 
18: **4. Establishing the Lower Bound for $S$**
19: We seek to find the minimum possible value of $S = \sum_{c=1}^{22} \binom{r_c}{2}$ given $\sum_{c=1}^{22} r_c = 48$, where $r_c$ are non-negative integers. The function $f(x) = \binom{x}{2} = \frac{x(x-1)}{2}$ is strictly convex. For a fixed sum, the sum of convex functions is minimized when the variables are as close to each other as possible.
20: Dividing the total occurrences by the number of colors, we have $48 / 22 \approx 2.18$. Thus, the minimum occurs when each $r_c$ is either $\lfloor 48/22 \rfloor = 2$ or $\lceil 48/22 \rceil = 3$.
21: Let $x$ be the number of colors that appear 3 times, and $22-x$ be the number of colors that appear 2 times.
22: \[ 3x + 2(22-x) = 48 \implies x + 44 = 48 \implies x = 4 \]
23: The minimum value of $S$ is therefore:
24: \[ S \ge 4 \binom{3}{2} + 18 \binom{2}{2} = 4(3) + 18(1) = 12 + 18 = 30 \]
25: 
26: **5. Establishing the Upper Bound under the Contradiction Hypothesis**
27: Suppose for the sake of contradiction that no two colors occur together in more than one box. This means that for any two distinct boxes $B_i$ and $B_j$, they share at most one color:
28: \[ |B_i \cap B_j| \le 1 \quad \text{for all } 1 \le i < j \le 8 \]
29: Under this assumption, the sum $S$ is bounded by the total number of pairs of boxes:
30: \[ S = \sum_{1 \le i < j \le 8} |B_i \cap B_j| \le \sum_{1 \le i < j \le 8} 1 = \binom{8}{2} = \frac{8 \times 7}{2} = 28 \]
31: 
32: **6. Final Conclusion**
33: We have shown that $S \ge 30$ based on the total number of balls and colors, but $S \le 28$ if the hypothesis that no two colors occur together in more than one box is true. This is a contradiction, as $30 \le 28$ is false.
34: Therefore, there must exist at least one pair of boxes $B_i, B_j$ such that $|B_i \cap B_j| \ge 2$. This implies that there are at least two colors that occur together in more than one box.
35: 
36: \(\square\)

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
