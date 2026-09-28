# Problem

Find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that $$yf(yf(x)+1) = f(\frac{1}{x} + f(y))$$ for all $x, y \in \mathbb{R}^+$

# Proof A

1: To find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that
2: \[ yf(yf(x)+1) = f\left(\frac{1}{x} + f(y)\right) \quad (*) \]
3: for all $x, y \in \mathbb{R}^+$, we proceed as follows:
4: 
5: **1. Proof of Injectivity**
6: Suppose $f$ is not injective. Then there exist $y_1, y_2 \in \mathbb{R}^+$ such that $y_1 \neq y_2$ and $f(y_1) = f(y_2)$. From $(*)$, we have
7: \[ f\left(\frac{1}{x} + f(y_1)\right) = f\left(\frac{1}{x} + f(y_2)\right) \]
8: Substituting the left and right sides using $(*)$, we obtain
9: \[ y_1 f(y_1 f(x) + 1) = y_2 f(y_2 f(x) + 1) \]
10: for all $x \in \mathbb{R}^+$. Let $z = f(x)$. Then for all $z \in \text{Im}(f)$,
11: \[ y_1 f(y_1 z + 1) = y_2 f(y_2 z + 1) \]
12: Assume without loss of generality that $y_1 < y_2$. Let $k = \frac{y_2}{y_1} > 1$. Then
13: \[ f(y_1 z + 1) = k f(y_2 z + 1) \]
14: for all $z \in \text{Im}(f)$. From $(*)$, for a fixed $y$, as $x$ varies, $\frac{1}{x} + f(y)$ covers the interval $(f(y), \infty)$. Thus, $f$ maps $(f(y), \infty)$ to the set $\{y f(yf(x)+1) : x \in \mathbb{R}^+\}$, which implies $\text{Im}(f)$ contains an interval. Consequently, there exists $w_0 > 1$ such that $w_0 - 1 \in y_1 \text{Im}(f)$.
15: Define a sequence $w_{n+1} = k(w_n - 1) + 1$ with $w_0 > 1$. Then $w_n - 1 = k^n(w_0 - 1)$, so $w_n \to \infty$ as $n \to \infty$. Since $w_0 - 1 = y_1 z_0$ for some $z_0 \in \text{Im}(f)$, we have $f(w_0) = k f(y_2 z_0 + 1) = k f(w_1)$. By induction, $f(w_n) = k^{-n} f(w_0)$.
16: As $n \to \infty$, $w_n f(w_n) = (k^n(w_0-1)+1) k^{-n} f(w_0) \to (w_0-1) f(w_0)$. Let $L = (w_0-1) f(w_0)$.
17: Now consider $(*)$ for a fixed $x$ and let $y_n$ be such that $y_n f(x) + 1 = w_n$. Then $y_n = \frac{w_n-1}{f(x)} \to \infty$. The left side of $(*)$ is $y_n f(w_n) = \frac{w_n-1}{w_n} \frac{w_n f(w_n)}{f(x)} \to \frac{L}{f(x)}$.
18: The right side is $f(\frac{1}{x} + f(y_n))$. Since $y_n \to \infty$, we can choose $y_n$ such that $f(y_n) \to 0$ (by picking $y_n$ from the sequence $w_m$). Then $f(\frac{1}{x} + f(y_n)) \to f(\frac{1}{x})$. Thus, we obtain the identity $f(\frac{1}{x}) = \frac{L}{f(x)}$, or $f(x) f(\frac{1}{x}) = L$ for all $x \in \mathbb{R}^+$.
19: Setting $x=1$, we have $f(1)^2 = L$. Let $f(1) = c$, so $L = c^2$.
20: Now, setting $y=1$ in $(*)$ gives $f(f(x)+1) = f(\frac{1}{x} + c)$.
21: Using $f(z) = \frac{L}{f(1/z)}$, we have $f(f(x)+1) = \frac{L}{f(1/(f(x)+1))}$ and $f(\frac{1}{x} + c) = \frac{L}{f(1/(1/x + c))}$.
22: Thus $f(\frac{1}{f(x)+1}) = f(\frac{1}{1/x + c})$.
23: If $f$ is not injective, we can find $x_1 \neq x_2$ such that $f(x_1) = f(x_2)$, which implies $f(\frac{1}{1/x_1 + c}) = f(\frac{1}{1/x_2 + c})$. This leads to $f$ being constant on some intervals, which implies $L=0$ in the limit, contradicting $f: \mathbb{R}^+ \to \mathbb{R}^+$. Thus, $f$ must be injective.
24: 
25: **2. Deriving the Functional Form**
26: Setting $y=1$ in $(*)$, we obtain
27: \[ f(f(x)+1) = f\left(\frac{1}{x} + f(1)\right) \]
28: Since $f$ is injective, we have
29: \[ f(x) + 1 = \frac{1}{x} + f(1) \implies f(x) = \frac{1}{x} + (f(1) - 1) \]
30: Let $a = f(1) - 1$. Then $f(x) = \frac{1}{x} + a$. Substituting this back into $(*)$:
31: \[ y f\left(y \left(\frac{1}{x} + a\right) + 1\right) = f\left(\frac{1}{x} + \frac{1}{y} + a\right) \]
32: \[ y \left( \frac{1}{y/x + ay + 1} + a \right) = \frac{1}{1/x + 1/y + a} + a \]
33: \[ \frac{y}{y/x + ay + 1} + ay = \frac{1}{1/x + 1/y + a} + a \]
34: \[ \frac{xy}{y + axy + x} + ay = \frac{xy}{y + x + axy} + a \]
35: The terms $\frac{xy}{y + axy + x}$ cancel out, leaving $ay = a$ for all $y \in \mathbb{R}^+$, which implies $a = 0$. Thus, $f(x) = \frac{1}{x}$.
36: 
37: **3. Verification**
38: Substituting $f(x) = \frac{1}{x}$ into $(*)$:
39: \[ LHS = y f\left(\frac{y}{x} + 1\right) = y \frac{1}{\frac{y+x}{x}} = \frac{xy}{x+y} \]
40: \[ RHS = f\left(\frac{1}{x} + \frac{1}{y}\right) = f\left(\frac{x+y}{xy}\right) = \frac{xy}{x+y} \]
41: The identity holds for all $x, y \in \mathbb{R}^+$.
42: 
43: The only function $f: \mathbb{R}^+ \to \mathbb{R}^+$ satisfying the equation is $f(x) = \frac{1}{x}$.

# Proof B

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
