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
