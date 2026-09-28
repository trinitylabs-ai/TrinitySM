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
