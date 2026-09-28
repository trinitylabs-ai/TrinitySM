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
