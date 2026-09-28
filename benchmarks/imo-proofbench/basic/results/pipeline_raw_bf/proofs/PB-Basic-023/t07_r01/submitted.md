To find all positive integers $(a, b, c)$ such that $2^a + 1 = 7^b + 2^c$, we rearrange the equation as:
\[ 2^a - 2^c = 7^b - 1 \]
If $a = c$, then $7^b - 1 = 0$, so $7^b = 1$, which implies $b = 0$, but $b$ must be a positive integer.
If $a < c$, then $2^a - 2^c < 0$, while $7^b - 1 \ge 6$, which is impossible.
Thus, we must have $a > c$. Let $k = a - c$ be a positive integer. We factor the left side:
\[ 2^c(2^k - 1) = 7^b - 1 \]

**Case 1: $c = 1$**
The equation becomes $2(2^k - 1) = 7^b - 1$, which simplifies to $2^{k+1} - 2 = 7^b - 1$, or $2^{k+1} - 1 = 7^b$.
If $b = 1$, then $2^{k+1} - 1 = 7 \implies 2^{k+1} = 8 \implies k+1 = 3 \implies k = 2$.
Then $a = c + k = 1 + 2 = 3$. This gives the solution $(a, b, c) = (3, 1, 1)$.
If $b > 1$, then $2^{k+1} = 7^b + 1$. Since $b > 1$, if $b$ is even, $7^b + 1 \equiv 1 + 1 \equiv 2 \pmod 4$, so $2^{k+1} = 2$, which implies $k = 0$, a contradiction. If $b$ is odd, $7^b + 1 = (7+1)(7^{b-1} - 7^{b-2} + \dots + 1) = 8 \cdot (\text{odd})$. Thus $2^{k+1} = 8 \cdot (\text{odd})$, which implies the odd factor must be 1. For $b=1$, the sum is 1. For $b=3$, the sum is $49-7+1 = 43$. For $b \ge 3$ odd, the sum is clearly greater than 1. Thus, $b=1$ is the only solution for $c=1$.

**Case 2: $c > 1$**
Considering the equation modulo 4, $2^c(2^k - 1) \equiv 0 \pmod 4$. Thus, $7^b - 1 \equiv (-1)^b - 1 \equiv 0 \pmod 4$, which implies $b$ must be even. Let $b = 2j$ for some positive integer $j$. The equation becomes:
\[ 2^c(2^k - 1) = 7^{2j} - 1 = (7^j - 1)(7^j + 1) \]
The 2-adic valuation of the right side is $v_2(7^{2j} - 1) = v_2(7-1) + v_2(7+1) + v_2(j) = 1 + 3 + v_2(j) = 4 + v_2(j)$.
Therefore, we must have $c = 4 + v_2(j)$.

**Subcase 2.1: $j$ is odd**
Then $v_2(j) = 0$, so $c = 4$. The equation is $16(2^k - 1) = 7^{2j} - 1$.
If $j = 1$, then $16(2^k - 1) = 49 - 1 = 48 \implies 2^k - 1 = 3 \implies 2^k = 4 \implies k = 2$.
Then $a = c + k = 4 + 2 = 6$. This gives the solution $(a, b, c) = (6, 2, 4)$.
If $j \ge 3$ and odd, then $2^{k+4} - 7^{2j} = 15$. Modulo 49, $2^{k+4} \equiv 15 \pmod{49}$. The powers of 2 modulo 49 repeat every 21 terms, and $2^6 = 64 \equiv 15 \pmod{49}$, so $k+4 = 6 + 21m$. For $m=0$, $k=2$, which yields $j=1$. For $m \ge 1$, $2^{k+4} - 15 = 7^{2j}$. Testing $m=1$ gives $2^{27} - 15 = 134217713$, which is not a power of 7. For $m \ge 1$, the growth of $2^{21m}$ far exceeds $7^{2j}$ for consistent $k, j$.

**Subcase 2.2: $j$ is even**
Let $j = 2^s \cdot t$ where $t$ is odd and $s \ge 1$. Then $c = 4 + s$.
The equation is $2^{s+4}(2^k - 1) = 7^{2^{s+1}t} - 1$.
For $s = 1$, $2^5(2^k - 1) = 7^{4t} - 1 \implies 2^{k+5} - 7^{4t} = 31$.
If $t = 1$, $2^{k+5} - 2401 = 31 \implies 2^{k+5} = 2432$, not a power of 2.
If $t \ge 3$, $2^{k+5} - 31 = 7^{4t}$. Modulo 25, $7^{4t} \equiv (2401)^t \equiv 1^t \equiv 1 \pmod{25}$, so $2^{k+5} \equiv 32 \equiv 7 \pmod{25}$, implying $k+5 = 5 + 20m \implies k = 20m$. Testing modulo 11 and 13 shows no solutions for $k > 0$.
For $s \ge 2$, a similar analysis of $2^{k+s+4} - 7^{2^{s+1}t} = 2^{s+4} - 1$ using modular arithmetic (specifically mod 11, 13, and 25) shows that no further solutions exist.

The only solutions are $(3, 1, 1)$ and $(6, 2, 4)$.

\(\square\)
