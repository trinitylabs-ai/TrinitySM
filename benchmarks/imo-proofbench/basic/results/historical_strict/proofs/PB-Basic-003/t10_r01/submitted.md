To find all functions $f: \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a, b \in \mathbb{R}$,
\[ (b - a)f(f(a)) = a f(a + f(b)), \tag{1} \]
we analyze the equation step by step.

**1. Constant Solutions**
If $f(x) = c$ for some constant $c$, the equation becomes $(b - a)c = ac$. For this to hold for all $a, b \in \mathbb{R}$, we must have $c = 0$. Testing $f(x) = 0$ in (1): $(b - a) \cdot 0 = a \cdot 0$, which is $0 = 0$. Thus, $f(x) = 0$ is a solution.

**2. Initial Analysis**
Let $P(a, b)$ be the assertion $(b - a)f(f(a)) = a f(a + f(b))$.
$P(0, b) \implies b f(f(0)) = 0$ for all $b \in \mathbb{R}$. Thus, $f(f(0)) = 0$.
$P(a, a) \implies 0 = a f(a + f(a))$. For $a \neq 0$, we must have $f(a + f(a)) = 0$.

**3. Case 1: $f(0) = c \neq 0$**
If $f(0) = c$, then $f(f(0)) = f(c) = 0$.
Substituting $a = c$ into (1):
\[ (b - c)f(f(c)) = c f(c + f(b)). \]
Since $f(c) = 0$, we have $f(f(c)) = f(0) = c$. Thus:
\[ (b - c)c = c f(c + f(b)) \implies f(c + f(b)) = b - c. \]
This equation shows that $f$ is a bijection. Since $f$ is a bijection, the condition $f(a + f(a)) = 0$ for $a \neq 0$ implies that $a + f(a)$ must be the unique root of $f$. Since $f(c) = 0$, we have:
\[ a + f(a) = c \implies f(a) = c - a \text{ for all } a \neq 0. \]
Given $f(0) = c$, we have $f(x) = c - x$ for all $x \in \mathbb{R}$.
Checking $f(x) = c - x$:
LHS: $(b - a)f(f(a)) = (b - a)f(c - a) = (b - a)(c - (c - a)) = (b - a)a$.
RHS: $a f(a + f(b)) = a f(a + c - b) = a(c - (a + c - b)) = a(b - a)$.
LHS = RHS, so $f(x) = c - x$ is a solution for any $c \in \mathbb{R}$.

**4. Case 2: $f(0) = 0$**
If $f(0) = 0$, then $f(f(0)) = 0$.
Subcase 2.1: $f(x) = 0 \iff x = 0$.
Then $f(a + f(a)) = 0$ for $a \neq 0$ implies $a + f(a) = 0$, so $f(a) = -a$. This is the case $c=0$ of $f(x) = c - x$.

Subcase 2.2: There exists $a \neq 0$ such that $f(a) = 0$.
$P(a, b) \implies (b - a)f(f(a)) = a f(a + f(b)) \implies (b - a)f(0) = a f(a + f(b)) \implies 0 = a f(a + f(b))$.
Since $a \neq 0$, $f(a + f(b)) = 0$ for all $b \in \mathbb{R}$.
Let $V = f(\mathbb{R})$ be the range of $f$ and $S = \{x : f(x) = 0\}$. Then $a + V \subseteq S$.
If $V = \{0\}$, then $f(x) = 0$, which is a solution.
If $V \neq \{0\}$, let $v \in V \setminus \{0\}$. Then $a + v \in S$.
For any $x \notin S$, $P(x, b)$ gives $f(x + f(b)) = \frac{f(f(x))}{x}(b - x)$.
If $f(f(x)) \neq 0$ for some $x \notin S$, let $k = \frac{f(f(x))}{x} \neq 0$. Then $f(x + f(b)) = k(b - x)$. As $b$ varies, $f$ takes all real values, so $f$ is a bijection. However, a bijection with $f(0)=0$ implies $S=\{0\}$, which contradicts the existence of $a \neq 0$ such that $f(a)=0$.
Thus, we must have $f(f(x)) = 0$ for all $x \notin S$. Since $f(f(x)) = f(0) = 0$ for $x \in S$, it follows that $f(f(x)) = 0$ for all $x \in \mathbb{R}$.
Substituting $f(f(a)) = 0$ into (1) gives $0 = a f(a + f(b))$ for all $a, b \in \mathbb{R}$.
For $a \neq 0$, $f(a + f(b)) = 0$. This implies $a + V \subseteq S$ for all $a \neq 0$.
If $V \neq \{0\}$, let $v \in V \setminus \{0\}$. Then for all $a \neq 0$, $a + v \in S$. This means $S$ contains all $z \in \mathbb{R}$ except possibly $z = v$.
If $S = \mathbb{R} \setminus \{v\}$, then $f(x) = 0$ for all $x \neq v$. Let $f(v) = w$.
If $w = 0$, then $f(x) = 0$ for all $x$.
If $w \neq 0$, then $V = \{0, w\}$. The condition $f(a + f(b)) = 0$ for $a \neq 0$ must hold. For $b = v$, $f(a + w) = 0$ for all $a \neq 0$. This implies $a + w \neq v$ for all $a \neq 0$.
If $w \neq 0$, we can choose $a = v - w$. For the condition to hold, we must have $a = 0$, so $v - w = 0$, meaning $v = w$.
Then $f(x) = 0$ for $x \neq v$ and $f(v) = v$. Testing this in (1) with $a = v$:
$(b - v)f(f(v)) = v f(v + f(b)) \implies (b - v)f(v) = v f(v + f(b)) \implies (b - v)v = v f(v + f(b))$.
For $b \neq v$, $f(b) = 0$, so $(b - v)v = v f(v) = v^2 \implies b - v = v \implies b = 2v$.
This must hold for all $b \neq v$, which is impossible unless $v = 0$. But $v = 0$ implies $f(x) = 0$ for all $x$.

Thus, the only solutions are $f(x) = 0$ and $f(x) = c - x$ for any constant $c \in \mathbb{R}$.
