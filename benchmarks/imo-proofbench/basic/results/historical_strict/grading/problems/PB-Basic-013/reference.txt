Let’s say a color "connects" two boxes if it appears in both. We want to show there are two colors that connect the same pair of boxes.

 Let $c_i$ denote the number of balls with color $i$. Then, the total number of times a color connects two boxes is $N = \sum_{i=1}^{22} \binom{c_i}{2}$. We also know the total number of balls is $48$, so $\sum_{i=1}^{22} c_i = 48$. We now try to find the minimum possible value of $N$.

 To do this, we first analyze the quantity $X = \sum_{i=1}^{22} (c_i - 2)^2$. If at $|c_i - 2| >= 2$ for some $i$, then clearly $X \ge 4$. Otherwise, all the $c_i$ are 1, 2, or 3. Then, in order for them to sum to 48, at most 18 of them can be 2, so once again $X \ge 4$. We then have

 $4 \le X = 2N - 3 \sum_{i=1}^{22} c_i + 4 * 22 = 2N - 3 * 48 + 4 * 22 = 2N - 56$,

 so that $N \ge 30$. But note that there are only $\binom{8}{2} = 28$ pairs of boxes. Thus, by the pigeonhole principle, some two colors connect the same pair of boxes, as desired.
