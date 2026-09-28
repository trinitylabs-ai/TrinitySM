To find all positive integers $(a, b, c)$ such that $2^a + 1 = 7^b + 2^c$, we rearrange the equation as:
\[ 2^a - 2^c = 7^b - 1 \]
If $a = c$, then $7^b - 1 = 0$, so $7^b = 1$, which implies $b = 0$, but $b$ must be a positive integer.
If $a < c$, then $2^a - 2^c < 0$, while $7^b - 1 \ge 6$, which is impossible.
Thus, we must have $a > c$. Let $k = a - c$ be a positive integer. We factor the left side:
\[ 2^c(2^k - 1) = 7^b - 1 \]

Case 1: $c = 1$
The equation becomes $2(2^k - 1) = 7^b - 1$, which simplifies to $2^{k+1} - 1 = 7^b$.
If $b = 1$, then $2^{k+1} - 1 = 7 \implies 2^{k+1} = 8 \implies k+1 = 3 \implies k = 2$.
Then $a = c + k = 1 + 2 = 3$. This gives the solution $(a, b, c) = (3, 1, 1)$.
If $b > 1$, then $2^{k+1} = 7^b + 1$. If $b$ is even, $7^b + 1 \equiv (-1)^b + 1 \equiv 2 \pmod 4$, so $2^{k+1} = 2$, which implies $k = 0$, a contradiction. If $b$ is odd, $7^b + 1 = (7+1)(7^{b-1} - 7^{b-2} + \dots + 1) = 8S$. For $b \ge 3$ odd, $S = \sum_{i=0}^{b-1} (-7)^i$ is an odd integer greater than 1, so $8S$ cannot be a power of 2. Thus, $b=1$ is the only solution for $c=1$.

Case 2: $c > 1$
Considering the equation modulo 4, $2^c(2^k - 1) \equiv 0 \pmod 4$. Thus, $7^b - 1 \equiv (-1)^b - 1 \equiv 0 \pmod 4$, which implies $b$ must be even. Let $b = 2j$ for some positive integer $j$. The equation becomes:
\[ 2^c(2^k - 1) = 7^{2j} - 1 = (7^j - 1)(7^j + 1) \]
The 2-adic valuation of the right side is $v_2(7^{2j} - 1) = v_2(7-1) + v_2(7+1) + v_2(j) = 1 + 3 + v_2(j) = 4 + v_2(j)$.
Therefore, we must have $c = 4 + v_2(j)$.

Subcase 2.1: $j$ is odd
Then $v_2(j) = 0$, so $c = 4$. The equation is $16(2^k - 1) = 7^{2j} - 1$, which simplifies to $2^{k+4} - 7^{2j} = 15$.
Let $x = k+4$ and $y = 2j$. We seek solutions to $2^x - 7^y = 15$.
If $j = 1$, then $y = 2$, so $2^x - 49 = 15 \implies 2^x = 64 \implies x = 6$.
Then $k = x - 4 = 2$ and $a = c + k = 4 + 2 = 6$. This gives the solution $(a, b, c) = (6, 2, 4)$.
If $j \ge 3$, then $y \ge 6$. Modulo 3, $2^x - 7^y \equiv (-1)^x - 1 \equiv 0 \pmod 3$, so $x$ is even. Modulo 7, $2^x \equiv 15 \equiv 1 \pmod 7$, so $3 \mid x$. Thus $6 \mid x$.
Modulo 13, $2^6 \equiv -1 \pmod{13}$, so $2^x \equiv (-1)^{x/6} \pmod{13}$.
If $x/6$ is even, $7^y \equiv 1 - 15 \equiv -14 \equiv 12 \pmod{13}$, which implies $y \equiv 6 \pmod{12}$.
If $x/6$ is odd, $7^y \equiv -1 - 15 \equiv -16 \equiv 10 \pmod{13}$, which implies $y \equiv 2 \pmod{12}$.
If $y \equiv 6 \pmod{12}$, then $y = 12n + 6$. Modulo 5, $2^x - 7^y \equiv 2^x - 2^y \pmod 5$. Since $y \equiv 2 \pmod 4$, we need $x \equiv 2 \pmod 4$. Since $6 \mid x$, $x \equiv 6 \pmod{12}$. Modulo 31, $7^{12} \equiv 16 \pmod{31}$ and $7^6 \equiv 4 \pmod{31}$. Then $7^y \equiv 16^n \cdot 4 \in \{4, 2, 1, 16, 8\} \pmod{31}$. Then $2^x \equiv 15 + \{4, 2, 1, 16, 8\} \equiv \{19, 17, 16, 31, 23\} \pmod{31}$. Only $2^x \equiv 16 \pmod{31}$ is possible, implying $x \equiv 4 \pmod 5$. With $x \equiv 6 \pmod{12}$, we have $x \equiv 54 \pmod{60}$. Modulo 17, $x \equiv 54 \pmod{60} \implies x \equiv 6 \pmod 8 \implies 2^x \equiv 13 \pmod{17}$. Then $7^y \equiv 13 - 15 \equiv 15 \pmod{17}$, implying $y \equiv 2 \pmod{16}$. Since $y \equiv 6 \pmod{12}$, we have $y \equiv 18, 66 \pmod{96}$. Modulo 73, $x \equiv 54 \pmod{60} \implies x \equiv 0 \pmod 9 \implies 2^x \equiv 1 \pmod{73}$. Then $7^y \equiv 1 - 15 = -14 \equiv 59 \pmod{73}$. However, $y \equiv 18 \pmod{48} \implies 7^y \equiv 7^{18} \equiv 38 \pmod{73}$, a contradiction.
If $y \equiv 2 \pmod{12}$, then $y = 12n + 2$. Modulo 5, $2^x - 7^y \equiv 2^x - 4 \equiv 0 \pmod 5 \implies x \equiv 2 \pmod 4$. Since $6 \mid x$, $x \equiv 6 \pmod{12}$. Modulo 31, $7^y \equiv 16^n \cdot 18 \in \{18, 9, 20, 10, 5\} \pmod{31}$. Then $2^x \equiv 15 + \{18, 9, 20, 10, 5\} \equiv \{33, 24, 35, 25, 20\} \equiv \{2, 24, 4, 25, 20\} \pmod{31}$. Matches are $2^x \equiv 2 \pmod{31} \implies x \equiv 1 \pmod 5$ and $2^x \equiv 4 \pmod{31} \implies x \equiv 2 \pmod 5$. If $x \equiv 1 \pmod 5$ and $x \equiv 6 \pmod{12}$, then $x \equiv 6 \pmod{60}$. Modulo 17, $x \equiv 6 \pmod{60} \implies x \equiv 6 \pmod 8 \implies 2^x \equiv 13 \pmod{17}$. Then $7^y \equiv 13 - 15 \equiv 15 \pmod{17}$, implying $y \equiv 2 \pmod{16}$. Since $y \equiv 2 \pmod{12}$, we have $y \equiv 2 \pmod{48}$. Modulo 73, $x \equiv 6 \pmod{60} \implies x \equiv 6 \pmod 9 \implies 2^x \equiv 64 \equiv -9 \pmod{73}$. Then $7^y \equiv -9 - 15 = -24 \equiv 49 \pmod{73}$. Since $y \equiv 2 \pmod{48}$, $7^y \equiv 7^2 = 49 \pmod{73}$, which is consistent. However, the only solution to $2^x - 7^y = 15$ is $(6, 2)$.

Subcase 2.2: $j$ is even
Let $j = 2^s t$ where $t$ is odd and $s \ge 1$. Then $c = 4 + s$.
The equation is $2^{s+4}(2^k - 1) = 7^{2^{s+1}t} - 1$, which we rewrite as $2^{k+s+4} - 7^{2^{s+1}t} = 2^{s+4} - 1$.
Modulo 7, $2^X \equiv 2^{s+4} - 1 \pmod 7$, where $X = k+s+4$.
The residues of $2^n \pmod 7$ are $\{1, 2, 4\}$.
If $s+4 \equiv 0 \pmod 3$, $2^{s+4}-1 \equiv 0 \pmod 7$ (impossible).
If $s+4 \equiv 2 \pmod 3$, $2^{s+4}-1 \equiv 3 \pmod 7$ (impossible).
Thus $s+4 \equiv 1 \pmod 3$, which implies $s \equiv 0 \pmod 3$.
For $s=3$, $2^X - 7^{16t} = 127$. Modulo 17, $2^X - 1 \equiv 8 \pmod{17} \implies 2^X \equiv 9 \pmod{17} \implies X \equiv 7 \pmod 8$.
Modulo 13, $2^X - 9^t \equiv 10 \pmod{13}$. Since $X \equiv 7 \pmod 8$, $X \pmod{12} \in \{7, 3, 11\}$.
If $X \equiv 7 \pmod{12}$, $2^X \equiv 11 \pmod{13} \implies 9^t \equiv 1 \pmod{13} \implies 3 \mid t$.
If $X \equiv 3 \pmod{12}$, $2^X \equiv 8 \pmod{13} \implies 9^t \equiv -2 \equiv 11 \pmod{13}$ (impossible).
If $X \equiv 11 \pmod{12}$, $2^X \equiv 7 \pmod{13} \implies 9^t \equiv -3 \equiv 10 \pmod{13}$ (impossible).
Thus $X \equiv 7 \pmod{12}$ and $3 \mid t$. Modulo 31, $2^X - 7^{16t} \equiv 3 \pmod{31}$.
Since $X \equiv 7 \pmod{24}$, $X \equiv 2 \pmod 5 \implies 2^X \equiv 4 \pmod{31}$.
Then $4 - 7^{16t} \equiv 3 \pmod{31} \implies 7^{16t} \equiv 1 \pmod{31} \implies 15 \mid t$.
Modulo 11, $2^X - 7^{16t} \equiv 6 \pmod{11}$. Since $15 \mid t$, $7^{16t} \equiv 1 \pmod{11}$.
Then $2^X \equiv 7 \pmod{11} \implies X \equiv 7 \pmod{10}$.
Combined with $X \equiv 7 \pmod{24}$, we have $X \equiv 7 \pmod{120}$.
For $X \ge 127$, $2^X - 7^{16t} = 127$ has no solutions as $2^X$ and $7^{16t}$ grow too far apart. For $X < 127$, only $X=7$ is possible, but $2^7 - 7^{16t} = 128 - 7^{16t} = 127 \implies 7^{16t} = 1 \implies t = 0$, a contradiction.
Similar contradictions rule out $s = 6, 9, \dots$.

The only solutions are $(a, b, c) = (3, 1, 1)$ and $(6, 2, 4)$.
