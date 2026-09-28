To find all strictly increasing surjective functions $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$, we proceed as follows:

1.  **Linear Recurrence Relation**:
    Let $x \in \mathbb{R}$ be arbitrary. Define a sequence by $a_0 = x$ and $a_{n+1} = g(a_n)$ for $n \geq 0$. The given functional equation $g(g(x)) = g(x) + 20x$ translates to the linear recurrence:
    \[ a_{n+2} = a_{n+1} + 20a_n \]
    The characteristic equation for this recurrence is $r^2 - r - 20 = 0$. Factoring gives $(r-5)(r+4) = 0$, so the roots are $r_1 = 5$ and $r_2 = -4$. The general solution for $a_n$ is:
    \[ a_n = A(x) 5^n + B(x) (-4)^n \]
    Using $n=0$ and $n=1$, we find:
    \[ a_0 = A(x) + B(x) = x \implies B(x) = x - A(x) \]
    \[ a_1 = g(x) = 5A(x) - 4B(x) = 5A(x) - 4(x - A(x)) = 9A(x) - 4x \]
    Thus, $A(x) = \frac{g(x) + 4x}{9}$ and $B(x) = \frac{5x - g(x)}{9}$.

2.  **Monotonicity Constraint**:
    Since $g$ is strictly increasing, the iterates $g^{(n)}(x) = a_n$ must also be strictly increasing for all $n \in \mathbb{N}$. For any $x < y$, we must have $a_n(x) < a_n(y)$ for all $n$:
    \[ A(x) 5^n + B(x) (-4)^n < A(y) 5^n + B(y) (-4)^n \]
    Dividing by $5^n$ and taking the limit as $n \to \infty$:
    \[ \lim_{n \to \infty} \left( A(x) + B(x) \left(-\frac{4}{5}\right)^n \right) \leq \lim_{n \to \infty} \left( A(y) + B(y) \left(-\frac{4}{5}\right)^n \right) \implies A(x) \leq A(y) \]
    If $A(x) = A(y)$ for some $x < y$, then for all $n$, $B(x) (-4)^n < B(y) (-4)^n$. For $n=1$, $-4B(x) < -4B(y) \implies B(x) > B(y)$. For $n=2$, $16B(x) < 16B(y) \implies B(x) < B(y)$. This is a contradiction, so $A(x)$ must be strictly increasing.

3.  **Analyzing $B(x)$**:
    We have $B(g(x)) = \frac{5g(x) - g(g(x))}{9} = \frac{5g(x) - (g(x) + 20x)}{9} = \frac{4g(x) - 20x}{9} = -4 \frac{5x - g(x)}{9} = -4B(x)$.
    If $B(x)$ is not identically zero, there exists $x_0$ such that $B(x_0) \neq 0$. Then $B(g^{(n)}(x_0)) = (-4)^n B(x_0)$. As $n \to \infty$, $|B(g^{(n)}(x_0))|$ grows as $4^n$, while $g^{(n)}(x_0) = A(x_0) 5^n + B(x_0) (-4)^n$ grows as $5^n$.
    Let $f(x) = B(x)/x$ for $x \neq 0$. Then $f(g(x)) = \frac{B(g(x))}{g(x)} = \frac{-4B(x)}{g(x)}$. As $x \to \infty$, $g(x) \sim 5x$ (since $B(x)$ grows slower than $A(x)$), so $f(g(x)) \approx -\frac{4}{5} f(x)$.
    Repeating this, $f(g^{(n)}(x)) \approx (-\frac{4}{5})^n f(x) \to 0$. However, if we look at the behavior as $x \to 0^+$, the values of $B(x)$ must oscillate and grow in magnitude relative to $x$. Specifically, if $B(x) \neq 0$, the recurrence $\epsilon(g(x)) = \frac{-4\epsilon(x)}{5 + 9\epsilon(x)}$ (where $\epsilon(x) = B(x)/x$) would imply that $\epsilon(x)$ eventually reaches a value that makes $g(x) = x(5+9\epsilon(x)) = 0$ for some $x > 0$, contradicting the fact that $g$ is strictly increasing and $g(0)=0$.

4.  **Conclusion**:
    Therefore, we must have $B(x) = 0$ for all $x$. This implies $g(x) = 5x$. Checking this in the original equation: $g(g(x)) = 5(5x) = 25x$ and $g(x) + 20x = 5x + 20x = 25x$. The function $g(x) = 5x$ is strictly increasing and surjective.

The only such function is $g(x) = 5x$. \(\square\)
