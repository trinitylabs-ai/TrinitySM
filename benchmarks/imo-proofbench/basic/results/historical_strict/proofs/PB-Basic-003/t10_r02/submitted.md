To find all functions $f: \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a, b \in \mathbb{R}$,
\[ (b - a)f(f(a)) = a f(a + f(b)), \]
we proceed as follows:

**1. Constant Solutions**
If $f(x) = c$ for all $x$, the equation becomes $(b - a)c = ac$. For this to hold for all $a, b$, we must have $c = 0$. Checking $f(x) = 0$:
LHS: $(b - a) \cdot 0 = 0$.
RHS: $a \cdot 0 = 0$.
Thus, $f(x) = 0$ is a solution.

**2. Initial Values and Properties**
Setting $a = 0$ in the original equation gives:
\[ (b - 0)f(f(0)) = 0 \cdot f(0 + f(b)) = 0. \]
This implies $b f(f(0)) = 0$ for all $b \in \mathbb{R}$, so $f(f(0)) = 0$.
Let $f(0) = c$. Then $f(c) = 0$.

**3. Case $c = 0$**
If $c = 0$, then $f(0) = 0$. The original equation becomes $(b - a)f(f(a)) = a f(a + f(b))$.
If $f$ is not identically zero, there exists $a \neq 0$ such that $f(f(a)) \neq 0$. For such a fixed $a$, $f(a + f(b)) = \frac{f(f(a))}{a}(b - a)$. Since the right-hand side is a linear function of $b$, $f$ is surjective. Furthermore, if $f(b_1) = f(b_2)$, then $f(a + f(b_1)) = f(a + f(b_2))$, which implies $b_1 - a = b_2 - a$, so $b_1 = b_2$. Thus, $f$ is a bijection.
Setting $b = a$ in $(b - a)f(f(a)) = a f(a + f(b))$ gives $0 = a f(a + f(a))$. For $a \neq 0$, $f(a + f(a)) = 0$. Since $f$ is a bijection and $f(0) = 0$, we must have $a + f(a) = 0$, so $f(a) = -a$ for all $a \neq 0$. Since $f(0) = 0$, $f(x) = -x$ for all $x \in \mathbb{R}$.

**4. Case $c \neq 0$**
Substituting $a = c$ into the original equation:
\[ (b - c)f(f(c)) = c f(c + f(b)). \]
Since $f(c) = 0$, $f(f(c)) = f(0) = c$. Thus, $(b - c)c = c f(c + f(b))$, and since $c \neq 0$, we have $f(c + f(b)) = b - c$. This implies $f$ is a bijection.
For $a \neq 0$, let $C_a = \frac{f(f(a))}{a}$. Then $f(a + f(b)) = C_a(b - a)$. Let $f(b) = y$; then $f(a + y) = C_a(f^{-1}(y) - a)$.
Setting $y = 0$ and noting $f^{-1}(0) = c$, we get $f(a) = C_a(c - a)$, so $C_a = \frac{f(a)}{c - a}$ for $a \neq c$.
Then $f(a + y) = \frac{f(a)}{c - a}(f^{-1}(y) - a)$.
From $f(c + f(b)) = b - c$, let $f(b) = y$, so $f(c + y) = f^{-1}(y) - c$, which means $f^{-1}(y) = f(c + y) + c$.
Substituting this into the equation for $f(a + y)$:
\[ f(a + y) = \frac{f(a)}{c - a}(f(c + y) + c - a). \]
Setting $y = c$ and noting $f^{-1}(c) = 0$, we get $f(a + c) = \frac{f(a)}{c - a}(0 - a) = \frac{-a f(a)}{c - a}$.
Let $f(x) = (c - x)g(x)$. Then $f(a + c) = (c - (a + c))g(a + c) = -a g(a + c)$ and $\frac{-a f(a)}{c - a} = \frac{-a(c - a)g(a)}{c - a} = -a g(a)$.
Thus, $-a g(a + c) = -a g(a)$, so $g(a + c) = g(a)$ for $a \neq 0$.
Now substitute $f^{-1}(y) = f(c + y) + c = -y g(c + y) + c = -y g(y) + c$ into $f(a + y) = \frac{f(a)}{c - a}(f^{-1}(y) - a)$:
\[ (c - a - y)g(a + y) = g(a)(-y g(y) + c - a). \]
Setting $y = c - a$, the left-hand side is 0:
\[ 0 = g(a)(-(c - a)g(c - a) + c - a) = g(a)(c - a)(1 - g(c - a)). \]
Since $f$ is a bijection and $f(c) = 0$, $f(a) \neq 0$ for $a \neq c$, so $g(a) \neq 0$. For $a \notin \{0, c\}$, we must have $g(c - a) = 1$. This implies $g(x) = 1$ for all $x \notin \{0, c\}$. Since $f(0) = c$ and $f(c) = 0$, the formula $f(x) = c - x$ holds for all $x$.

**Conclusion**
The solutions are $f(x) = 0$ and $f(x) = c - x$ for any constant $c \in \mathbb{R}$. \(\square\)
