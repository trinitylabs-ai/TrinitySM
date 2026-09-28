To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we rearrange the equation as follows:
\[a^2 - 1 = ab + b^3\]
\[(a-1)(a+1) = b(a + b^2)\]
Since $b$ is a prime number and it divides the product $(a-1)(a+1)$, by Euclid's Lemma, $b$ must divide at least one of the factors. Thus, we have two cases: $b \mid (a-1)$ or $b \mid (a+1)$.

**Case 1: $b \mid (a-1)$**
Let $a-1 = nb$ for some positive integer $n$. Then $a = nb + 1$. Substituting this into the original equation:
\[(nb+1)^2 - (nb+1)b - b^3 = 1\]
\[n^2b^2 + 2nb + 1 - nb^2 - b - b^3 = 1\]
\[-b^3 + (n^2-n)b^2 + (2n-1)b = 0\]
Since $b$ is prime, $b \neq 0$, so we divide by $b$:
\[-b^2 + (n^2-n)b + (2n-1) = 0 \implies b^2 - (n^2-n)b - (2n-1) = 0\]
Using the quadratic formula to solve for $b$:
\[b = \frac{(n^2-n) \pm \sqrt{(n^2-n)^2 + 4(2n-1)}}{2}\]
Let $D_n = (n^2-n)^2 + 8n - 4$. For $b$ to be an integer, $D_n$ must be a perfect square.
- For $n=1$, $D_1 = 0 + 8 - 4 = 4 = 2^2$, so $b = \frac{0 \pm 2}{2} = \pm 1$ (not prime).
- For $n=2$, $D_2 = 2^2 + 16 - 4 = 16 = 4^2$, so $b = \frac{2 \pm 4}{2} = 3$ or $-1$. If $b=3$, then $a = 2(3)+1 = 7$. Since both 7 and 3 are prime, $(7, 3)$ is a solution.
- For $n=3$, $D_3 = 6^2 + 24 - 4 = 56$ (not a square).
- For $n=4$, $D_4 = 12^2 + 32 - 4 = 172$ (not a square).
- For $n \ge 5$, we observe that $(n^2-n)^2 < D_n$. Also, $(n^2-n+1)^2 = (n^2-n)^2 + 2(n^2-n) + 1 = n^4 - 2n^3 + 3n^2 - 2n + 1$. Comparing $D_n$ and $(n^2-n+1)^2$:
\[(n^2-n+1)^2 - D_n = (n^4 - 2n^3 + 3n^2 - 2n + 1) - (n^4 - 2n^3 + n^2 + 8n - 4) = 2n^2 - 10n + 5\]
The quadratic $2n^2 - 10n + 5$ is positive for $n \ge 5$ (the larger root is $\frac{10+\sqrt{60}}{4} \approx 4.43$). Thus, for $n \ge 5$, $(n^2-n)^2 < D_n < (n^2-n+1)^2$, meaning $D_n$ cannot be a square.

**Case 2: $b \mid (a+1)$**
Let $a+1 = nb$ for some positive integer $n$. Then $a = nb - 1$. Substituting this into the original equation:
\[(nb-1)^2 - (nb-1)b - b^3 = 1\]
\[n^2b^2 - 2nb + 1 - nb^2 + b - b^3 = 1\]
\[-b^3 + (n^2-n)b^2 + (1-2n)b = 0\]
Dividing by $b$:
\[-b^2 + (n^2-n)b + (1-2n) = 0 \implies b^2 - (n^2-n)b + (2n-1) = 0\]
Using the quadratic formula to solve for $b$:
\[b = \frac{(n^2-n) \pm \sqrt{(n^2-n)^2 - 4(2n-1)}}{2}\]
Let $D_n = (n^2-n)^2 - 8n + 4$.
- For $n=1, 2$, $D_n < 0$.
- For $n=3$, $D_3 = 6^2 - 24 + 4 = 16 = 4^2$, so $b = \frac{6 \pm 4}{2} = 5$ or $1$. If $b=5$, then $a = 3(5)-1 = 14$ (not prime).
- For $n=4$, $D_4 = 12^2 - 32 + 4 = 116$ (not a square).
- For $n \ge 5$, we observe that $D_n < (n^2-n)^2$ because $-8n+4 < 0$. Also, $(n^2-n-1)^2 = (n^2-n)^2 - 2(n^2-n) + 1 = n^4 - 2n^3 - n^2 + 2n + 1$. Comparing $D_n$ and $(n^2-n-1)^2$:
\[D_n - (n^2-n-1)^2 = (n^4 - 2n^3 + n^2 - 8n + 4) - (n^4 - 2n^3 - n^2 + 2n + 1) = 2n^2 - 10n + 3\]
The quadratic $2n^2 - 10n + 3$ is positive for $n \ge 5$ (the larger root is $\frac{10+\sqrt{76}}{4} \approx 4.69$). Thus, for $n \ge 5$, $(n^2-n-1)^2 < D_n < (n^2-n)^2$, meaning $D_n$ cannot be a square.

Checking the only candidate pair $(7, 3)$:
$7^2 - 7(3) - 3^3 = 49 - 21 - 27 = 1$.

The only pair of primes $(a, b)$ satisfying the equation is $(7, 3)$.

\(\square\)
