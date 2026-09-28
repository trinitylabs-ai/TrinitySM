Let $X = \sum_{(a, b) \in S_{AB}} (b - a)$, $Y=\sum_{(a, b) \in S_{BA}} (a -b)$ and $Z=X-Y$. We first analyze the case where all elements of $A$ are smaller than all elements of $B$. In that case, $S_{BA} = 0$, and
 \[ X = \sum_{i = 1012}^{2022} \sum_{j = 1}^{1011} (i - j) = 1011 \cdot \left(\sum_{i = 1012}^{2022} i - \sum_{j = 1}^{1011} j \right) = 1011^3, \]
 and so $Z = 1011^3$.

 Now, arrange the numbers $1$ to $2022$ on a line in increasing order from left to right, and consider how the quantity $Z$ changes if we swap the set of two adjacent numbers, where the left number is in $A$ and the right number is in $B$. Let $A_l$ and $B_l$ be the number of numbers from $A$ and $B$ to the left of this adjacent pair, and similarly let $A_r$ and $B_r$ be the number of numbers from $A$ and $B$ to the right of this adjacent pair,

 First think of how $X$ changes. By moving the number from $A$ one unit to the right, we decrease each $A$-$B$ segment of $B_r$ by one unit. By moving the number from $B$ one unit to the left, we shorten each $A$-$B$ segments of $A_l$ by one unit. Also, we eliminated the length-1 $A$-$B$ segment formed by the swapped points themselves. Thus, $X$ decreases by $B_r + A_l + 1$.

 Similarly, $Y$ increases by $A_r + B_l + 1$, after the swap. Thus, $Z$ decreases by $B_r + R_l + B_r + B_l + 2 = 2022$.

 Now, starting from the initial configuration where all the 1011 left-most points are $A$, we can reach any other configuration by a series of swaps of adjacent pairs, where the left number is $A$ and the right number is $B$. In the initial configuration, we have $Z = 1011^3$, and it decreases by $2022$ with each swap. Thus, $Z$ always remains an odd number, so it can never be zero. We conclude that $X \neq Y$.
