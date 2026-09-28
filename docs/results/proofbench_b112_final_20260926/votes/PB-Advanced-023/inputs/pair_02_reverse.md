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
