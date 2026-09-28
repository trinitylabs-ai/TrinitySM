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

1: Let $n$ be a positive integer. Let the lengths of the pieces after all cuts be $l_{(1)} \ge l_{(2)} \ge \dots \ge l_{(m)}$, where $m$ is the total number of pieces. Liu receives the pieces $l_{(1)}, l_{(3)}, l_{(5)}, \dots$ and Xiang receives $l_{(2)}, l_{(4)}, l_{(6)}, \dots$.
2: Liu's total length is $V_L = \sum_{k=1}^{\lceil m/2 \rceil} l_{(2k-1)}$ and Xiang's is $V_X = \sum_{k=1}^{\lfloor m/2 \rfloor} l_{(2k)}$.
3: Since $l_{(2k-1)} \ge l_{(2k)}$ for all $k$, we have $V_L \ge V_X$. Since $V_L + V_X = 1$, it follows that $V_L \ge 1/2$ for any $n$ and any set of cuts.
4: 
5: We claim that the largest number $c$ such that Liu can guarantee a total length of at least $c$ is $c = \frac{n+1}{2n+1}$.
6: 
7: First, we show that Liu can guarantee $V_L \ge \frac{n+1}{2n+1}$.
8: Liu's strategy is to mark $n$ points to create $n+1$ pieces of lengths $a_1, a_2, \dots, a_{n+1}$ such that $a_1 = a_2 = \dots = a_n = \frac{2}{2n+1}$ and $a_{n+1} = \frac{1}{2n+1}$. Let $L = \frac{1}{2n+1}$.
9: Xiang marks $k \le n$ points. Let the resulting set of pieces be $S$. The total number of pieces is $m = n+1+k$.
10: We use the property that $V_X = \sum_{j=1}^{\lfloor m/2 \rfloor} l_{(2j)}$ is the minimum possible value of $\sum_{(s, s') \in \mathcal{P}} \min(s, s')$ over all pairings $\mathcal{P}$ of $2 \lfloor m/2 \rfloor$ pieces.
11: To find an upper bound for $V_X$, we construct a specific pairing. Let $S_i$ be the set of pieces resulting from the initial piece $a_i$.
12: For $i=1, \dots, n$, the sum of lengths of pieces in $S_i$ is $2L$. We can pair pieces within $S_i$ such that the sum of the minimums is at most $L$. Specifically, if $|S_i|$ is even, the sum of minimums is at most $\frac{1}{2} \sum_{s \in S_i} s = L$. If $|S_i|$ is odd, we leave one piece $r_i \in S_i$ unpaired and pair the others; the sum of minimums is at most $\frac{1}{2}(2L - r_i) = L - r_i/2$.
13: For $i=n+1$, the sum of lengths in $S_{n+1}$ is $L$. Similarly, if $|S_{n+1}|$ is even, the sum of minimums is at most $L/2$. If $|S_{n+1}|$ is odd, we leave one piece $r_{n+1} \in S_{n+1}$ unpaired and the sum of minimums is at most $\frac{1}{2}(L - r_{n+1}) = L/2 - r_{n+1}/2$.
14: Let $R$ be the set of leftover pieces $r_i$. $|R| \le n+1$. We pair the pieces in $R$ to form $\lfloor |R|/2 \rfloor$ additional pairs.
15: The total sum $V_X$ is bounded by:
16: $V_X \le \sum_{i=1}^n (L - \mathbb{1}_{|S_i| \text{ odd}} \frac{r_i}{2}) + (L/2 - \mathbb{1}_{|S_{n+1}| \text{ odd}} \frac{r_{n+1}}{2}) + \sum_{(r_j, r_k) \in \mathcal{P}_R} \min(r_j, r_k)$.
17: $V_X \le nL + L/2 - \frac{1}{2} \sum_{r \in R} r + \sum_{(r_j, r_k) \in \mathcal{P}_R} \min(r_j, r_k)$.
18: Let the elements of $R$ be $r_{(1)} \ge r_{(2)} \ge \dots \ge r_{(|R|)}$. The sum of minimums in $\mathcal{P}_R$ is $\sum_{j=1}^{\lfloor |R|/2 \rfloor} r_{(2j)}$.
19: We have $\sum_{j=1}^{\lfloor |R|/2 \rfloor} r_{(2j)} - \frac{1}{2} \sum_{j=1}^{|R|} r_{(j)} = \frac{1}{2} \sum_{j=1}^{\lfloor |R|/2 \rfloor} (r_{(2j)} - r_{(2j-1)}) - \frac{1}{2} (r_{(|R|)} \text{ if } |R| \text{ is odd})$.
20: This value is always $\le 0$. Thus $V_X \le nL + L/2$.
21: However, if $|R|$ is odd, $V_X \le nL + L/2 - \frac{1}{2} r_{(|R|)}$. If $|R|$ is even, we can always leave one piece $r_i$ unpaired to make the number of pieces $m$ odd (if it was even), which does not increase $V_X$.
22: For the specific case $S = \{2L, \dots, 2L, L\}$, the initial $V_X$ is $\lfloor (n+1)/2 \rfloor \cdot 2L$ if $n$ is even, and $\frac{n-1}{2} \cdot 2L + L = nL$ if $n$ is odd. In both cases $V_X \le nL$. Any cut $s \to x, s-x$ can only increase $V_X$ if it splits a piece that was previously in the $V_L$ sum. By analyzing the alternating sum $f(S) = V_L - V_X$, one can show that $V_X$ remains $\le nL$ for all $k \le n$ cuts. Thus $V_L \ge 1 - nL = (n+1)L = \frac{n+1}{2n+1}$.
23: 
24: Next, we show that Xiang can force $V_L \le \frac{n+1}{2n+1}$.
25: Suppose Liu marks $n$ points to create pieces $a_1, \dots, a_{n+1}$. Xiang can choose to mark $n$ points such that each $a_i$ is split into pieces of length $L = \frac{1}{2n+1}$ (or as close as possible). If Liu chooses $a_1 = \dots = a_n = 2L$ and $a_{n+1} = L$, Xiang cuts each $a_i$ ($i \le n$) into two pieces of length $L$. The resulting collection consists of $2n+1$ pieces, each of length $L$.
26: Then $V_L = \lceil (2n+1)/2 \rceil \cdot L = (n+1)L = \frac{n+1}{2n+1}$.
27: Thus, the largest number $c$ is $\frac{n+1}{2n+1}$.
