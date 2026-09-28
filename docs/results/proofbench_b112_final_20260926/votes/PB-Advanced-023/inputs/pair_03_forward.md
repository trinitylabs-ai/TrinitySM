# Problem

On a table of size $3002\times3001$, a stone is placed on the leftmost cell of the first row. James and Peter play a game on this table. Peter selects $3000$ cells, under the rule that he must choose one from each row except the first and last rows (i.e., the $1$st and $3002$th row), and there must be at most one selected cell in each column. James knows this rule too, but he doesn't know which cells Peter selected. The goal of James is to move the stone to the last row, avoiding the cells selected by Peter. The stone can only move to adjacent cells on the table. If the stone enters a cell selected by Peter, James receives a penalty of 1 point, and the stone returns to its initial position (i.e., the leftmost cell). Find the smallest positive integer $n$ such that there exists a method for James to achieve his goal before receiving a penalty of $n$ points.

# Proof A

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
