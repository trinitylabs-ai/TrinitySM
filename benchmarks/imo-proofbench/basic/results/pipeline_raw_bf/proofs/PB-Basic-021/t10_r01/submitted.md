To prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$, where $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for $n \ge 2$, we use the method of induction on two intertwined properties.

Let $P(n)$ be the statement: $x_n \mid x_{n+1}$ for $n \ge 1$.
Let $Q(n)$ be the statement: $(x_n - 1) \mid (2^{x_n} + 1)$ for $n \ge 1$.

**1. Base Cases**
For $n=1$:
- $x_1 = 6$.
- $x_2 = 2^{x_1} + 2 = 2^6 + 2 = 66$.
Since $66 = 6 \times 11$, $x_1 \mid x_2$ is true, so $P(1)$ holds.
- $x_1 - 1 = 5$.
- $2^{x_1} + 1 = 2^6 + 1 = 65$.
Since $65 = 5 \times 13$, $(x_1 - 1) \mid (2^{x_1} + 1)$ is true, so $Q(1)$ holds.

**2. Proof that $Q(n) \implies P(n+1)$**
Assume $Q(n)$ is true: $(x_n - 1) \mid (2^{x_n} + 1)$.
We wish to show $P(n+1)$, which is $x_{n+1} \mid x_{n+2}$.
By the definition of the sequence:
$x_{n+1} = 2^{x_n} + 2 = 2(2^{x_n-1} + 1)$
$x_{n+2} = 2^{x_{n+1}} + 2 = 2(2^{x_{n+1}-1} + 1)$
Thus, $x_{n+1} \mid x_{n+2}$ is equivalent to:
$2(2^{x_n-1} + 1) \mid 2(2^{x_{n+1}-1} + 1) \iff (2^{x_n-1} + 1) \mid (2^{x_{n+1}-1} + 1)$
We use the lemma that $a^m + 1 \mid a^k + 1$ if and only if $k/m$ is an odd integer.
Here, $a=2$, $m = x_n - 1$, and $k = x_{n+1} - 1$.
The ratio is:
$$\frac{k}{m} = \frac{x_{n+1} - 1}{x_n - 1} = \frac{2^{x_n} + 2 - 1}{x_n - 1} = \frac{2^{x_n} + 1}{x_n - 1}$$
By the inductive hypothesis $Q(n)$, this ratio is an integer. Furthermore, since both $2^{x_n} + 1$ and $x_n - 1$ are odd, their quotient must be odd. Thus, the condition for the lemma is satisfied, and $(2^{x_n-1} + 1) \mid (2^{x_{n+1}-1} + 1)$ holds. Therefore, $P(n+1)$ is true.

**3. Proof that $P(n) \implies Q(n+1)$**
Assume $P(n)$ is true: $x_n \mid x_{n+1}$.
We wish to show $Q(n+1)$, which is $(x_{n+1} - 1) \mid (2^{x_{n+1}} + 1)$.
Substituting the definition $x_{n+1} - 1 = 2^{x_n} + 1$, this is:
$$(2^{x_n} + 1) \mid (2^{x_{n+1}} + 1)$$
Applying the same lemma as before, this holds if the ratio of the exponents $\frac{x_{n+1}}{x_n}$ is an odd integer.
From $P(n)$, we know $x_{n+1}/x_n$ is an integer. We now check if it is odd:
$$\frac{x_{n+1}}{x_n} = \frac{2^{x_n} + 2}{x_n} = \frac{2(2^{x_n-1} + 1)}{x_n}$$
For $n=1$, $x_2/x_1 = 66/6 = 11$, which is odd.
For $n \ge 2$, $x_n = 2^{x_{n-1}} + 2 = 2(2^{x_{n-1}-1} + 1)$.
Substituting this into the ratio:
$$\frac{x_{n+1}}{x_n} = \frac{2(2^{x_n-1} + 1)}{2(2^{x_{n-1}-1} + 1)} = \frac{2^{x_n-1} + 1}{2^{x_{n-1}-1} + 1}$$
Since $x_n$ and $x_{n-1}$ are positive, both the numerator and denominator are odd. The quotient of two odd integers, if it is an integer, must be odd. Thus, $x_{n+1}/x_n$ is odd, and $Q(n+1)$ is true.

**4. Conclusion**
We have shown:
- $P(1)$ is true and $Q(1)$ is true.
- $Q(n) \implies P(n+1)$.
- $P(n) \implies Q(n+1)$.
By induction, $P(n)$ is true for all $n \ge 1$. Specifically, for any $n \ge 2$, $P(n-1)$ is true, which means $x_{n-1} \mid x_n$.

\(\square\)
