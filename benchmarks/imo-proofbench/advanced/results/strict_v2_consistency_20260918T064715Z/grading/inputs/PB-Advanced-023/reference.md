First we demonstrate that there is no winning strategy if James has
 2 attempts.


 Suppose that $(2,i)$ is the first cell in the second row that James
 reaches on his first attempt. Peter could have selected this cell,
 in which case James receives a penalty and returns to the initial
 position, and he cannot have reached any other cells past the first
 row.


 Next, suppose that $(3,j)$ is the first cell in the third row that
 James reaches on his second attempt. James must have moved to this
 cell from $(2,j)$, so we know $j\neq i$. So it is possible that
 Peter selected the cell $(3,j)$, in which case James also receives
 a penalty and returns to the initial position on his second attempt.
 Therefore James cannot guarantee to reach the last row in 2 attempts.


 Next, we exhibit a strategy for $n=3$. On the first attempt, James
 travels along the path

 \[
 (1,1)\rightarrow(2,1)\rightarrow(2,2)\rightarrow\cdots\rightarrow(2,3001).
 \]

 This path meets every cell in the second row, so James will find the
 selected cell in row 2, receive a penalty, and return to the initial
 position.


 If the selected cell in the second row is not on the edge of the board
 (that is, it is in cell $(2,i)$ with $2\leq i\leq3000$ ), then James
 takes the following two paths in his second and third attempts:

 \[
 \begin{aligned} & (1,1)\rightarrow\dots\rightarrow(1,i-1)\rightarrow(2,i-1)\rightarrow(3,i-1)\rightarrow(3,i)\rightarrow(4,i)\rightarrow\cdots\rightarrow(3002,i).

  & (1,1)\rightarrow\dots\rightarrow(1,i+1)\rightarrow(2,i+1)\rightarrow(3,i+1)\rightarrow(3,i)\rightarrow(4,i)\rightarrow\cdots\rightarrow(3002,i).
 \end{aligned}
 \]

 The only cells that Peter might have selected in either of these paths
 are $(3,i-1)$ and $(3,i+1)$. At most one of these can have been
 selected by Peter, so at least one of the two paths will be successful.
 James starts each path from the initial position $(1,1)$, but he
 knows where the selected cell in row 2 is, so he can navigate to $(1,i-1)$
 or $(1,i+1)$ directly.


 If the selected cell in the second row is on the edge of the board,
 without loss of generality we may assume it is in $(2,1)$. Then,
 on the second attempt, James takes the following path:

 \[
 (1,1)\rightarrow(1,2)\rightarrow(2,2)\rightarrow(2,3)\rightarrow(3,3)\rightarrow\cdots\rightarrow(3000,3001)\rightarrow(3001,3001)\rightarrow(3002,3001).
 \]

 If none of the cells on this path were selected by Peter, then James
 wins. Otherwise, let $(i,j)$ be the first cell on which James encounters
 a selected cell. We have that $j=i$ or $j=i+1$. Then, on the third
 attempt, James takes the following path:

 \[
 \begin{aligned}(1,1)\rightarrow\dots\rightarrow(1,2) & \rightarrow(2,2)\rightarrow(2,3)\rightarrow(3,3)\rightarrow\cdots\rightarrow(i-2,i-1)\rightarrow(i-1,i-1)

  & \rightarrow(i,i-1)\rightarrow(i,i-2)\rightarrow\cdots\rightarrow(i,2)\rightarrow(i,1)

  & \rightarrow(i+1,1)\rightarrow\cdots\rightarrow(3001,1)\rightarrow(3002,1).
 \end{aligned}
 \]

 Now note that:
 \begin{itemize}
 \item The cells from $(1,2)$ to $(i-1,i-1)$ were not selected because
 they were reached earlier than $(i,j)$ on the previous attempt.
 \item The cells $(i,k)$ for $1\leq k\leq i-1$ were not selected because
 there is only one selected cell in row $i$, and it lies in $(i,i)$
 or $(i,i+1)$.
 \item The cells $(k,1)$ for $i\leq k\leq3002$ were not selected because
 Peter selected at most one cell in column 1 (since there is one selected
 cell per row from 2 to 3001), and it lies in $(2,1)$.
 \end{itemize}
 Therefore James will win on the third attempt. Therefore, the smallest
 positive integer $n$ is $3$.