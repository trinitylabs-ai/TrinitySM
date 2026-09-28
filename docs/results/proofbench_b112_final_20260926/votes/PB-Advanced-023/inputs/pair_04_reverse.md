# Problem

On a table of size $3002\times3001$, a stone is placed on the leftmost cell of the first row. James and Peter play a game on this table. Peter selects $3000$ cells, under the rule that he must choose one from each row except the first and last rows (i.e., the $1$st and $3002$th row), and there must be at most one selected cell in each column. James knows this rule too, but he doesn't know which cells Peter selected. The goal of James is to move the stone to the last row, avoiding the cells selected by Peter. The stone can only move to adjacent cells on the table. If the stone enters a cell selected by Peter, James receives a penalty of 1 point, and the stone returns to its initial position (i.e., the leftmost cell). Find the smallest positive integer $n$ such that there exists a method for James to achieve his goal before receiving a penalty of $n$ points.

# Proof A

1: Let $k = 3000$. The table size is $(k+2) \times (k+1)$. Peter selects a set $P$ of $k$ cells $P = \{(r, c_r) : r = 2, \dots, k+1\}$, where $c_r \in \{1, \dots, k+1\}$ and all $c_r$ are distinct. James starts at $(1, 1)$ and wins by reaching row $k+2$. A penalty occurs if James enters a cell in $P$, resetting him to $(1, 1)$. We seek the smallest $n$ such that James can guarantee reaching the goal before receiving $n$ penalties.
2: 
3: First, we show that $n = k+1 = 3001$ is sufficient. James can employ a strategy of testing columns sequentially:
4: 1. James attempts to reach the goal by moving along column 1: $(1,1) \to (2,1) \to \dots \to (k+1, 1) \to (k+2, 1)$.
5: 2. If he hits a cell $(r_1, 1)$, he knows $c_{r_1} = 1$. He then attempts to reach the goal along column 2: $(1,1) \to (1,2) \to (2,2) \to \dots \to (k+1, 2) \to (k+2, 2)$. This path is safe at row $r_1$ because $c_{r_1} = 1 \neq 2$.
6: 3. He continues this process for columns $j = 1, 2, \dots, k$. If any path $P_j$ is safe, he reaches the goal.
7: 4. If he hits a cell in each of the first $k$ paths, he has received $k$ penalties and knows $c_{r_1}=1, c_{r_2}=2, \dots, c_{r_k}=k$ for some distinct rows $r_1, \dots, r_k$.
8: 5. Since Peter only selects $k$ cells and $k$ distinct columns are already occupied, the remaining column $k+1$ must be entirely free of selected cells. James then takes the path along column $k+1$, which is guaranteed to be safe.
9: Thus, James reaches the goal with at most $k$ penalties. This means $n=k+1$ is sufficient.
10: 
11: Next, we prove that $n=k+1$ is the smallest such integer by showing that for any strategy James uses, Peter can force at least $k$ penalties. We use an adversarial strategy for Peter. Peter does not fix the set $P$ in advance but maintains a set $S_m$ of all valid configurations consistent with the $m$ penalties James has already incurred.
12: Let $R_{hit}$ and $C_{hit}$ be the sets of rows and columns of the $m$ cells James has hit. $|R_{hit}| = |C_{hit}| = m$. A cell $(r, c)$ is "guaranteed safe" if for all $P \in S_m$, $(r, c) \notin P$.
13: - For $r \in R_{hit}$, the cell $(r, c)$ is guaranteed safe if and only if $c \neq c_r$ (the known penalty column for that row).
14: - For $r \notin R_{hit}$, the cell $(r, c)$ is guaranteed safe if and only if $c \in C_{hit}$. This is because if $c \notin C_{hit}$, Peter can always construct a valid permutation $P \in S_m$ where $(r, c)$ is the selected cell for row $r$, as there are $k-m$ available rows and $(k+1)-m$ available columns.
15: 
16: James wins without further penalties if there exists a path of guaranteed safe cells from row 1 to row $k+2$. Suppose $m < k$. Then there is at least one row $r_{out} \in \{2, \dots, k+1\} \setminus R_{hit}$. In this row, James must be in a column $c \in C_{hit}$ to be safe.
17: To move between two columns $c_i, c_j \in C_{hit}$, James must move horizontally.
18: - If this move occurs in a row $r \notin R_{hit}$, he must stay within $C_{hit}$. If Peter ensures that $C_{hit}$ contains no adjacent columns (which he can do by declaring the first hit cell in a column $c$ to be a penalty if $c$ is adjacent to any column in $C_{hit}$, provided $m < k$), then horizontal moves in $r \notin R_{hit}$ are impossible.
19: - If this move occurs in a row $r \in R_{hit}$, he must avoid $c_r$.
20: 
21: Even if James attempts to make $C_{hit}$ contiguous to facilitate movement, Peter can maintain the consistency of $P$ such that for any $m < k$, no path of guaranteed safe cells exists. Specifically, for $m=1$, $C_{hit} = \{c_1\}$ and $R_{hit} = \{r_1\}$. In any row $r \notin R_{hit}$, only $(r, c_1)$ is safe. In row $r_1$, only $(r_1, c \neq c_1)$ are safe. To move from $(r, c_1)$ to $(r', c_1)$ where $r < r_1 < r'$, James must pass through row $r_1$. To do so, he must either enter $(r_1, c_1)$ (unsafe) or move to some $(r, c)$ with $c \neq c_1$ (unsafe). Thus, for $m=1$, James is blocked. For $1 < m < k$, Peter can similarly ensure that any attempt to switch columns in $R_{hit}$ to avoid a penalty in one row requires passing through a non-guaranteed-safe cell in a row $r \notin R_{hit}$ or hitting another penalty cell.
22: 
23: Thus, James can be forced to receive at least $k$ penalties. The smallest $n$ such that James can reach the goal before receiving $n$ penalties is $n = k+1 = 3001$.

# Proof B

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
