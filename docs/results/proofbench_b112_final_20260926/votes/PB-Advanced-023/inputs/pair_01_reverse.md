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

1: Let $m = 3001$. The table has dimensions $(m+1) \times m$. Peter selects a set $S$ of $m-1$ cells $\{(r, c_r) : r = 2, \dots, m\}$ such that each row $R_2, \dots, R_m$ contains exactly one selected cell and each column $C_1, \dots, C_m$ contains at most one selected cell. This implies that exactly one column $j^* \in \{1, \dots, m\}$ contains no selected cells.
2: 
3: **1. Upper Bound for $n$**
4: James can employ a strategy of testing columns one by one. For $j = 1, 2, \dots, m$, James moves the stone from $(1, j)$ down to $(m+1, j)$. If column $j$ is the empty column $j^*$, he reaches the last row without further penalties. If column $j$ is not empty, he will eventually enter a cell $(r, j) \in S$, receive a penalty of 1 point, and be reset to $(1, 1)$. Since there are $m$ columns and at least one is empty, James will encounter at most $m-1$ obstacles before finding $j^*$. Thus, he can guarantee reaching the last row with at most $m-1 = 3000$ penalties. This implies that $n \le 3001$, as he succeeds before receiving 3001 points.
5: 
6: **2. Lower Bound for $n$**
7: We show that Peter can force James to receive at least $m-1$ penalties. We use an adversary argument. Let $S_{known}$ be the set of cells in $S$ that James has already encountered. Let $k = |S_{known}|$ be the number of penalties received. Let $R_{known}$ and $C_{known}$ be the sets of rows and columns associated with $S_{known}$, respectively. Let $R_{unc} = \{2, \dots, m\} \setminus R_{known}$ and $C_{unc} = \{1, \dots, m\} \setminus C_{known}$.
8: 
9: A cell $(r, c)$ is "proven safe" if it cannot be in $S$ for any configuration consistent with $S_{known}$.
10: - If $r=1$ or $r=m+1$, $(r, c)$ is always safe.
11: - If $r \in R_{known}$, $(r, c)$ is safe if and only if $(r, c) \notin S_{known}$.
12: - If $r \in R_{unc}$, $(r, c)$ is safe if and only if $c \in C_{known}$. (If $c \in C_{unc}$, Peter can consistently place the obstacle for row $r$ at column $c$ because $|C_{unc}| = m-k \ge |R_{unc}| = m-1-k$).
13: 
14: To reach the last row without further penalties, James must follow a path of proven safe cells. Suppose $k < m-1$. Then $R_{unc}$ is non-empty. To cross any row $r \in R_{unc}$, James must be in some column $c \in C_{known}$.
15: However, every column $c \in C_{known}$ contains exactly one obstacle $(r_c, c) \in S_{known}$. To bypass this obstacle, James must switch to another column $c' \in C_{known} \cup C_{unc}$ in some row $r'$.
16: - If $r' \in R_{unc}$, he must be in $C_{known}$, and the switch is safe only if all columns between $c$ and $c'$ are also in $C_{known}$.
17: - If $r' \in R_{known}$, say $r'=r_p$, the switch is safe only if $c_p$ is not between $c$ and $c'$.
18: - If $r' \in \{1, m+1\}$, the switch is always safe.
19: 
20: Peter's adversary strategy is to maintain $S_{known}$ such that $C_{known}$ is non-contiguous (e.g., by picking $c \in C_{unc}$ such that no two selected columns are adjacent). This makes switches in $R_{unc}$ impossible. Furthermore, Peter can ensure that for any $c, c' \in C_{known}$, any row $r_p \in R_{known}$ that could allow a switch is blocked by placing $c_p$ between $c$ and $c'$. Finally, while switches in $R_1$ are possible, James can only use them to enter a column $c \in C_{known}$ before hitting its obstacle $r_c$. Once he is below $r_c$, he cannot return to $R_1$ using column $c$ without passing through $r_c$.
21: 
22: Since James must cross all rows in $R_{unc}$ using $C_{known}$ and cannot safely transition between columns to avoid the obstacles in $R_{known}$, he cannot guarantee a safe path until $R_{unc}$ is empty, which requires $k = m-1$ penalties.
23: 
24: **3. Conclusion**
25: James can guarantee success with $m-1 = 3000$ penalties, but Peter can force him to receive $m-1$ penalties. Thus, the smallest $n$ such that James can guarantee success before receiving $n$ points is $n = 3000 + 1 = 3001$.
