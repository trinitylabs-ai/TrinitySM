# Problem

On a table of size $3002\times3001$, a stone is placed on the leftmost cell of the first row. James and Peter play a game on this table. Peter selects $3000$ cells, under the rule that he must choose one from each row except the first and last rows (i.e., the $1$st and $3002$th row), and there must be at most one selected cell in each column. James knows this rule too, but he doesn't know which cells Peter selected. The goal of James is to move the stone to the last row, avoiding the cells selected by Peter. The stone can only move to adjacent cells on the table. If the stone enters a cell selected by Peter, James receives a penalty of 1 point, and the stone returns to its initial position (i.e., the leftmost cell). Find the smallest positive integer $n$ such that there exists a method for James to achieve his goal before receiving a penalty of $n$ points.

# Proof A

1: Let $N = 3002$ be the number of rows and $M = 3001$ be the number of columns. Peter selects a set $S$ of $N-2 = 3000$ cells, one per row for $r \in \{2, \dots, N-1\}$, such that each cell is in a distinct column. Let $S = \{(r, c_r) : r = 2, \dots, N-1\}$. Since there are $M$ columns and only $N-2$ selected cells, there is exactly one column $c^*$ that contains no selected cells.
2: 
3: **1. Information from Penalties**
4: When James enters a cell $(r, c) \in S$, he receives a penalty and is reset to $(1, 1)$. He learns that the forbidden cell for row $r$ is $(r, c)$. Because each column contains at most one selected cell, he also knows that for all $r' \neq r$, the cell $(r', c)$ is safe.
5: 
6: **2. Sufficiency of 3 Penalties**
7: James can guarantee reaching the last row $N$ with at most 3 penalties. His strategy is to try columns $1, 2,$ and $3$ sequentially.
8: - He first moves vertically in column 1. If he hits a forbidden cell $(r_1, 1)$, he receives a penalty and is reset.
9: - He then moves vertically in column 2. If he hits a forbidden cell $(r_2, 2)$, he receives a penalty and is reset.
10: - He then moves vertically in column 3. If he hits a forbidden cell $(r_3, 3)$, he receives a penalty and is reset.
11: 
12: If at any point he reaches row $N$ without a penalty, he has succeeded. If he hits penalties in all three columns, he now knows three forbidden cells: $(r_1, 1), (r_2, 2),$ and $(r_3, 3)$. Let these rows be ordered such that $r_1 < r_2 < r_3$. James can now reach row $N$ using the following path:
13: 1. Move $(1, 1) \to (1, 2) \to (2, 2) \to \dots \to (r_1, 2)$. This is safe because $r_2 > r_1$, so no forbidden cell in column 2 occurs at or before row $r_1$.
14: 2. In row $r_1$, move $(r_1, 2) \to (r_1, 3)$. This is safe because the only forbidden cell in row $r_1$ is $(r_1, 1)$.
15: 3. Move $(r_1, 3) \to (r_1+1, 3) \to \dots \to (r_2, 3)$. This is safe because $r_3 > r_2$, so no forbidden cell in column 3 occurs at or before row $r_2$.
16: 4. In row $r_2$, move $(r_2, 3) \to (r_2, 1)$. This is safe if he avoids $(r_2, 2)$. He can move $(r_2, 3) \to (r_2-1, 3) \to (r_2-1, 1) \to (r_2, 1)$. The horizontal move $(r_2-1, 3) \to (r_2-1, 1)$ is safe if $r_2-1 \neq r_1$ and $r_2-1 \neq r_3$. If $r_2-1 = r_1$, he can instead move $(r_2, 3) \to (r_2+1, 3) \to (r_2+1, 1) \to (r_2, 1)$, which is safe if $r_2+1 \neq r_3$ and $r_2+1 \neq r_1$. Since $r_1 < r_2 < r_3$, at least one of these rows is not in $\{r_1, r_3\}$.
17: 5. Move $(r_2, 1) \to (r_2+1, 1) \to \dots \to (r_3, 1)$. This is safe because $r_1 < r_2$.
18: 6. In row $r_3$, move $(r_3, 1) \to (r_3, 2)$. This is safe because the only forbidden cell in row $r_3$ is $(r_3, 3)$.
19: 7. Move $(r_3, 2) \to (r_3+1, 2) \to \dots \to (N, 2)$. This is safe because $r_2 < r_3$.
20: 
21: Thus, 3 penalties are sufficient to guarantee success.
22: 
23: **3. Necessity of 3 Penalties**
24: Peter can force James to incur at least 3 penalties. Suppose James has a strategy. Peter can choose $S$ such that any two columns $c_i, c_j$ James attempts to use are "stuck." For example, if James tries columns 1 and 2, Peter can set $(r, 1) \in S$ and $(r+1, 2) \in S$. To move from row $r$ to $r+2$ using only columns 1 and 2, James must move $(r, 2) \to (r+1, 2)$ (forbidden) or $(r, 2) \to (r, 1) \to (r+1, 1) \to (r+1, 2)$ (forbidden). Thus, James is forced to use a third column. Peter can ensure that any column James tries is not the empty column $c^*$ and that any pair of columns is stuck, forcing a 3rd penalty.
25: 
26: Since James can always succeed with $\le 3$ penalties, but Peter can force 3, the smallest $n$ such that James reaches the goal before $n$ penalties is $n = 3 + 1 = 4$.
27: 
28: The smallest positive integer $n$ is 4.

# Proof B

1: Let $N = 3000$. The table size is $(N+2) \times (N+1)$. Peter selects $N$ cells $S = \{(r, c_r) : r = 2, 3, \dots, N+1\}$, where $c_r \in \{1, \dots, N+1\}$ are distinct. Since there are $N+1$ columns, there is exactly one column $c^* \in \{1, \dots, N+1\}$ that contains no selected cells.
2: 
3: First, we show that James can guarantee reaching the last row after receiving at most $N$ penalties. If James has received penalties in $N$ distinct rows $r \in \{2, \dots, N+1\}$, he knows the blocked cell $(r, c_r)$ for every such row. He can then identify the unique column $c^* \notin \{c_2, \dots, c_{N+1}\}$ and move from $(1, 1) \to (1, c^*) \to (2, c^*) \to \dots \to (N+2, c^*)$. This path is safe because no cell in column $c^*$ is selected. Thus, James can achieve his goal before receiving $n = N+1 = 3001$ penalties.
4: 
5: Next, we show that for any $k < N$, Peter can choose $S$ such that James cannot guarantee reaching the last row. Let Peter's strategy be $c_r = r-1$ for $r = 2, 3, \dots, N+1$. The selected cells are $S = \{(2, 1), (3, 2), \dots, (N+1, N)\}$, and the safe column is $c^* = N+1$.
6: 
7: Let $P \subset \{2, \dots, N+1\}$ be the set of rows where James has hit a penalty, and let $C_P = \{c_r : r \in P\} = \{r-1 : r \in P\}$ be the corresponding set of columns. Let $k = |P|$. If $k < N$, there is at least one row $u \in \{2, \dots, N+1\} \setminus P$ where the blocked cell $(u, c_u)$ is unknown. For any column $c \notin C_P$, the cell $(u, c)$ could potentially be the blocked cell $c_u$. Thus, to guarantee that the stone does not enter a blocked cell in row $u$, James must ensure that every cell he visits in row $u$ is in $C_P$.
8: 
9: Let $P = \{r_1, r_2, \dots, r_k\}$ with $r_1 < r_2 < \dots < r_k$. Let $x_i = r_i-1$, so $C_P = \{x_1, \dots, x_k\}$ with $x_1 < x_2 < \dots < x_k$.
10: To traverse the table, James must use a sequence of columns $c^{(0)}, c^{(1)}, \dots, c^{(k)}$ such that for any unknown row $u$ between $r_i$ and $r_{i+1}$, he stays in column $c^{(i)} \in C_P$. In row $r_i$, he transitions from column $c^{(i-1)}$ to $c^{(i)}$. The path in row $r_i$ is the interval $[\min(c^{(i-1)}, c^{(i)}), \max(c^{(i-1)}, c^{(i)})]$. For this to be safe, it must not contain the blocked cell $c_{r_i} = x_i$. This implies that $c^{(i-1)}$ and $c^{(i)}$ must both be strictly greater than $x_i$ or both strictly less than $x_i$.
11: 
12: We analyze these constraints:
13: 1. For $i=1$, $c^{(0)}$ and $c^{(1)}$ must be on the same side of $x_1$. Since $x_1$ is the minimum of $C_P$, we must have $c^{(0)}, c^{(1)} \in \{x_2, \dots, x_k\}$.
14: 2. For $i=2$, $c^{(1)}$ and $c^{(2)}$ must be on the same side of $x_2$. Since $c^{(1)} \in \{x_2, \dots, x_k\}$ and $c^{(1)} \neq x_2$ (otherwise the interval contains $x_2$), we must have $c^{(1)} > x_2$. Thus, $c^{(2)} > x_2$, meaning $c^{(2)} \in \{x_3, \dots, x_k\}$.
15: 3. By induction, for any $i < k$, we have $c^{(i)} \in \{x_{i+1}, \dots, x_k\}$.
16: 4. For $i=k$, the transition from $c^{(k-1)}$ to $c^{(k)}$ must avoid $x_k$. This requires $c^{(k-1)}$ and $c^{(k)}$ to be on the same side of $x_k$. Since $x_k$ is the maximum of $C_P$, we must have $c^{(k-1)}, c^{(k)} < x_k$.
17: 
18: However, our induction shows that $c^{(k-1)} \in \{x_k\}$, which means $c^{(k-1)} = x_k$. This contradicts the requirement that $c^{(k-1)} < x_k$. If $k=0$, James cannot pass the first unknown row since $C_P$ is empty. Thus, James cannot guarantee success for any $k < N$.
19: 
20: The smallest positive integer $n$ is $N+1 = 3001$.
