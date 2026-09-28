To determine all non-negative integers $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number, we analyze the structure of the expression.

First, let $k = n^2+n+1$. For any non-negative integer $n$, $k$ is a positive integer. Since $n(n+1)$ is always even, $k = n(n+1) + 1$ is always an odd integer, and its minimum value is $k = 0^2+0+1 = 1$.

The expression for $A_n$ can be rewritten by expressing the base 9 as a power of 3:
\[ A_n = 1 + 3^{20k} + (3^2)^{14k} = 1 + 3^{20k} + 3^{28k} \]
To simplify this, we let $z = 3^{4k}$. Then $3^{20k} = (3^{4k})^5 = z^5$ and $3^{28k} = (3^{4k})^7 = z^7$. Substituting these into the equation for $A_n$, we obtain:
\[ A_n = z^7 + z^5 + 1 \]
We examine the polynomial $P(z) = z^7 + z^5 + 1$. We check if it has a factor of the form $z^2 + z + 1$. Let $\omega$ be a primitive cube root of unity, such that $\omega^2 + \omega + 1 = 0$ and $\omega^3 = 1$. Evaluating $P(z)$ at $z = \omega$:
\[ P(\omega) = \omega^7 + \omega^5 + 1 = (\omega^3)^2 \cdot \omega + (\omega^3) \cdot \omega^2 + 1 = \omega + \omega^2 + 1 = 0 \]
Since $\omega$ is a root of $P(z)$, the polynomial $z^2 + z + 1$ must be a factor of $z^7 + z^5 + 1$. By polynomial division, we find:
\[ z^7 + z^5 + 1 = (z^2 + z + 1)(z^5 - z^4 + z^3 - z + 1) \]
To verify this factorization, we expand the product:
\[ (z^2 + z + 1)(z^5 - z^4 + z^3 - z + 1) = z^2(z^5 - z^4 + z^3 - z + 1) + z(z^5 - z^4 + z^3 - z + 1) + 1(z^5 - z^4 + z^3 - z + 1) \]
\[ = (z^7 - z^6 + z^5 - z^3 + z^2) + (z^6 - z^5 + z^4 - z^2 + z) + (z^5 - z^4 + z^3 - z + 1) \]
\[ = z^7 + z^5 + 1 \]
Thus, $A_n$ is the product of two integers: $F_1 = z^2 + z + 1$ and $F_2 = z^5 - z^4 + z^3 - z + 1$. For $A_n$ to be prime, one of these factors must be equal to 1.

For $n \ge 0$, we have $k \ge 1$, which implies $z = 3^{4k} \ge 3^4 = 81$.
1.  Evaluating $F_1$:
    \[ F_1 = z^2 + z + 1 \ge 81^2 + 81 + 1 = 6561 + 81 + 1 = 6643 > 1 \]
2.  Evaluating $F_2$:
    We can rewrite $F_2$ as:
    \[ F_2 = z^4(z - 1) + z(z^2 - 1) + 1 \]
    Since $z \ge 81$, it follows that $z - 1 > 0$ and $z^2 - 1 > 0$. Thus:
    \[ F_2 \ge 81^4(80) + 81(81^2 - 1) + 1 > 1 \]

Since $A_n$ is the product of two integers $F_1$ and $F_2$, both of which are strictly greater than 1 for all non-negative integers $n$, $A_n$ is always a composite number.

Therefore, there are no non-negative integers $n$ such that $A_n$ is prime.

\(\square\)
