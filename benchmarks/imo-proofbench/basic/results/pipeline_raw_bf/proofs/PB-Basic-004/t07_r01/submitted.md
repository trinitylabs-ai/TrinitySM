To find all strictly increasing surjective functions $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$, we proceed as follows:

**1. Analysis of Iterates**
Since $g$ is strictly increasing and surjective, it is a homeomorphism of the real line. Specifically, $g$ is a bijection, and its inverse $g^{-1}$ is also strictly increasing. For any $x_0 \in \mathbb{R}$, we can define a sequence $\{x_n\}_{n \in \mathbb{Z}}$ by the recurrence $x_{n+1} = g(x_n)$.
The given equation $g(g(x)) = g(x) + 20x$ implies that for any $n \in \mathbb{Z}$:
\[ x_{n+2} = x_{n+1} + 20x_n \]
This is a linear homogeneous recurrence relation with constant coefficients. The characteristic equation is:
\[ r^2 - r - 20 = 0 \implies (r-5)(r+4) = 0 \]
The roots are $r_1 = 5$ and $r_2 = -4$. Thus, the general solution for $x_n$ is:
\[ x_n = A \cdot 5^n + B \cdot (-4)^n \]
where $A$ and $B$ are constants determined by $x_0$ and $x_1 = g(x_0)$. Specifically:
\[ x_0 = A + B, \quad x_1 = 5A - 4B \]

**2. Monotonicity and the Coefficient $B$**
Because $g$ is strictly increasing, the sequence $\{x_n\}$ must be monotonic. That is, if $x_1 > x_0$, then $x_{n+1} > x_n$ for all $n \in \mathbb{Z}$. If $x_1 < x_0$, then $x_{n+1} < x_n$ for all $n \in \mathbb{Z}$. If $x_1 = x_0$, then $x_n$ is constant for all $n$.
The difference between consecutive terms is:
\[ x_{n+1} - x_n = A(5^{n+1} - 5^n) + B((-4)^{n+1} - (-4)^n) = 4A \cdot 5^n - 5B \cdot (-4)^n \]
We examine the behavior of this difference as $n \to -\infty$. We can factor out $(-4)^n$:
\[ x_{n+1} - x_n = (-4)^n \left[ 4A \left( \frac{5}{-4} \right)^n - 5B \right] \]
As $n \to -\infty$, the term $\left( \frac{5}{-4} \right)^n \to 0$. Therefore, for sufficiently large negative $n$, the sign of the bracketed expression $[4A(-1.25)^n - 5B]$ is determined by the sign of $-5B$.
If $B \neq 0$, the term $(-4)^n$ alternates in sign for each successive $n$. Consequently, $x_{n+1} - x_n$ would alternate in sign as $n \to -\infty$, which contradicts the requirement that the sequence $\{x_n\}$ is monotonic. Thus, we must have $B = 0$ for every $x_0 \in \mathbb{R}$.

**3. Solving for $g(x)$**
Since $B = 0$ for all $x_0$, the general form of the sequence simplifies to $x_n = A \cdot 5^n$.
Using $n=0$, we have $x_0 = A \cdot 5^0 = A$.
Using $n=1$, we have $x_1 = g(x_0) = A \cdot 5^1 = 5A$.
Substituting $A = x_0$, we obtain:
\[ g(x_0) = 5x_0 \]
for all $x_0 \in \mathbb{R}$.

**4. Verification**
We verify if $g(x) = 5x$ satisfies all the conditions of the problem:
- **Strictly increasing**: $g'(x) = 5 > 0$, so $g$ is strictly increasing.
- **Surjective**: For any $y \in \mathbb{R}$, $g(y/5) = y$, so $g$ is surjective.
- **Functional Equation**: $g(g(x)) = 5(5x) = 25x$ and $g(x) + 20x = 5x + 20x = 25x$.
The equation $25x = 25x$ holds for all $x \in \mathbb{R}$.

The only function satisfying the given conditions is $g(x) = 5x$.

\(\square\)
