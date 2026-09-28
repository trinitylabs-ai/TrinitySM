# Problem

IMO 2026 Problem 3. Let n be a positive integer. Liu Bang and Xiang Yu have a stick of length 1 and want to divide it between themselves. Liu first marks at most n points on the stick, and then Xiang marks at most n points on the stick. All marked points are distinct. The stick is then cut at every marked point, producing a collection of pieces. Afterwards, Liu and Xiang take turns claiming any unclaimed piece, with Liu moving first. Each player wants to maximise the total length of the pieces they receive. For each n, determine the largest number c such that Liu can guarantee a total length of at least c, regardless of Xiang's play.

# Proof A

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
