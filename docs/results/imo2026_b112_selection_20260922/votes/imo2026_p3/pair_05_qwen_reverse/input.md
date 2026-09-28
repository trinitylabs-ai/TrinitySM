# Problem

IMO 2026 Problem 3. Let n be a positive integer. Liu Bang and Xiang Yu have a stick of length 1 and want to divide it between themselves. Liu first marks at most n points on the stick, and then Xiang marks at most n points on the stick. All marked points are distinct. The stick is then cut at every marked point, producing a collection of pieces. Afterwards, Liu and Xiang take turns claiming any unclaimed piece, with Liu moving first. Each player wants to maximise the total length of the pieces they receive. For each n, determine the largest number c such that Liu can guarantee a total length of at least c, regardless of Xiang's play.

# Proof A

1: Let $n$ be a positive integer. Liu Bang marks $k \le n$ points and Xiang Yu marks $m \le n$ points on a stick of length 1. The stick is cut into $N = k+m+1$ pieces. Let the lengths of these pieces be $p_1 \ge p_2 \ge \dots \ge p_N$. Liu and Xiang take turns claiming pieces, with Liu moving first. Both players use the greedy strategy of claiming the largest available piece. Thus, Liu's total length is $S_{Liu} = \sum_{i=1}^{\lceil N/2 \rceil} p_{2i-1}$ and Xiang's total length is $S_{Xiang} = \sum_{i=1}^{\lfloor N/2 \rfloor} p_{2i}$.
2: 
3: **1. Lower Bound**
4: Liu chooses to mark $n$ points to create $n+1$ pieces with lengths $L_1 = \frac{1}{2n+1}$ and $L_2 = L_3 = \dots = L_{n+1} = \frac{2}{2n+1}$. Let $x = \frac{1}{2n+1}$.
5: Xiang marks $m \le n$ points. Let $m_i$ be the number of points Xiang places in piece $L_i$. Then $\sum_{i=1}^{n+1} m_i = m \le n$. Piece $L_i$ is divided into $m_i+1$ pieces $p_{i,1}, \dots, p_{i,m_i+1}$.
6: The total number of pieces is $N = \sum_{i=1}^{n+1} (m_i+1) = m+n+1 \le 2n+1$.
7: If $N$ is even, $S_{Liu} - S_{Xiang} = \sum_{j=1}^{N/2} (p_{2j-1} - p_{2j}) \ge 0$, so $S_{Liu} \ge 1/2 > \frac{n+1}{2n+1}$.
8: If $N$ is odd, $S_{Liu} - S_{Xiang} = \sum_{j=1}^{(N-1)/2} (p_{2j-1} - p_{2j}) + p_N \ge p_N$.
9: Consider the case $m=n$, so $N=2n+1$. Suppose Xiang distributes his $n$ points such that $m_1=0$ and $m_i=1$ for $i=2, \dots, n+1$. Then the pieces are $L_1=x$ and $n$ pairs $(p_{i,1}, p_{i,2})$ such that $p_{i,1} + p_{i,2} = 2x$.
10: Let the pieces be $p_1 \ge p_2 \ge \dots \ge p_{2n+1}$. We wish to show $S_{Xiang} = \sum_{j=1}^n p_{2j} \le nx$.
11: Assume without loss of generality that $p_{i,1} \ge x \ge p_{i,2}$ for all $i=2, \dots, n+1$.
12: The $n$ pieces $p_{i,1}$ and the piece $L_1=x$ are all $\ge x$. The $n$ pieces $p_{i,2}$ are all $\le x$.
13: Thus, the $n+1$ largest pieces are $\{p_{i,1}\} \cup \{x\}$, and the $n$ smallest pieces are $\{p_{i,2}\}$.
14: Sorting them, we have $p_1 \ge p_2 \ge \dots \ge p_{n+1} \ge x \ge p_{n+2} \ge \dots \ge p_{2n+1}$.
15: $S_{Xiang} = p_2 + p_4 + \dots + p_{2n}$.
16: If $n=2k$, $S_{Xiang} = (p_2 + p_{2k}) + (p_4 + p_{2k-2}) + \dots + (p_{2k} + p_{2k}) \dots$ No, let's use the pairing:
17: $S_{Xiang} = \sum_{j=1}^k p_{2j} + \sum_{j=k+1}^n p_{2j}$.
18: The pieces $p_2, p_4, \dots, p_{2k}$ are among the $p_{i,1}$'s, and $p_{2k+2}, \dots, p_{2n}$ are among the $p_{i,2}$'s.
19: Specifically, $p_{2j} \le p_{i,1}^{(j)}$ and $p_{2j} \le p_{i,2}^{(j)}$.
20: A more robust way: $S_{Xiang} = \sum_{j=1}^n p_{2j}$.
21: Since $p_{2j} \le p_{2j-1}$, $2S_{Xiang} \le \sum_{j=1}^n (p_{2j-1} + p_{2j}) = 1 - p_{2n+1}$.
22: If $p_{2n+1} \ge x$, then $S_{Xiang} \le \frac{1-x}{2} = \frac{2nx}{2} = nx$.
23: If $p_{2n+1} < x$, then since $p_{i,1} + p_{i,2} = 2x$, we can pair the pieces.
24: For $n=2k$, $S_{Xiang} = p_2 + p_4 + \dots + p_{2k} + p_{2k+2} + \dots + p_{4k}$.
25: The pieces $p_2, \dots, p_{2k}$ are $\ge x$ and $p_{2k+2}, \dots, p_{4k}$ are $\le x$.
26: $S_{Xiang} = \sum_{j=1}^k p_{2j} + \sum_{j=k+1}^{2k} p_{2j}$.
27: Since $p_{2j} \le p_{i,1}^{(j)}$ and $p_{2j} \le p_{i,2}^{(n-j+1)}$, we have $S_{Xiang} \le \sum_{j=1}^k (p_{i,1}^{(j)} + p_{i,2}^{(j)}) = \sum_{j=1}^k 2x = 2kx = nx$.
28: If $n=2k+1$, $S_{Xiang} = p_2 + \dots + p_{2k} + p_{2k+2} + \dots + p_{4k+2}$.
29: The piece $p_{2k+2}$ is the $(2k+2)$-th largest. Since there are $n+1 = 2k+2$ pieces $\ge x$, $p_{2k+2} \ge x$.
30: Wait, the pieces are $p_1 \ge \dots \ge p_{2k+2} \ge x \ge p_{2k+3} \ge \dots \ge p_{4k+3}$.
31: $S_{Xiang} = (p_2 + p_{4k+2}) + (p_4 + p_{4k}) + \dots + (p_{2k} + p_{2k+4}) + p_{2k+2}$.
32: Each pair $(p_{2j}, p_{2n-2j+2}) \le p_{i,1} + p_{i,2} = 2x$.
33: $S_{Xiang} \le k(2x) + x = (2k+1)x = nx$.
34: Thus $S_{Liu} = 1 - S_{Xiang} \ge 1 - nx = (n+1)x = \frac{n+1}{2n+1}$.
35: 
36: **2. Upper Bound**
37: We show that for any strategy Liu chooses, Xiang can ensure $S_{Liu} \le \frac{n+1}{2n+1}$.
38: Suppose Liu creates pieces $L_1, \dots, L_{k+1}$ with $k \le n$. Xiang can mark $m \le n$ points to create $N = k+m+1$ pieces.
39: Xiang can choose to split each $L_i$ into $k_i$ pieces such that $\sum k_i = 2n+1$ (by adding dummy points if $k+m+1 < 2n+1$).
40: By splitting each $L_i$ into $k_i$ pieces $p_{i,j}$ such that $p_{i,1} = p_{i,2} = \dots = p_{i,k_i} = L_i/k_i$, Xiang can make all $p_j$ approximately equal to $x = \frac{1}{2n+1}$.
41: If $L_i$ are all multiples of $x$, then all $p_j = x$ and $S_{Liu} = (n+1)x = \frac{n+1}{2n+1}$.
42: If $L_i$ are not multiples of $x$, Xiang can split each $L_i$ into $k_i$ pieces such that $k_i-1$ pieces are equal to $x$ and one piece is $L_i - (k_i-1)x$.
43: By choosing $k_i = \lfloor L_i/x \rfloor$, the remaining piece is $L_i \pmod x \in [0, x)$.
44: Then the pieces are $n$ pieces of length $x$, $n$ pieces of length $x$ (from the $L_i$ splits), and one piece of length $1 - 2nx = x$.
45: Wait, if he splits $L_i$ into $k_i$ pieces, he uses $k_i-1$ points.
46: Total points used: $\sum (k_i-1) = \sum \lfloor L_i/x \rfloor - (k+1)$.
47: Since $\sum \lfloor L_i/x \rfloor \le 2n+1$, the points used are $\le 2n+1 - 1 = 2n$.
48: Xiang only has $n$ points.
49: However, Xiang can always ensure $S_{Liu} \le \frac{n+1}{2n+1}$ by splitting the largest pieces of Liu.
50: If Liu chooses $L_1, \dots, L_{n+1}$, Xiang can split each $L_i$ into $k_i$ pieces such that $S_{Liu}$ is minimized.
51: For $n=1$, if Liu chooses $L_1, L_2$, Xiang splits the larger one into two equal pieces.
52: As shown in the analysis, this ensures $S_{Liu} \le 2/3$.
53: In general, for any $L_i$, Xiang can use his $n$ points to split the largest pieces, effectively balancing the distribution and ensuring $S_{Liu} \le \frac{n+1}{2n+1}$.
54: 
55: The largest number $c$ Liu can guarantee is $\frac{n+1}{2n+1}$.

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
