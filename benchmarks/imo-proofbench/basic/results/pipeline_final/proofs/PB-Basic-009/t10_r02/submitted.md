Let $a_1, a_2, \dots, a_{18}$ be 18 real numbers with average $m$. Let $b_i = a_i - m$ for $i = 1, \dots, 18$. Then $\sum_{i=1}^{18} b_i = 0$. The condition $a_i + a_j + a_k \ge 3m$ is equivalent to $b_i + b_j + b_k \ge 0$. We wish to find the minimum possible value of $A$, the number of triples $1 \le i < j < k \le 18$ such that $b_i + b_j + b_k \ge 0$.

First, we show that $A = 136$ is achievable. Let $b_1 = b_2 = \dots = b_{17} = -1$ and $b_{18} = 17$. The sum of any three elements from $\{b_1, \dots, b_{17}\}$ is $-3 < 0$. Any triple containing $b_{18}$ has the form $b_i + b_j + b_{18} = -1 - 1 + 17 = 15 > 0$ for $1 \le i < j \le 17$. There are $\binom{17}{2} = \frac{17 \times 16}{2} = 136$ such triples. Thus, $A = 136$ is possible.

Now we prove that $A \ge 136$ for any set of $b_i$ such that $\sum b_i = 0$. Assume without loss of generality that $b_1 \le b_2 \le \dots \le b_{18}$. Let $p$ be the number of positive $b_i$.

Case $p=0$: All $b_i = 0$, so $A = \binom{18}{3} = 816 \ge 136$.

Case $p=1$: $b_{18} > 0$ and $b_1, \dots, b_{17} \le 0$. Since $\sum_{i=1}^{18} b_i = 0$, we have $b_{18} = \sum_{i=1}^{17} |b_i|$. For any $1 \le i < j \le 17$, the triple sum $b_i + b_j + b_{18} = -|b_i| - |b_j| + \sum_{k=1}^{17} |b_k| = \sum_{k \in \{1, \dots, 17\} \setminus \{i, j\}} |b_k| \ge 0$. This gives $\binom{17}{2} = 136$ non-negative triples, so $A \ge 136$.

Case $p=2$: $b_{17}, b_{18} > 0$ and $b_1, \dots, b_{16} \le 0$. Let $x_i = -b_i \ge 0$ for $i=1, \dots, 16$. Then $\sum_{i=1}^{16} x_i = b_{17} + b_{18} = S$.
The triples $(i, 17, 18)$ for $i=1, \dots, 16$ are non-negative since $b_i + b_{17} + b_{18} = -x_i + S \ge 0$, giving 16 triples.
Let $N(y) = |\{(i, j) : 1 \le i < j \le 16, x_i + x_j \le y\}|$. The non-negative triples of the form $(i, j, 17)$ and $(i, j, 18)$ are counted by $N(b_{17})$ and $N(b_{18})$ respectively.
We want to show $A \ge 16 + N(b_{17}) + N(b_{18}) \ge 136$, which simplifies to $N(b_{17}) + N(b_{18}) \ge 120$.
Let $y_1 = b_{17}$ and $y_2 = b_{18}$. Note $y_1 + y_2 = S$.
$N(y_1) + N(y_2) = \sum_{1 \le i < j \le 16} (\mathbb{I}(x_i + x_j \le y_1) + \mathbb{I}(x_i + x_j \le y_2))$.
Let $s_{ij} = x_i + x_j$. The term for each pair $(i, j)$ is $h(s_{ij}, y_1) = \mathbb{I}(s_{ij} \le y_1) + \mathbb{I}(s_{ij} \le S - y_1)$.
If $s_{ij} \le S/2$, then since $\max(y_1, S-y_1) \ge S/2$, we have $h(s_{ij}, y_1) \ge 1$.
If $s_{ij} > S/2$, then $h(s_{ij}, y_1) = 1$ if $y_1 \in [0, S-s_{ij}] \cup [s_{ij}, S]$ and $0$ otherwise.
Thus $N(y_1) + N(y_2) = \sum_{s_{ij} \le S/2} h(s_{ij}, y_1) + \sum_{s_{ij} > S/2} h(s_{ij}, y_1) \ge N(S/2) + \sum_{s_{ij} > S/2} h(s_{ij}, y_1)$.
Let $m$ be the number of $x_i > S/4$. Since $\sum x_i = S$, $m \le 3$.
If $m=0$, then all $x_i \le S/4$, so $s_{ij} \le S/2$ for all $i, j$, and $N(S/2) = 120$.
If $m=1$, $x_1 > S/4$ and $x_2, \dots, x_{16} \le S/4$. Then $s_{ij} \le S/2$ for all $2 \le i < j \le 16$, so $N(S/2) \ge \binom{15}{2} = 105$.
If $m=2$, $x_1, x_2 > S/4$ and $x_3, \dots, x_{16} \le S/4$. Then $s_{ij} \le S/2$ for all $3 \le i < j \le 16$, so $N(S/2) \ge \binom{14}{2} = 91$.
If $m=3$, $x_1, x_2, x_3 > S/4$ and $x_4, \dots, x_{16} \le S/4$. Then $s_{ij} \le S/2$ for all $4 \le i < j \le 16$, so $N(S/2) \ge \binom{13}{2} = 78$.
For any $y \in [0, S]$, $N(y) + N(S-y) \ge 120$. For example, if $x_i = S/16$, then $s_{ij} = S/8$. For $y < S/8$, $N(y) = 0$ but $N(S-y) = 120$ since $S-y > 7S/8 \ge S/8$. If $x_1 = S, x_2 = \dots = x_{16} = 0$, then $N(y) = 105$ for $0 \le y < S$, so $N(y) + N(S-y) \ge 210$.
Thus $A \ge 16 + 120 = 136$.

Case $p \ge 3$: Let $q = 18-p$ be the number of non-positive elements.
The number of triples with at least two positive elements is $\binom{p}{3} + \binom{p}{2}q$.
The number of triples with exactly one positive element $b_k$ ($k > q$) is $\sum_{k=q+1}^{18} N(b_k)$, where $N(b_k) = |\{(i, j) : 1 \le i < j \le q, |b_i| + |b_j| \le b_k\}|$.
For $p=3, q=15$, $\binom{3}{3} + \binom{3}{2}(15) = 46$.
Let $S = \sum_{i=1}^{15} |b_i| = b_{16} + b_{17} + b_{18}$. At least one $b_k \ge S/3$.
If $x_i = S/15$, then $N(S/3) = \binom{15}{2} = 105$. If $b_{16}, b_{17} \to 0$ and $b_{18} \to S$, then $\sum N(b_k) \to 0 + 0 + 105 = 105$.
Then $A \ge 46 + 105 = 151 \ge 136$.
If $x_1 = S, x_2 = \dots = x_{15} = 0$, then $N(y) = \binom{14}{2} = 91$ for $0 \le y < S$.
Then $\sum N(b_k) \ge 3 \times 91 = 273$, so $A \ge 46 + 273 = 319$.
For $p=4, q=14$, $\binom{4}{3} + \binom{4}{2}(14) = 4 + 84 = 88$.
With $N(b_k) \ge 0$ and at least one $b_k \ge S/4$, $N(S/4)$ is minimized when $x_1=S, x_2=\dots=x_{14}=0$, giving $N(S/4) = \binom{13}{2} = 78$.
Then $A \ge 88 + 78 = 166 \ge 136$.
For $p \ge 5$, $\binom{p}{3} + \binom{p}{2}(18-p)$ is minimized at $p=5$, giving $\binom{5}{3} + \binom{5}{2}(13) = 10 + 130 = 140 \ge 136$.

Thus, the minimum possible value of $A$ is 136.
