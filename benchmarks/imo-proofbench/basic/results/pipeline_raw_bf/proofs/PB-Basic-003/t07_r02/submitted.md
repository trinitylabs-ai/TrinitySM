To find all functions $f: \mathbb{R} \to \mathbb{R}$ such that for all $a, b \in \mathbb{R}$,
\[ (b - a) f(f(a)) = a f(a + f(b)), \]
we proceed as follows.

**1. Initial Observations**
If $f(x) = c$ is a constant function, then $(b - a) c = a c \implies bc = 2ac$ for all $a, b$, which implies $c = 0$. Checking $f(x) = 0$: $(b - a) \cdot 0 = a \cdot 0 \implies 0 = 0$. Thus, $f(x) = 0$ is a solution.
Now assume $f$ is not the zero function. Setting $a = 0$ in the original equation gives:
\[ b f(f(0)) = 0 \cdot f(0 + f(b)) = 0. \]
Since this must hold for all $b \in \mathbb{R}$, we must have $f(f(0)) = 0$. Let $f(0) = c$. Then $f(c) = 0$.

**2. The Case $f(0) = 0$**
If $c = 0$, then $f(0) = 0$. Setting $b = 0$ in the original equation gives:
\[ -a f(f(a)) = a f(a + f(0)) = a f(a). \]
For $a \neq 0$, we have $f(f(a)) = -f(a)$. Substituting this back into the original equation:
\[ (b - a)(-f(a)) = a f(a + f(b)) \implies -b f(a) + a f(a) = a f(a + f(b)). \]
If there exists $a_0 \neq 0$ such that $f(a_0) \neq 0$, then for any $b$, $f(a_0 + f(b)) = \frac{(a_0 - b) f(a_0)}{a_0}$. As $b$ varies, the right-hand side takes all real values, so $f$ is surjective. For any $z \in \mathbb{R}$, there exists $a$ such that $f(a) = z$, so $f(z) = f(f(a)) = -f(a) = -z$. Checking $f(x) = -x$: $(b - a)(-(-a)) = (b - a)a = ab - a^2$ and $a f(a + (-b)) = a f(a - b) = a(b - a) = ab - a^2$. This is a solution.

**3. The Case $f(0) = c$ for $c \neq 0$**
Since $f(c) = 0$, setting $a = c$ in the original equation gives:
\[ (b - c) f(f(c)) = c f(c + f(b)) \implies (b - c) f(0) = c f(c + f(b)) \implies (b - c) c = c f(c + f(b)). \]
Since $c \neq 0$, we have $f(c + f(b)) = b - c$.
Setting $b = c$ in the original equation gives:
\[ (c - a) f(f(a)) = a f(a + f(c)) = a f(a + 0) = a f(a). \]
For $a \neq c$, we have $f(f(a)) = \frac{a f(a)}{c - a}$.
Setting $b = 0$ in the original equation gives:
\[ -a f(f(a)) = a f(a + f(0)) = a f(a + c) \implies f(a + c) = -f(f(a)) = \frac{a f(a)}{a - c}. \]
From $f(c + f(b)) = b - c$, applying $f$ to both sides gives $f(f(c + f(b))) = f(b - c)$.
Using the identity $f(f(z)) = \frac{z f(z)}{c - z}$ with $z = c + f(b)$, we get:
\[ f(b - c) = \frac{(c + f(b)) f(c + f(b))}{c - (c + f(b))} = \frac{(c + f(b))(b - c)}{-f(b)}. \]
Substituting $b \to x + c$ yields $f(x) = \frac{(c + f(x + c))x}{-f(x + c)}$, which simplifies to $f(x + c) = \frac{-cx}{x + f(x)}$.
Equating the two expressions for $f(x + c)$:
\[ \frac{x f(x)}{x - c} = \frac{-cx}{x + f(x)} \implies f(x)(x + f(x)) = -c(x - c) \implies f(x)^2 + x f(x) + cx - c^2 = 0. \]
Solving for $f(x)$ using the quadratic formula:
\[ f(x) = \frac{-x \pm \sqrt{x^2 - 4(cx - c^2)}}{2} = \frac{-x \pm \sqrt{(x - 2c)^2}}{2} = \frac{-x \pm |x - 2c|}{2}. \]
This implies $f(x) = \frac{-x + x - 2c}{2} = -c$ or $f(x) = \frac{-x - (x - 2c)}{2} = c - x$.
If $f(x) = -c$ for all $x$, then $f(0) = -c$, but $f(0) = c$, which implies $c = 0$, contradicting $c \neq 0$.
If $f(x) = c - x$, we check:
LHS: $(b - a) f(f(a)) = (b - a) a = ab - a^2$.
RHS: $a f(a + f(b)) = a f(a + c - b) = a(c - (a + c - b)) = a(b - a) = ab - a^2$.
This is a solution for any $c \in \mathbb{R}$. Note that $f(x) = -x$ is the case $c = 0$.

The functions that satisfy the equation are $f(x) = 0$ and $f(x) = c - x$ for any $c \in \mathbb{R}$.

\(\square\)
