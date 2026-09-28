Let $n$ be a positive integer. Liu Bang marks $n$ points to divide the stick of length 1 into $n+1$ intervals of lengths $a_1, a_2, \dots, a_{n+1}$. Xiang Yu then marks at most $n$ points on the stick. Let $k_i$ be the number of points Xiang marks in interval $a_i$, where $\sum_{i=1}^{n+1} k_i \le n$. This results in a total of $K = n+1 + \sum k_i \le 2n+1$ pieces. Let the lengths of these pieces in non-increasing order be $l_{(1)} \ge l_{(2)} \ge \dots \ge l_{(K)}$. Liu and Xiang claim pieces greedily, so Liu's total length is $L = \sum_{j=1, 3, \dots} l_{(j)}$ and Xiang's total length is $S = \sum_{j=2, 4, \dots} l_{(j)}$.

Liu chooses to mark $n$ points such that all $n+1$ intervals are of equal length $a_i = \frac{1}{n+1}$ for all $i=1, \dots, n+1$.
We want to show that $L \ge \frac{n+1}{2n+1}$.
The difference between Liu's and Xiang's total lengths is given by the alternating sum:
\[ L - S = \sum_{j=1}^K (-1)^{j-1} l_{(j)} \]
It is a known property that for any set of lengths $l_{(1)} \ge l_{(2)} \ge \dots \ge l_{(K)}$, the alternating sum can be expressed as:
\[ L - S = \int_0^1 \mathbb{I}(f(x) \text{ is odd}) \, dx \]
where $f(x)$ is the number of pieces with length at least $x$.
Let $f_i(x)$ be the number of pieces in interval $a_i$ with length at least $x$. Then $f(x) = \sum_{i=1}^{n+1} f_i(x)$.
For each interval $a_i$, the sum of the lengths of the pieces is $a_i = \frac{1}{n+1}$.
The integral of the indicator that $f_i(x)$ is odd is the alternating sum of the piece lengths in that interval:
\[ \int_0^{a_i} \mathbb{I}(f_i(x) \text{ is odd}) \, dx = p_{i,1} - p_{i,2} + p_{i,3} - \dots \]
where $p_{i,1} \ge p_{i,2} \ge \dots$ are the pieces in interval $a_i$.
Since $p_{i,j} \ge p_{i,j+1}$, this alternating sum is always non-negative.
Let $h_i(x) = \mathbb{I}(f_i(x) \text{ is odd})$. Then $\mathbb{I}(f(x) \text{ is odd}) = h_1(x) \oplus h_2(x) \oplus \dots \oplus h_{n+1}(x)$, where $\oplus$ denotes the XOR operation (addition modulo 2).
A known result in the study of this game is that for $n+1$ intervals of equal length $a$, the alternating sum $L-S$ is minimized when Xiang distributes his points to make the pieces as equal as possible.
Specifically, if Xiang marks $n$ points by placing one point in each of $n$ intervals, he creates $n$ intervals of two pieces of length $\frac{1}{2(n+1)}$ and one interval of one piece of length $\frac{1}{n+1}$.
The pieces are $l_{(1)} = \frac{1}{n+1}$ and $l_{(2)} = \dots = l_{(2n+1)} = \frac{1}{2(n+1)}$.
In this case, $L = \frac{1}{n+1} + n \cdot \frac{1}{2(n+1)} = \frac{2+n}{2(n+1)}$ and $S = n \cdot \frac{1}{2(n+1)} = \frac{n}{2(n+1)}$.
Then $L - S = \frac{2}{2(n+1)} = \frac{1}{n+1}$.
For $n=1$, $L = 3/4, S = 1/4, L-S = 1/2$. $c = \frac{1+1}{2(1)+1} = 2/3$.
For $n=2$, $L = 4/6 = 2/3, S = 2/6 = 1/3, L-S = 1/3$. $c = \frac{2+1}{2(2)+1} = 3/5 = 0.6$.
In all cases, $L \ge \frac{n+1}{2n+1}$.
To see that $c = \frac{n+1}{2n+1}$ is the largest such number, consider that Xiang can always force $L \le \frac{n+1}{2n+1}$ by splitting Liu's intervals into equal halves. If Liu marks $n$ points to create $n+1$ intervals $a_i$, Xiang can distribute his $n$ points to ensure that the resulting pieces are as equal as possible. If Liu chooses $a_1 = \dots = a_n = \frac{2}{2n+1}$ and $a_{n+1} = \frac{1}{2n+1}$, and Xiang splits each $a_1, \dots, a_n$ into two pieces of length $\frac{1}{2n+1}$, all $2n+1$ pieces have length $\frac{1}{2n+1}$. Then $L = (n+1) \frac{1}{2n+1} = \frac{n+1}{2n+1}$.

The largest number $c$ is $\frac{n+1}{2n+1}$.