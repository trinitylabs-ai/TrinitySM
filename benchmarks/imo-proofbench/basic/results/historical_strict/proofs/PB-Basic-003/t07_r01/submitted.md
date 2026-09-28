To find all functions $f: \mathbb{R} \to \mathbb{R}$ such that for all $a, b \in \mathbb{R}$,
\[ (b - a)f(f(a)) = a f(a + f(b)), \]
we analyze the properties of $f$.

**1. Constant Functions**
Let $f(x) = c$. Substituting into the equation:
$(b - a)c = ac \implies bc - ac = ac \implies bc = 2ac$.
For this to hold for all $a, b$, we must have $c = 0$. Thus, $f(x) = 0$ is a solution.

**2. General Analysis**
Let $f(0) = c$. Setting $a = 0$ in the original equation:
$b f(f(0)) = 0 \cdot f(f(b)) = 0 \implies b f(c) = 0$ for all $b$, so $f(c) = 0$.

**Case A: $c = 0$**
Then $f(0) = 0$. Setting $b = 0$ in the original equation:
$-a f(f(a)) = a f(a + f(0)) = a f(a)$.
For $a \neq 0$, $f(f(a)) = -f(a)$. Since $f(0) = 0$, this holds for all $a \in \mathbb{R}$.
Substituting $f(f(a)) = -f(a)$ back into the original equation:
$(b - a)(-f(a)) = a f(a + f(b)) \implies f(a + f(b)) = \frac{(a - b)f(a)}{a}$ for $a \neq 0$.
If $f$ is not identically zero, there exists $a_0 \neq 0$ such that $f(a_0) \neq 0$. For any $y \in \mathbb{R}$, we can choose $b$ such that $f(a_0 + f(b)) = y$ by setting $b = a_0 - \frac{a_0 y}{f(a_0)}$. Thus $f$ is surjective.
Injectivity: if $f(b_1) = f(b_2)$, then $f(a + f(b_1)) = f(a + f(b_2))$, so $\frac{(a - b_1)f(a)}{a} = \frac{(a - b_2)f(a)}{a}$, which implies $b_1 = b_2$ for $a \neq 0, f(a) \neq 0$. Thus $f$ is a bijection.
Let $f(1) = k$. Since $f$ is a bijection and $f(0) = 0$, we have $k \neq 0$. From $f(a + f(b)) = \frac{(a - b)f(a)}{a}$, setting $a = 1$ gives $f(1 + f(b)) = k(1 - b)$.
Since $f$ is surjective, for any $y \in \mathbb{R}$, there exists $b$ such that $f(b) = y$. Then $f(1 + y) = k(1 - f^{-1}(y))$.
Applying $f$ to both sides and using $f(f(x)) = -f(x)$:
$f(f(1 + y)) = f(k(1 - f^{-1}(y))) \implies -f(1 + y) = f(k(1 - f^{-1}(y)))$.
Substituting $f(1 + y) = k(1 - f^{-1}(y))$, we get $f(k(1 - f^{-1}(y))) = -k(1 - f^{-1}(y))$.
As $y$ varies, $z = k(1 - f^{-1}(y))$ varies over all $\mathbb{R}$. Thus $f(z) = -z$ for all $z \in \mathbb{R}$.

**Case B: $c \neq 0$**
Setting $a = c$ in the original equation:
$(b - c)f(f(c)) = c f(c + f(b)) \implies (b - c)f(0) = c f(c + f(b)) \implies (b - c)c = c f(c + f(b))$.
Since $c \neq 0$, $f(c + f(b)) = b - c$. This implies $f$ is a bijection.
Setting $b = 0$ in the original equation:
$-a f(f(a)) = a f(a + f(0)) = a f(a + c)$.
For $a \neq 0$, $f(f(a)) = -f(a + c)$. Since $f(f(0)) = f(c) = 0$ and $-f(0 + c) = -f(c) = 0$, this holds for all $a \in \mathbb{R}$.
From $f(c + f(b)) = b - c$, let $f(b) = y$. Then $f(c + y) = f^{-1}(y) - c$, so $f^{-1}(y) = f(c + y) + c$.
Substituting $f(f(a)) = -f(a + c)$ into the original equation:
$(b - a)(-f(a + c)) = a f(a + f(b)) \implies f(a + f(b)) = \frac{(a - b)f(a + c)}{a}$ for $a \neq 0$.
Let $f(b) = y$, then $f(a + y) = \frac{(a - f^{-1}(y))f(a + c)}{a}$.
Setting $y = 0$ and using $f^{-1}(0) = c$:
$f(a) = \frac{(a - c)f(a + c)}{a} \implies f(a + c) = \frac{a f(a)}{a - c}$ for $a \neq 0, c$.
Substituting this back into the expression for $f(a + y)$:
$f(a + y) = \frac{(a - f^{-1}(y))f(a)}{a - c}$.
To find $f(2c)$, use $f(f(a)) = -f(a + c)$ with $a = c$:
$f(f(c)) = -f(2c) \implies f(0) = -f(2c) \implies c = -f(2c) \implies f(2c) = -c$.
Now set $a = 2c$ in the expression for $f(a + y)$:
$f(2c + y) = \frac{(2c - f^{-1}(y))f(2c)}{2c - c} = \frac{(2c - f^{-1}(y))(-c)}{c} = f^{-1}(y) - 2c$.
Using $f^{-1}(y) = f(c + y) + c$, we have $f(2c + y) = f(c + y) + c - 2c = f(c + y) - c$.
Let $z = c + y$. Then $f(z + c) = f(z) - c$ for all $z \in \mathbb{R}$.
Equating the two expressions for $f(z + c)$:
$f(z) - c = \frac{z f(z)}{z - c} \implies (f(z) - c)(z - c) = z f(z) \implies z f(z) - c f(z) - cz + c^2 = z f(z)$.
This simplifies to $c f(z) = c^2 - cz$. Since $c \neq 0$, $f(z) = c - z$.

**Verification**
For $f(x) = 0$: $(b - a) \cdot 0 = a \cdot 0$ (Correct).
For $f(x) = c - x$:
$f(f(a)) = c - (c - a) = a$.
LHS: $(b - a)a = ab - a^2$.
RHS: $a f(a + c - b) = a(c - (a + c - b)) = a(b - a) = ab - a^2$.
LHS = RHS.

The solutions are $f(x) = 0$ and $f(x) = c - x$ for any $c \in \mathbb{R}$.
