To find all strictly increasing surjective functions $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$, we proceed as follows:

### 1. Construction of a Recurrence Relation
For any $x \in \mathbb{R}$, let us define a sequence $\{a_n\}_{n \geq 0}$ by $a_0 = x$ and $a_{n+1} = g(a_n)$ for all $n \geq 0$. By the given functional equation, we have:
\[ a_{n+2} = g(a_{n+1}) = g(g(a_n)) = g(a_n) + 20a_n = a_{n+1} + 20a_n. \]
This is a linear homogeneous recurrence relation with constant coefficients. The characteristic equation is $r^2 - r - 20 = 0$, which factors as $(r-5)(r+4) = 0$. The roots are $r_1 = 5$ and $r_2 = -4$. Thus, the general solution for the sequence is:
\[ a_n = A(x) 5^n + B(x) (-4)^n, \]
where $A(x)$ and $B(x)$ are constants determined by the initial conditions $a_0 = x$ and $a_1 = g(x)$. Solving for these constants:
\[ a_0 = A(x) + B(x) = x \]
\[ a_1 = 5A(x) - 4B(x) = g(x) \]
Multiplying the first equation by 4 and adding it to the second gives $9A(x) = g(x) + 4x$, so $A(x) = \frac{g(x) + 4x}{9}$. Substituting this back into the first equation gives $B(x) = x - \frac{g(x) + 4x}{9} = \frac{5x - g(x)}{9}$.

### 2. Extension to Negative Indices
Since $g$ is strictly increasing and surjective, it is a bijection from $\mathbb{R}$ to $\mathbb{R}$. Therefore, the inverse function $g^{-1}$ exists and is also strictly increasing. We can extend the sequence $\{a_n\}$ to all integers $n \in \mathbb{Z}$ by defining $a_{n-1} = g^{-1}(a_n)$. The recurrence $a_{n+2} = a_{n+1} + 20a_n$ remains valid for all $n \in \mathbb{Z}$ because $g(g(a_n)) = g(a_n) + 20a_n$ holds for any $a_n$ in the domain. Consequently, the general solution $a_n = A(x) 5^n + B(x) (-4)^n$ holds for all $n \in \mathbb{Z}$.

### 3. Monotonicity and Convergence
Because $g$ is strictly increasing, the sequence $\{a_n\}_{n \in \mathbb{Z}}$ must be monotonic for any $x$. If $g(x) > x$, then $a_1 > a_0$, which implies $a_{n+1} > a_n$ for all $n \in \mathbb{Z}$ by induction. Similarly, if $g(x) < x$, then $a_{n+1} < a_n$ for all $n \in \mathbb{Z}$. If $g(x) = x$, then $x = x + 20x$, which implies $x = 0$.

Consider the difference between consecutive terms:
\[ a_{n+1} - a_n = A(x)(5^{n+1} - 5^n) + B(x)((-4)^{n+1} - (-4)^n) = 4A(x) 5^n - 5B(x) (-4)^n. \]
For $n \to \infty$, the sign of $a_{n+1} - a_n$ is determined by the sign of $4A(x) 5^n$.
For $n \to -\infty$, let $n = -m$ where $m \to \infty$. The difference becomes:
\[ a_{-m+1} - a_{-m} = 4A(x) 5^{-m+1} - 5B(x) (-4)^{-m+1} = \frac{20A(x)}{5^m} + \frac{20B(x)}{(-4)^m}. \]
As $m \to \infty$, the term $\frac{20B(x)}{(-4)^m}$ dominates the term $\frac{20A(x)}{5^m}$ because $4^m$ grows slower than $5^m$ in the denominator (meaning the term with $4^m$ is larger). The sign of $\frac{20B(x)}{(-4)^m}$ is $\text{sgn}(B(x)) \cdot (-1)^m$, which alternates as $m$ increases. 

If $B(x) \neq 0$, the sign of $a_{n+1} - a_n$ will alternate for sufficiently large negative $n$, which contradicts the requirement that the sequence be monotonic. Therefore, we must have $B(x) = 0$ for all $x \in \mathbb{R}$.

### 4. Conclusion
Since $B(x) = 0$ for all $x$, we have:
\[ \frac{5x - g(x)}{9} = 0 \implies g(x) = 5x. \]
We check this solution against the original conditions:
1. $g(x) = 5x$ is strictly increasing.
2. $g(x) = 5x$ is surjective.
3. $g(g(x)) = 5(5x) = 25x$ and $g(x) + 20x = 5x + 20x = 25x$.
All conditions are satisfied.

The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ satisfying the equation is $g(x) = 5x$. \(\square\)
