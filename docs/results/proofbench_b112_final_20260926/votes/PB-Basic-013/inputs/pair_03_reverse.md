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

1: To prove that there are two colors that occur together in more than one box, we use a combinatorial counting argument based on the intersections of the sets of colors in each box.
2: 
3: **1. Problem Formalization**
4: Let $B_1, B_2, \dots, B_8$ be the sets of colors contained in the 8 boxes. We are given that each box contains 6 balls of distinct colors, so $|B_i| = 6$ for all $i \in \{1, \dots, 8\}$. The colors are chosen from a set $C$ of 22 available colors, so $B_i \subseteq C$ and $|C| = 22$.
5: 
6: We wish to prove that there exist two distinct colors $c_j, c_k \in C$ and two distinct boxes $B_m, B_n$ such that $\{c_j, c_k\} \subseteq B_m$ and $\{c_j, c_k\} \subseteq B_n$. This is equivalent to proving that there exist $m \neq n$ such that $|B_m \cap B_n| \ge 2$.
7: 
8: **2. Proof by Contradiction**
9: Assume, for the sake of contradiction, that no two colors occur together in more than one box. This means that for any two distinct boxes $B_m$ and $B_n$, they can share at most one color:
10: \[ |B_m \cap B_n| \le 1 \quad \text{for all } 1 \le m < n \le 8 \]
11: Let $S$ be the sum of the sizes of the intersections of all pairs of boxes:
12: \[ S = \sum_{1 \le m < n \le 8} |B_m \cap B_n| \]
13: Given our assumption, and since there are $\binom{8}{2} = 28$ pairs of boxes, we have:
14: \[ S \le \sum_{1 \le m < n \le 8} 1 = \binom{8}{2} = 28 \]
15: 
16: **3. Lower Bound for $S$ via Color Frequencies**
17: We can also calculate $S$ by counting how many pairs of boxes share each color. Let $n_k$ be the number of boxes that contain color $c_k$ for $k = 1, 2, \dots, 22$.
18: Each color $c_k$ is contained in $n_k$ boxes, and thus it contributes $\binom{n_k}{2}$ to the sum $S$. Therefore:
19: \[ S = \sum_{k=1}^{22} \binom{n_k}{2} \]
20: The total number of balls across all boxes is $8 \times 6 = 48$. Since each ball has exactly one color, the sum of the frequencies $n_k$ is:
21: \[ \sum_{k=1}^{22} n_k = 48 \]
22: To find the minimum possible value of $S$, we use the fact that the function $f(n) = \binom{n}{2} = \frac{n(n-1)}{2}$ is convex for $n \ge 0$. For a fixed sum $\sum n_k$, the sum $\sum f(n_k)$ is minimized when the values of $n_k$ are as close to each other as possible.
23: Dividing 48 by 22, we have:
24: \[ 48 = 22 \times 2 + 4 \]
25: The minimum occurs when 4 of the $n_k$ values are 3 and the remaining 18 values are 2. Calculating this minimum:
26: \[ S \ge 4 \binom{3}{2} + 18 \binom{2}{2} = 4(3) + 18(1) = 12 + 18 = 30 \]
27: 
28: **4. Final Contradiction**
29: We have established two bounds for the sum $S$:
30: 1. From the assumption that no two colors occur together in more than one box: $S \le 28$.
31: 2. From the distribution of colors and the convexity of the binomial coefficient: $S \ge 30$.
32: 
33: This yields the inequality $30 \le S \le 28$, which is a contradiction. Thus, the assumption must be false, and there must be at least two colors that occur together in more than one box.
34: 
35: \(\square\)
