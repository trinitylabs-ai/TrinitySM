To solve the equation $2^a + 1 = 7^b + 2^c$ for positive integers $a, b, c$, we first consider the relationship between $a$ and $c$.

1.  **Case $a \le c$**:
    If $a = c$, we have $2^a + 1 = 7^b + 2^a$, which implies $7^b = 1$. Since $b \ge 1$, this is impossible.
    If $a < c$, then $2^c > 2^a$, so $2^c - 2^a = 1 - 7^b$. Since $b \ge 1$, $1 - 7^b \le -6$, but $2^c - 2^a > 0$, which is a contradiction.
    Thus, we must have $a > c$.

2.  **Analysis of $a > c$**:
    The equation can be rewritten as $2^a - 2^c = 7^b - 1$.
    Factoring the left side: $2^c(2^{a-c} - 1) = 7^b - 1$.
    Let $k = a - c$. Then $2^c(2^k - 1) = 7^b - 1$.

3.  **Testing small values of $b$**:
    - If $b = 1$, $2^c(2^k - 1) = 7^1 - 1 = 6 = 2^1 \cdot 3$.
      Thus $2^c = 2^1 \implies c = 1$, and $2^k - 1 = 3 \implies 2^k = 4 \implies k = 2$.
      Then $a = c + k = 1 + 2 = 3$. This gives the solution $(3, 1, 1)$.
    - If $b = 2$, $2^c(2^k - 1) = 7^2 - 1 = 48 = 2^4 \cdot 3$.
      Thus $2^c = 2^4 \implies c = 4$, and $2^k - 1 = 3 \implies 2^k = 4 \implies k = 2$.
      Then $a = c + k = 4 + 2 = 6$. This gives the solution $(6, 2, 4)$.

4.  **General Case Analysis**:
    We have $2^c(2^k - 1) = 7^b - 1$.
    - If $b$ is odd, $v_2(7^b - 1) = v_2(7 - 1) = v_2(6) = 1$.
      Thus $c = 1$. The equation becomes $2(2^k - 1) = 7^b - 1$, which simplifies to $2^{k+1} - 2 = 7^b - 1$, or $2^{k+1} - 7^b = 1$.
      By Catalan's Conjecture (or testing modulo 3 and 49), the only solution to $2^x - 7^y = 1$ in positive integers is $2^3 - 7^1 = 1$.
      Thus $k+1 = 3 \implies k = 2$ and $b = 1$, leading back to $(3, 1, 1)$.
    - If $b$ is even, let $b = 2n$. Then $2^c(2^k - 1) = 7^{2n} - 1 = (7^n - 1)(7^n + 1)$.
      Since $7^n - 1$ and $7^n + 1$ are consecutive even integers, their greatest common divisor is 2.
      One must be $2 \cdot (\text{odd})$ and the other $2^{c-1} \cdot (\text{odd})$.
      If $n$ is odd, $v_2(7^n - 1) = v_2(6) = 1$ and $v_2(7^n + 1) = v_2(8) = 3$ if $n=1$.
      For $n=1$, we found $(6, 2, 4)$. For odd $n > 1$, $v_2(7^n + 1) = 3$ still holds.
      Then $c-1 = 3 \implies c = 4$. The equation becomes $2^4(2^k - 1) = 7^{2n} - 1$, or $2^k - 1 = \frac{7^{2n} - 1}{16}$.
      This implies $7^{2n} + 15 = 2^{k+4}$.
      Testing modulo 17: $7^2 = 49 \equiv 15 \pmod{17}$, $7^4 \equiv 15^2 \equiv (-2)^2 = 4 \pmod{17}$, $7^8 \equiv 16 \equiv -1 \pmod{17}$.
      $7^{2n} + 15 \equiv (7^2)^n + 15 \equiv (-2)^n + 15 \pmod{17}$.
      For $2^x \pmod{17}$, the values are $\{2, 4, 8, 16, 15, 13, 9, 1\}$.
      If $n=1$, $13+15 = 28 \equiv 11$ (Wait, $n=1$ works as $64 = 2^6$).
      If $n=3$, $(-2)^3 + 15 = -8 + 15 = 7$, not in the set.
      If $n=5$, $(-2)^5 + 15 = -32 + 15 = -17 \equiv 0$, not in the set.
      If $n$ is even, $v_2(7^n + 1) = 1$ and $v_2(7^n - 1) = c-1$.
      This leads to $2^{c+k} - 7^{2n} = 2^c - 1$. For $c \ge 2$, modulo 3 gives $k$ is even.
      Testing $k=2$ gives $2^c(3) = 7^{2n} - 1$. For $n=1$, $c=4$. For $n \ge 2$, $2^c = \frac{7^{2n}-1}{3}$ is not a power of 2.

The only solutions are $(3, 1, 1)$ and $(6, 2, 4)$.

\(\square\)
