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
