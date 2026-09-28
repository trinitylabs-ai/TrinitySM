To prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$, given $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for $n \ge 2$, we observe that the condition $x_{n-1} \mid x_n$ is equivalent to $x_{n-1} \mid 2^{x_{n-1}} + 2$. We will prove a stronger statement by induction.

**Claim:** For all integers $n \ge 1$, the value $2x_n(x_n - 1)$ divides $2^{x_n} + 2 - x_n$.

**Proof of Claim:**
We proceed by induction on $n$.

**Base Case:** For $n=1$, we have $x_1 = 6$.
The left-hand side is $2x_1(x_1 - 1) = 2(6)(5) = 60$.
The right-hand side is $2^{x_1} + 2 - x_1 = 2^6 + 2 - 6 = 64 + 2 - 6 = 60$.
Since $60$ divides $60$, the base case holds.

**Inductive Step:** Assume the claim holds for $n=k$; that is, $2x_k(x_k - 1) \mid 2^{x_k} + 2 - x_k$. Let $m = x_k$. The inductive hypothesis is $2m(m-1) \mid 2^m + 2 - m$. We wish to prove the claim for $n = k+1$. Let $x_{k+1} = 2^m + 2$. We must show that:
\[ 2x_{k+1}(x_{k+1} - 1) \mid 2^{x_{k+1}} + 2 - x_{k+1} \]
Substituting $x_{k+1} = 2^m + 2$ into the expression:
\[ 2(2^m + 2)(2^m + 1) \mid 2^{2^m + 2} + 2 - (2^m + 2) \]
\[ 4(2^{m-1} + 1)(2^m + 1) \mid 2^{2^m + 2} - 2^m \]
The right-hand side can be factored as $2^m(2^{2^m + 2 - m} - 1)$. Since $m = x_k \ge 6$, $2^m$ is divisible by 4. Thus, the divisibility condition is equivalent to:
\[ (2^{m-1} + 1)(2^m + 1) \mid 2^{m-2}(2^{2^m + 2 - m} - 1) \]
Since $2^{m-1} + 1$ and $2^m + 1$ are odd, they are coprime to $2^{m-2}$. Thus, we only need to show that:
\[ (2^{m-1} + 1)(2^m + 1) \mid 2^{2^m + 2 - m} - 1 \]
We note that $\gcd(2^{m-1} + 1, 2^m + 1) = \gcd(2^{m-1} + 1, 2(2^{m-1} + 1) - 1) = \gcd(2^{m-1} + 1, 1) = 1$. Therefore, it suffices to show that $2^{m-1} + 1$ and $2^m + 1$ each divide $2^{2^m + 2 - m} - 1$.

1.  **Divisibility by $2^{m-1} + 1$**: The order of $2$ modulo $2^{m-1} + 1$ is $2(m-1)$. Thus, $2^{m-1} + 1 \mid 2^{2^m + 2 - m} - 1$ if and only if $2(m-1) \mid 2^m + 2 - m$. This is true because $2m(m-1) \mid 2^m + 2 - m$ by the inductive hypothesis.
2.  **Divisibility by $2^m + 1$**: The order of $2$ modulo $2^m + 1$ is $2m$. Thus, $2^m + 1 \mid 2^{2^m + 2 - m} - 1$ if and only if $2m \mid 2^m + 2 - m$. This is also true because $2m(m-1) \mid 2^m + 2 - m$ by the inductive hypothesis.

Since both conditions are satisfied, the inductive step is complete. By induction, $2x_n(x_n - 1) \mid 2^{x_n} + 2 - x_n$ for all $n \ge 1$.

**Conclusion:**
From the proven claim, we have $x_n \mid 2x_n(x_n - 1)$, so $x_n \mid 2^{x_n} + 2 - x_n$. This implies $x_n \mid 2^{x_n} + 2$. By the definition of the sequence, $x_{n+1} = 2^{x_n} + 2$, so we have $x_n \mid x_{n+1}$ for all $n \ge 1$. Consequently, $x_{n-1} \mid x_n$ for all $n \ge 2$.

\(\square\)
