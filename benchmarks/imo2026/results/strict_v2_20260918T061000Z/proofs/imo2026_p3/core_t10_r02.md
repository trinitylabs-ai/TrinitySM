Let $n$ be a positive integer. Let $m$ be the total number of pieces after all cuts are made. Since Liu marks at most $n$ points and Xiang marks at most $n$ points, $m \le 2n+1$. Let the lengths of these pieces be $l_{(1)} \ge l_{(2)} \ge \dots \ge l_{(m)}$.
Liu and Xiang take turns claiming pieces, with Liu moving first. Liu will always claim $l_{(1)}$, then Xiang claims $l_{(2)}$, then Liu claims $l_{(3)}$, and so on. Thus, Liu's total length is $S_L = \sum_{i=1}^{\lceil m/2 \rceil} l_{(2i-1)}$ and Xiang's total length is $S_X = \sum_{i=1}^{\lfloor m/2 \rfloor} l_{(2i)}$.
Since $l_{(2i-1)} \ge l_{(2i)}$ for all $i$, it follows that $S_L \ge S_X$. Since $S_L + S_X = 1$, we have $S_L \ge 1/2$.

We claim that the largest number $c$ Liu can guarantee is $c = \frac{n+1}{2n+1}$.

**1. Lower Bound: Liu's Strategy**
Liu marks $n$ points to create $n+1$ pieces $L_1, L_2, \dots, L_{n+1}$ with $L_1 = \frac{n+1}{2n+1}$ and $L_2 = L_3 = \dots = L_{n+1} = \frac{1}{2n+1}$.
Xiang makes $n$ cuts, resulting in $m \le 2n+1$ pieces. We analyze $S_L - S_X = \sum_{j=1}^m (-1)^{j-1} l_{(j)}$.
If $m$ is odd, $S_L - S_X = (l_{(1)} - l_{(2)}) + \dots + (l_{(m-2)} - l_{(m-1)}) + l_{(m)} \ge l_{(m)}$.
If $m$ is even, $S_L - S_X = (l_{(1)} - l_{(2)}) + \dots + (l_{(m-1)} - l_{(m)}) \ge 0$.

To minimize $S_L$, Xiang wants to maximize $S_X = \sum_{j=1}^{\lfloor m/2 \rfloor} l_{(2j)}$.
The pieces are formed by dividing $L_1, \dots, L_{n+1}$. Let $c_i$ be the number of cuts in $L_i$, so $\sum c_i \le n$.
If $c_i = 0$, $L_i$ remains a piece of length $L_i$. If $c_i > 0$, $L_i$ is split into $c_i+1$ pieces, each of length at most $L_i$.
Xiang's best strategy to maximize $S_X$ is to make the pieces as equal as possible. If he cuts $L_1$ into $n+1$ equal pieces of length $\frac{1}{2n+1}$ and leaves $L_2, \dots, L_{n+1}$ uncut, then all $2n+1$ pieces are $\frac{1}{2n+1}$. In this case, $S_X = \frac{n}{2n+1}$, so $S_L = \frac{n+1}{2n+1}$.
If Xiang makes the pieces unequal or uses fewer cuts, $S_L - S_X$ generally increases. For instance, if $m=3$ and $L_1=2/3, L_2=1/3$, $S_L - S_X = 1 - 2l_{(2)}$. Since $l_{(2)} \le 1/3$ (the second largest of $\{x, 2/3-x, 1/3\}$), $S_L - S_X \ge 1/3$.
Thus, Liu can guarantee $S_L \ge \frac{n+1}{2n+1}$.

**2. Upper Bound: Xiang's Strategy**
We show that for any choice of $L_1, \dots, L_{n+1}$ by Liu, Xiang can ensure $S_L - S_X \le \frac{1}{2n+1}$.
Let $L_{(1)} \ge L_{(2)} \ge \dots \ge L_{(n+1)}$ be the sorted pieces chosen by Liu.
Case 1: $L_{(n+1)} \le \frac{1}{2n+1}$.
Xiang cuts $L_{(1)}, \dots, L_{(n)}$ each into two equal pieces of length $L_{(i)}/2$.
The pieces are $L_{(1)}/2, L_{(1)}/2, L_{(2)}/2, L_{(2)}/2, \dots, L_{(n)}/2, L_{(n)}/2, L_{(n+1)}$.
The sorted pieces $l_{(j)}$ satisfy $l_{(2i-1)} = l_{(2i)} = L_{(i)}/2$ for $i=1, \dots, n$, and $l_{(2n+1)} = L_{(n+1)}$.
Then $S_L - S_X = \sum_{i=1}^n (L_{(i)}/2 - L_{(i)}/2) + L_{(n+1)} = L_{(n+1)} \le \frac{1}{2n+1}$.

Case 2: $L_{(n+1)} > \frac{1}{2n+1}$.
Then all $L_i > \frac{1}{2n+1}$, which implies $L_{(1)} = 1 - \sum_{i=2}^{n+1} L_{(i)} < 1 - \frac{n}{2n+1} = \frac{n+1}{2n+1}$.
Xiang uses his $n$ cuts to divide $L_{(1)}$ into $n+1$ pieces $x_1, \dots, x_{n+1}$.
He chooses $x_i = L_{(i+1)} - \epsilon$ for $i=1, \dots, n$, where $\epsilon > 0$ is very small.
The last piece is $x_{n+1} = L_{(1)} - \sum_{i=1}^n (L_{(i+1)} - \epsilon) = 2L_{(1)} - 1 + n\epsilon$.
The pieces are $\{L_{(2)}, L_{(2)}-\epsilon, L_{(3)}, L_{(3)}-\epsilon, \dots, L_{(n+1)}, L_{(n+1)}-\epsilon, x_{n+1}\}$.
Since $L_{(1)} < \frac{n+1}{2n+1}$, $x_{n+1} \approx 2L_{(1)} - 1 < \frac{1}{2n+1} < L_{(n+1)}$.
For sufficiently small $\epsilon$, the sorted pieces are $l_{(2i-1)} = L_{(i+1)}$ and $l_{(2i)} = L_{(i+1)}-\epsilon$ for $i=1, \dots, n$, and $l_{(2n+1)} = x_{n+1}$.
Then $S_L - S_X = \sum_{i=1}^n (L_{(i+1)} - (L_{(i+1)}-\epsilon)) + x_{n+1} = n\epsilon + 2L_{(1)} - 1 + n\epsilon = 2L_{(1)} - 1 + 2n\epsilon$.
Since $2L_{(1)} - 1 < \frac{1}{2n+1}$, Xiang can choose $\epsilon$ small enough such that $S_L - S_X \le \frac{1}{2n+1}$.

In both cases, $S_L - S_X \le \frac{1}{2n+1}$, which implies $2S_L - 1 \le \frac{1}{2n+1}$, so $S_L \le \frac{n+1}{2n+1}$.
Thus, the largest number $c$ Liu can guarantee is $\frac{n+1}{2n+1}$.