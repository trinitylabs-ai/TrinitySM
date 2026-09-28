To find all positive integer solutions $(a, b, c)$ to the equation $2^a + 1 = 7^b + 2^c$, we analyze the relationship between $a$ and $c$.

**Case 1: $a \le c$**
If $a = c$, the equation becomes $2^a + 1 = 7^b + 2^a$, which implies $7^b = 1$. Since $b \ge 1$, this is impossible.
If $a < c$, we have $2^c - 2^a = 1 - 7^b$. Since $b \ge 1$, the right side $1 - 7^b \le -6$, but the left side $2^a(2^{c-a} - 1)$ is positive. Thus, no solutions exist for $a \le c$.

**Case 2: $a > c$**
Rearranging the equation gives $2^a - 2^c = 7^b - 1$, which factors as:
\[ 2^c(2^{a-c} - 1) = 7^b - 1 \]
Let $k = a - c$. The equation is $2^c(2^k - 1) = 7^b - 1$.

**Subcase 2.1: $b$ is odd**
If $b$ is odd, we consider the equation modulo 4. Since $7 \equiv -1 \pmod 4$, $7^b - 1 \equiv (-1)^b - 1 \equiv -2 \equiv 2 \pmod 4$.
This implies $v_2(7^b - 1) = 1$, where $v_2(n)$ is the exponent of the highest power of 2 dividing $n$.
Comparing this to $2^c(2^k - 1)$, we must have $c = 1$. The equation becomes $2(2^k - 1) = 7^b - 1$, which simplifies to $2^{k+1} - 1 = 7^b$.
For $b = 1$, $2^{k+1} - 1 = 7 \implies 2^{k+1} = 8 \implies k = 2$. This gives $c = 1, a = 1 + 2 = 3$.
Checking: $2^3 + 1 = 9$ and $7^1 + 2^1 = 9$. Thus, $(3, 1, 1)$ is a solution.
For $b > 1$, $2^{k+1} - 1 = 7^b$ implies $2^{k+1} \equiv 1 \pmod 7$, so $k+1 = 3m$. Then $2^{3m} - 1 = (2^m - 1)(2^{2m} + 2^m + 1) = 7^b$. Both factors must be powers of 7. However, the difference $(2^{2m} + 2^m + 1) - (2^m - 1)^2 = 3 \cdot 2^m$ is not divisible by 7, meaning $2^m - 1$ must be 1, so $m=1, b=1$.

**Subcase 2.2: $b$ is even**
Let $b = 2n$. By the Lifting The Exponent Lemma, $v_2(7^b - 1) = v_2(7-1) + v_2(7+1) + v_2(b) - 1 = 1 + 3 + v_2(b) - 1 = v_2(b) + 3$.
Thus, $c = v_2(b) + 3$. The original equation is $2^{c+k} - 7^b = 2^c - 1$.
If $c+k$ is even, let $c+k = 2m$. Then $(2^m - 7^n)(2^m + 7^n) = 2^c - 1$.
This implies $2^m + 7^n \le 2^c - 1$. Since $c = v_2(b) + 3$, we have $7^n < 2^{v_2(b)+3}$.
Substituting $b=2n$, we get $7^n < 2^{v_2(n)+4}$.
For $n=1$, $7 < 16$ (True). For $n=2$, $49 < 32$ (False). For $n > 2$, $7^n$ grows much faster than $2^{v_2(n)+4}$.
Thus, we must have $n=1$, which means $b=2$.
Then $c = v_2(2) + 3 = 4$. The equation $2^{4+k} - 7^2 = 2^4 - 1$ gives $2^{4+k} - 49 = 15 \implies 2^{4+k} = 64 \implies k = 2$.
This gives $c = 4, a = 4 + 2 = 6$.
Checking: $2^6 + 1 = 65$ and $7^2 + 2^4 = 49 + 16 = 65$. Thus, $(6, 2, 4)$ is a solution.

If $c+k$ is odd, $k$ must be even (from modulo 3). Then $c$ must be odd, so $v_2(b)$ is even. Let $b = 2^s m$ with $s$ even.
$2^c(2^k - 1) = 7^b - 1$. For $s \ge 2$, the odd part of $7^b - 1$ is $\frac{7^m-1}{2} \cdot \frac{7^m+1}{8} \cdot \prod_{j=1}^{s-1} \frac{7^{2^j m}+1}{2}$.
For $b=4$, $c=5$, $2^5(2^k - 1) = 2400 \implies 2^k = 76$ (No).
For $b \ge 8$, the product grows too rapidly to be of the form $2^k - 1$.

The only solutions are $(3, 1, 1)$ and $(6, 2, 4)$.

Final Answer: $(a, b, c) \in \{(3, 1, 1), (6, 2, 4)\}$ \(\square\)
