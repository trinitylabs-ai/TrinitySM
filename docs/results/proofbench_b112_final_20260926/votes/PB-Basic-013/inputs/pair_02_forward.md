# Problem

Each of 8 boxes contains 6 balls. Each ball has been colored with one of 22 colors. If no two balls in the same box are the same color, prove that there are two colors that occur together in more than one box.

# Proof A

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
