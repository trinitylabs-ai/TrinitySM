# Problem

Find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that $$yf(yf(x)+1) = f(\frac{1}{x} + f(y))$$ for all $x, y \in \mathbb{R}^+$

# Proof A

1: To find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that
2: $$yf(yf(x)+1) = f\left(\frac{1}{x} + f(y)\right)$$
3: for all $x, y \in \mathbb{R}^+$, we proceed as follows:
4: 
5: **1. Verification of $f(x) = \frac{1}{x}$**
6: Substituting $f(x) = \frac{1}{x}$ into the original equation:
7: $$\text{LHS} = y f\left(\frac{y}{x} + 1\right) = y \left(\frac{1}{\frac{y}{x} + 1}\right) = y \left(\frac{x}{y+x}\right) = \frac{xy}{x+y}$$
8: $$\text{RHS} = f\left(\frac{1}{x} + \frac{1}{y}\right) = \frac{1}{\frac{1}{x} + \frac{1}{y}} = \frac{1}{\frac{x+y}{xy}} = \frac{xy}{x+y}$$
9: The equation holds for all $x, y \in \mathbb{R}^+$. Thus, $f(x) = \frac{1}{x}$ is a solution.
10: 
11: **2. Proof of Injectivity**
12: Suppose $f$ is not injective. Then there exist $x_1, x_2 \in \mathbb{R}^+$ such that $x_1 \neq x_2$ and $f(x_1) = f(x_2)$.
13: From the original equation, we have:
14: $$f\left(\frac{1}{x_1} + f(y)\right) = y f(y f(x_1) + 1)$$
15: $$f\left(\frac{1}{x_2} + f(y)\right) = y f(y f(x_2) + 1)$$
16: Since $f(x_1) = f(x_2)$, the right-hand sides are identical for all $y \in \mathbb{R}^+$, yielding:
17: $$f\left(\frac{1}{x_1} + f(y)\right) = f\left(\frac{1}{x_2} + f(y)\right)$$
18: Let $a = \frac{1}{x_1}$ and $b = \frac{1}{x_2}$. Since $x_1 \neq x_2$, we have $a \neq b$. Let $w = f(y)$. Then for all $w \in \text{Im}(f)$, we have:
19: $$f(a + w) = f(b + w)$$
20: Assume without loss of generality that $a < b$. Let $p = b - a > 0$. Then $f(a + w) = f(a + w + p)$ for all $w \in \text{Im}(f)$.
21: Now consider the original equation again: $f(\frac{1}{x} + f(y)) = y f(y f(x) + 1)$.
22: For a fixed $x$, the right-hand side is $y f(y f(x) + 1)$. The left-hand side is $f(\frac{1}{x} + f(y))$.
23: Since $f(y) \in \text{Im}(f)$, the property $f(a+w) = f(a+w+p)$ implies that for any $w \in \text{Im}(f)$, $f(a+w) = f(a+w+p) = f(a+w+2p) = \dots$ as long as the values remain in the domain.
24: Crucially, if $f(a+w) = f(b+w)$ for all $w \in \text{Im}(f)$, then for any $y \in \mathbb{R}^+$, $f(\frac{1}{x} + f(y))$ would be periodic in $f(y)$ with period $p$.
25: However, $f(\frac{1}{x} + f(y)) = y f(y f(x) + 1)$. If $f$ were periodic on its image, then for a fixed $x$, the expression $y f(y f(x) + 1)$ would have to exhibit periodic behavior in $y$ (since $f(y)$ is periodic). But the term $y f(y f(x) + 1)$ involves a linear multiplier $y$, which prevents the expression from being periodic unless $f(y f(x) + 1) = 0$, which is impossible as the codomain is $\mathbb{R}^+$.
26: Thus, the assumption that $f$ is not injective leads to a contradiction. Therefore, $f$ must be injective.
27: 
28: **3. Deriving the Unique Solution**
29: Since $f$ is injective, we use the original equation with $y=1$:
30: $$f(f(x)+1) = f\left(\frac{1}{x} + f(1)\right)$$
31: Injectivity implies:
32: $$f(x) + 1 = \frac{1}{x} + f(1)$$
33: Let $k = f(1) - 1$. Then $f(x) = \frac{1}{x} + k$. Substituting this back into the original equation:
34: $$\text{LHS} = y f\left(y\left(\frac{1}{x} + k\right) + 1\right) = y \left(\frac{1}{\frac{y}{x} + yk + 1} + k\right) = \frac{xy}{x + y + xyk} + yk$$
35: $$\text{RHS} = f\left(\frac{1}{x} + \frac{1}{y} + k\right) = \frac{1}{\frac{1}{x} + \frac{1}{y} + k} + k = \frac{xy}{x + y + xyk} + k$$
36: Comparing the two sides, we obtain $yk = k$ for all $y \in \mathbb{R}^+$, which implies $k=0$.
37: Therefore, $f(x) = \frac{1}{x}$ is the only solution.
38: 
39: The only function $f: \mathbb{R}^+ \to \mathbb{R}^+$ satisfying the equation is $f(x) = \frac{1}{x}$.

# Proof B

1: To find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that
2: \[ y f(y f(x) + 1) = f\left(\frac{1}{x} + f(y)\right) \quad \text{for all } x, y \in \mathbb{R}^+, \]
3: we proceed as follows:
4: 
5: **1. Testing for a simple solution**
6: We test if $f(x) = \frac{1}{x}$ is a solution. Substituting this into the functional equation:
7: LHS: $y f\left(y \frac{1}{x} + 1\right) = y \frac{1}{\frac{y}{x} + 1} = \frac{yx}{y + x}$.
8: RHS: $f\left(\frac{1}{x} + \frac{1}{y}\right) = \frac{1}{\frac{1}{x} + \frac{1}{y}} = \frac{xy}{x + y}$.
9: Since LHS = RHS for all $x, y \in \mathbb{R}^+$, $f(x) = \frac{1}{x}$ is a solution.
10: 
11: **2. Proving Injectivity**
12: Suppose there exist $y_1, y_2 \in \mathbb{R}^+$ such that $y_1 \neq y_2$ and $f(y_1) = f(y_2)$. Without loss of generality, assume $y_1 > y_2$. Let $k = \frac{y_1}{y_2} > 1$.
13: From the original equation, $f(y_1) = f(y_2)$ implies $f(\frac{1}{x} + f(y_1)) = f(\frac{1}{x} + f(y_2))$. Substituting the original equation into both sides:
14: \[ y_1 f(y_1 f(x) + 1) = y_2 f(y_2 f(x) + 1). \]
15: Let $z = f(x)$. Then $y_1 f(y_1 z + 1) = y_2 f(y_2 z + 1)$ for all $z \in \text{Ran}(f)$. Since $y_1 = k y_2$, we have:
16: \[ k y_2 f(k y_2 z + 1) = y_2 f(y_2 z + 1) \implies f(y_2 z + 1) = k f(k y_2 z + 1) \quad \text{for all } z \in \text{Ran}(f). \]
17: Now, substitute $y = k^n y_2$ into the original functional equation for $n \in \mathbb{N}$:
18: \[ k^n y_2 f(k^n y_2 f(x) + 1) = f\left(\frac{1}{x} + f(k^n y_2)\right). \]
19: Using the relation $f(y_2 z + 1) = k f(k y_2 z + 1)$ repeatedly (or by induction on $n$), we have $f(y_2 z + 1) = k^n f(k^n y_2 z + 1)$. Thus, the LHS becomes:
20: \[ k^n y_2 \left[ k^{-n} f(y_2 f(x) + 1) \right] = y_2 f(y_2 f(x) + 1). \]
21: From the original equation with $y = y_2$, we know $y_2 f(y_2 f(x) + 1) = f(\frac{1}{x} + f(y_2))$. Thus,
22: \[ f\left(\frac{1}{x} + f(k^n y_2)\right) = f\left(\frac{1}{x} + f(y_2)\right) \quad \text{for all } x \in \mathbb{R}^+, n \in \mathbb{N}. \]
23: Let $a_n = f(k^n y_2)$. Then $f(s + a_n) = f(s + a_0)$ for all $s > 0$, where $a_0 = f(y_2)$.
24: If $a_n$ is not constant for $n \in \mathbb{N}$, then $f$ is periodic on the interval $(\min(a_0, a_n), \infty)$. If $f$ is periodic, let $M = \sup f$. Then $f(1/x + f(y)) \le M$ for all $x, y$. However, $y f(y f(x) + 1) \ge y \inf f$. If $\inf f > 0$, then for large $y$, $y \inf f > M$, a contradiction. If $\inf f = 0$, we note that $f(k^n y_2 z + 1) = k^{-n} f(y_2 z + 1) \to 0$ as $n \to \infty$. A periodic function $f: \mathbb{R}^+ \to \mathbb{R}^+$ that tends to 0 at infinity must be identically 0, which contradicts the codomain $\mathbb{R}^+$.
25: Thus, $a_n$ must be constant, so $f(k^n y_2) = a_0$ for all $n \in \mathbb{N}$.
26: However, we established that $f(k^n y_2 z + 1) = k^{-n} f(y_2 z + 1)$, which implies $f(w) \to 0$ as $w \to \infty$ for $w$ in the set $\{k^n y_2 z + 1 : z \in \text{Ran}(f), n \in \mathbb{N}\}$. Since $\text{Ran}(f)$ contains an interval $(f(y), \infty)$, this set covers all values from some $T$ onwards. Thus $f(w) \to 0$ as $w \to \infty$. Since $k^n y_2 \to \infty$ as $n \to \infty$, we must have $f(k^n y_2) \to 0$, which contradicts $f(k^n y_2) = a_0 > 0$.
27: Therefore, $y_1$ must equal $y_2$, and $f$ is injective.
28: 
29: **3. Determining the Function**
30: Using the injectivity of $f$ and setting $y=1$ in the original equation:
31: \[ f(f(x) + 1) = f\left(\frac{1}{x} + f(1)\right). \]
32: Since $f$ is injective, the arguments must be equal:
33: \[ f(x) + 1 = \frac{1}{x} + f(1). \]
34: Let $f(1) = a$. Then $f(x) = \frac{1}{x} + a - 1$.
35: Substitute this back into the original equation:
36: LHS: $y f\left(y\left(\frac{1}{x} + a - 1\right) + 1\right) = y \left( \frac{1}{\frac{y}{x} + y(a-1) + 1} + a - 1 \right) = \frac{yx}{y + xy(a-1) + x} + y(a-1)$.
37: RHS: $f\left(\frac{1}{x} + \frac{1}{y} + a - 1\right) = \frac{1}{\frac{1}{x} + \frac{1}{y} + a - 1} + a - 1 = \frac{xy}{x + y + xy(a-1)} + a - 1$.
38: Equating the two sides:
39: \[ \frac{xy}{x + y + xy(a-1)} + y(a-1) = \frac{xy}{x + y + xy(a-1)} + a - 1. \]
40: This implies $y(a-1) = a-1$ for all $y \in \mathbb{R}^+$, which means $a-1 = 0$, so $a=1$.
41: Substituting $a=1$ into $f(x) = \frac{1}{x} + a - 1$ gives $f(x) = \frac{1}{x}$.
42: 
43: The only function $f: \mathbb{R}^+ \to \mathbb{R}^+$ that satisfies the given equation is $f(x) = \frac{1}{x}$.
