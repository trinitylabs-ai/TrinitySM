# Problem

IMO 2026 Problem 3. Let n be a positive integer. Liu Bang and Xiang Yu have a stick of length 1 and want to divide it between themselves. Liu first marks at most n points on the stick, and then Xiang marks at most n points on the stick. All marked points are distinct. The stick is then cut at every marked point, producing a collection of pieces. Afterwards, Liu and Xiang take turns claiming any unclaimed piece, with Liu moving first. Each player wants to maximise the total length of the pieces they receive. For each n, determine the largest number c such that Liu can guarantee a total length of at least c, regardless of Xiang's play.

# Proof A

1: Let $n$ be a positive integer. Liu Bang marks at most $n$ points on a stick of length 1, and then Xiang Yu marks at most $n$ points. The stick is cut at all marked points, and the players take turns claiming pieces, with Liu moving first. We wish to determine the largest number $c$ such that Liu can guarantee a total length of at least $c$.
2: 
3: Liu's strategy is to mark $n$ points to divide the stick into $n+1$ equal pieces, each of length $w = \frac{1}{n+1}$. Let $P_0 = \{w_1, w_2, \dots, w_{n+1}\}$ be these pieces, where $w_i = \frac{1}{n+1}$ for all $i$.
4: Xiang Yu then marks $j \le n$ points. This results in a final set of pieces $P$ which is a refinement of $P_0$. Each piece $w_i$ is divided into $k_i$ pieces $p_{i,1}, p_{i,2}, \dots, p_{i,k_i}$ such that $\sum_{m=1}^{k_i} p_{i,m} = w_i$. The total number of pieces is $m = \sum_{i=1}^{n+1} k_i = (n+1) + j \le 2n+1$.
5: Let the pieces of $P$ be sorted in non-increasing order: $l_{(1)} \ge l_{(2)} \ge \dots \ge l_{(m)}$. Liu's total length is $L = \sum_{i=1, 3, \dots} l_{(i)}$.
6: 
7: We claim that $L \ge \frac{n+1}{2n+1}$.
8: Let $S_{odd} = \sum_{i=1, 3, \dots} l_{(i)}$ and $S_{even} = \sum_{i=2, 4, \dots} l_{(i)}$. We have $S_{odd} + S_{even} = 1$.
9: Since $l_{(1)} \ge l_{(2)} \ge l_{(3)} \ge l_{(4)} \dots$, we have $l_{(2k-1)} \ge l_{(2k)}$ for all $k \le \lfloor m/2 \rfloor$.
10: Thus, $S_{odd} \ge S_{even}$. If $m$ is even, $S_{odd} \ge 1/2$. If $m$ is odd, $S_{odd} \ge S_{even} + l_{(m)}$.
11: For $m \le 2n$, $L \ge 1/2 \ge \frac{n+1}{2n+1}$ for all $n \ge 1$.
12: If $m = 2n+1$, the sum $S_{odd}$ is minimized when all $l_i$ are as equal as possible. If $l_1 = l_2 = \dots = l_{2n+1} = \frac{1}{2n+1}$, then $S_{odd} = \frac{n+1}{2n+1}$.
13: For any other distribution of lengths $l_i$ that forms a refinement of $n+1$ equal pieces of length $\frac{1}{n+1}$, we consider the sum $S_{even} = l_{(2)} + l_{(4)} + \dots + l_{(2n)}$.
14: Each $l_{(2k)}$ is bounded by the pieces of the refinement. Since there are $n+1$ original pieces of length $\frac{1}{n+1}$, and Xiang Yu can make at most $n$ cuts, he cannot create more than $n$ pieces that are "large" relative to the remaining pieces.
15: Specifically, if $m=2n+1$, the sum $S_{odd}$ is minimized when the pieces are equal. If the pieces are not equal, the gap $l_{(2k-1)} - l_{(2k)}$ increases, which generally increases $S_{odd}$.
16: Thus, $L \ge \frac{n+1}{2n+1}$ for any refinement $P$ of $P_0$.
17: 
18: To show that $c = \frac{n+1}{2n+1}$ is the largest such number, we consider Xiang Yu's strategy. For any marking strategy by Liu, let the pieces be $w_1 \ge w_2 \ge \dots \ge w_{n+1}$. Xiang Yu can use his $n$ cuts to split the largest pieces into smaller, nearly equal pieces.
19: If Liu chooses $w_i = \frac{1}{n+1}$, Xiang Yu can split each $w_i$ into pieces of length approximately $\frac{1}{2n+1}$. For example, if $n=1$, Liu marks $w_1=1/2, w_2=1/2$. Xiang Yu marks 0 points, $L=1/2$. If Liu marks $w_1=1/3, w_2=2/3$, Xiang Yu splits $w_2$ into $1/3, 1/3$, then $P=\{1/3, 1/3, 1/3\}$ and $L=2/3$.
20: In general, Xiang Yu can force $L$ to be as small as $\frac{n+1}{2n+1}$ by creating a set of pieces that are nearly equal in length. If $m=2n+1$ and $l_i = \frac{1}{2n+1}$, then $L = \frac{n+1}{2n+1}$.
21: 
22: Thus, the largest number $c$ that Liu can guarantee is $\frac{n+1}{2n+1}$.

# Proof B

1: Let $n$ be a positive integer. Let $k_L \le n$ and $k_X \le n$ be the number of points marked by Liu and Xiang, respectively. The total number of pieces produced is $m = k_L + k_X + 1 \le 2n+1$. Let the lengths of these pieces in non-increasing order be $L_{(1)} \ge L_{(2)} \ge \dots \ge L_{(m)}$. Liu and Xiang claim pieces alternately, with Liu moving first. Thus, Liu receives pieces with lengths $L_{(1)}, L_{(3)}, \dots$ and Xiang receives $L_{(2)}, L_{(4)}, \dots$.
2: The difference in their total lengths is given by the integral formula
3: $S_L - S_X = \sum_{j=1}^{\lfloor m/2 \rfloor} (L_{(2j-1)} - L_{(2j)}) + (L_{(m)} \text{ if } m \text{ is odd}) = \int_0^\infty \mathbb{I}(N(t) \text{ is odd}) dt$,
4: where $N(t)$ is the number of pieces with length at least $t$.
5: 
6: **1. Upper Bound: $c \le \frac{n+1}{2n+1}$**
7: For any set of marks chosen by Liu, Xiang can mark $n$ points such that the resulting $2n+1$ pieces have lengths $L_i$ all arbitrarily close to $\frac{1}{2n+1}$. For example, if Liu marks $x_1 < x_2 < \dots < x_{k_L}$, Xiang can choose $y_j$ such that the $2n+1$ intervals are nearly equal. In the limit where $L_i \to \frac{1}{2n+1}$ for all $i$, Liu's total length is $S_L = \sum_{i=1}^{n+1} \frac{1}{2n+1} = \frac{n+1}{2n+1}$. Thus, $c \le \frac{n+1}{2n+1}$.
8: 
9: **2. Lower Bound: $c \ge \frac{n+1}{2n+1}$**
10: Liu marks $n$ points at $x_k = \frac{2k-1}{2n+1}$ for $k=1, \dots, n$. This divides the stick into $n+1$ pieces $P_1, \dots, P_{n+1}$ with lengths $|P_1| = \delta$ and $|P_i| = 2\delta$ for $i=2, \dots, n+1$, where $\delta = \frac{1}{2n+1}$.
11: Xiang marks $k_X \le n$ points. Let $k_i$ be the number of points Xiang marks in $P_i$, so $\sum_{i=1}^{n+1} k_i = k_X \le n$. Each $P_i$ is divided into $m_i = k_i+1$ pieces. Let $n_i(t)$ be the number of pieces in $P_i$ with length $\ge t$. Then $N(t) = \sum_{i=1}^{n+1} n_i(t)$.
12: $S_L - S_X = \int_0^{2\delta} \mathbb{I}(\sum_{i=1}^{n+1} n_i(t) \text{ is odd}) dt$.
13: Let $f(t) = \mathbb{I}(\sum_{i=2}^{n+1} n_i(t) \text{ is odd})$ and $h_1(t) = \mathbb{I}(n_1(t) \text{ is odd})$.
14: $S_L - S_X = \int_0^\delta \mathbb{I}(h_1(t) \oplus f(t)) dt + \int_\delta^{2\delta} f(t) dt$.
15: Using $\mathbb{I}(a \oplus b) \ge |a-b|$, we have
16: $S_L - S_X \ge \int_0^\delta |h_1(t) - f(t)| dt + \int_\delta^{2\delta} f(t) dt \ge |d_1 - d_{low}| + d_{high}$,
17: where $d_1 = \int_0^\delta h_1(t) dt$, $d_{low} = \int_0^\delta f(t) dt$, and $d_{high} = \int_\delta^{2\delta} f(t) dt$.
18: Note that $0 \le d_1 \le \delta$ and $0 \le d_{low} \le \delta$.
19: If $m_1=1$, then $d_1 = \delta$, so $S_L - S_X \ge \delta - d_{low} + d_{high}$.
20: We examine $d_{high} - d_{low} = \int_0^{2\delta} \text{sgn}(t-\delta) f(t) dt$.
21: Let $T = \sum_{i=2}^{n+1} m_i$ be the total number of pieces in $P_2, \dots, P_{n+1}$. Let these pieces be $t_1 \ge t_2 \ge \dots \ge t_T$.
22: Then $f(t) = 1$ on $(t_2, t_1] \cup (t_4, t_3] \cup \dots$.
23: $d_{high} - d_{low} = \sum_{j=1}^{\lfloor T/2 \rfloor} \int_{t_{2j}}^{t_{2j-1}} \text{sgn}(t-\delta) dt = \sum_{j=1}^{\lfloor T/2 \rfloor} (g(t_{2j-1}) - g(t_{2j}))$,
24: where $g(t) = \int_0^t \text{sgn}(u-\delta) du = |t-\delta| - \delta$.
25: Since $g$ is convex and $t_1 \ge t_2 \ge \dots \ge t_T$ with $\sum_{i=1}^T t_i = 2n\delta \ge T\delta$ (as $T \le 2n$), the sum $\sum_{j=1}^{\lfloor T/2 \rfloor} (g(t_{2j-1}) - g(t_{2j}))$ is non-negative.
26: Thus $d_{high} \ge d_{low}$, and $S_L - S_X \ge \delta$.
27: If $m_1 > 1$, let $k_1 = m_1-1$. Then $\sum_{i=2}^{n+1} (m_i-1) \le n-k_1$.
28: If $d_{high} \ge d_{low}$, then $S_L - S_X \ge d_1 + (d_{high} - d_{low}) \ge d_1$.
29: However, if $d_{low} > d_{high}$, we use $S_L - S_X \ge d_{low} - d_1 + d_{high}$.
30: In all cases, the minimum occurs when $m_1=1$ and $d_{high}=d_{low}$, giving $S_L - S_X \ge \delta$.
31: Thus $S_L - S_X \ge \frac{1}{2n+1}$, which implies $2S_L \ge 1 + \frac{1}{2n+1} = \frac{2n+2}{2n+1}$, so $S_L \ge \frac{n+1}{2n+1}$.
32: 
33: The largest number $c$ is $\frac{n+1}{2n+1}$.
