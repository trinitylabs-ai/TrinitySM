To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we begin by rearranging the equation to isolate the prime $b$.

The given equation is:
\[ a^2 - 1 = ab + b^3 \]
Factoring both sides:
\[ (a-1)(a+1) = b(a + b^2) \]
Since $b$ is a prime number and divides the product $(a-1)(a+1)$, by Euclid's Lemma, $b$ must divide either $a-1$ or $a+1$. This leads us to two cases.

**Case 1: $b$ divides $a-1$**
Let $a-1 = nb$ for some positive integer $n$. Then $a = nb + 1$. Substituting this into the original equation:
\[ (nb+1)^2 - (nb+1)b - b^3 = 1 \]
\[ n^2b^2 + 2nb + 1 - nb^2 - b - b^3 = 1 \]
\[ n^2b^2 + 2nb - nb^2 - b - b^3 = 0 \]
Since $b$ is a prime, $b \neq 0$, so we can divide by $b$:
\[ n^2b + 2n - nb - 1 - b^2 = 0 \]
Rearranging this as a quadratic in $b$:
\[ b^2 + (n-n^2)b + (1-2n) = 0 \]
Using the quadratic formula to solve for $b$:
\[ b = \frac{(n^2-n) \pm \sqrt{(n-n^2)^2 - 4(1-2n)}}{2} = \frac{n^2-n \pm \sqrt{n^4 - 2n^3 + n^2 + 8n - 4}}{2} \]
For $b$ to be an integer, the discriminant $D = n^4 - 2n^3 + n^2 + 8n - 4$ must be a perfect square.
- For $n=1$, $D = 1-2+1+8-4 = 4 = 2^2$. Then $b = \frac{0 \pm 2}{2} = \pm 1$. (Not prime)
- For $n=2$, $D = 16-16+4+16-4 = 16 = 4^2$. Then $b = \frac{2 \pm 4}{2}$. Thus $b=3$ or $b=-1$. For $b=3$, $a = 2(3)+1 = 7$. Check: $7^2 - 7(3) - 3^3 = 49 - 21 - 27 = 1$. (Valid)
- For $n=3$, $D = 81-54+9+24-4 = 56$. (Not a square)
- For $n=4$, $D = 256-128+16+32-4 = 172$. (Not a square)
- For $n \ge 5$, we observe that $(n^2-n)^2 = n^4 - 2n^3 + n^2$. Since $8n-4 > 0$, $D > (n^2-n)^2$.
Also, $(n^2-n+1)^2 = n^4 - 2n^3 + 3n^2 - 2n + 1$.
The difference $(n^2-n+1)^2 - D = 2n^2 - 10n + 5$. For $n=5$, $50-50+5=5 > 0$. For $n > 5$, the derivative $4n-10$ is positive. Thus $D < (n^2-n+1)^2$ for $n \ge 5$.
Since $D$ lies strictly between two consecutive squares for $n \ge 5$, it cannot be a square.

**Case 2: $b$ divides $a+1$**
Let $a+1 = nb$ for some positive integer $n$. Then $a = nb - 1$. Substituting this into the original equation:
\[ (nb-1)^2 - (nb-1)b - b^3 = 1 \]
\[ n^2b^2 - 2nb + 1 - nb^2 + b - b^3 = 1 \]
\[ n^2b^2 - 2nb - nb^2 + b - b^3 = 0 \]
Dividing by $b$:
\[ n^2b - 2n - nb + 1 - b^2 = 0 \]
Rearranging as a quadratic in $b$:
\[ b^2 + (n-n^2)b + (2n-1) = 0 \]
Solving for $b$:
\[ b = \frac{(n^2-n) \pm \sqrt{(n-n^2)^2 - 4(2n-1)}}{2} = \frac{n^2-n \pm \sqrt{n^4 - 2n^3 + n^2 - 8n + 4}}{2} \]
Let $D = n^4 - 2n^3 + n^2 - 8n + 4$.
- For $n=1$, $D = 1-2+1-8+4 = -4$.
- For $n=2$, $D = 16-16+4-16+4 = -8$.
- For $n=3$, $D = 81-54+9-24+4 = 16 = 4^2$. Then $b = \frac{6 \pm 4}{2}$. Thus $b=5$ or $b=1$. For $b=5$, $a = 3(5)-1 = 14$. (Not prime)
- For $n=4$, $D = 256-128+16-32+4 = 116$. (Not a square)
- For $n \ge 5$, we observe that $D < (n^2-n)^2$ since $8n-4 > 0$.
Also, $(n^2-n-1)^2 = n^4 - 2n^3 - n^2 + 2n + 1$.
The difference $D - (n^2-n-1)^2 = 2n^2 - 10n + 3$. For $n=5$, $50-50+3 = 3 > 0$. For $n > 5$, the derivative $4n-10$ is positive. Thus $D > (n^2-n-1)^2$ for $n \ge 5$.
Since $D$ lies strictly between two consecutive squares for $n \ge 5$, it cannot be a square.

The only pair of primes that satisfies the equation is $(7, 3)$.

\(\square\)
