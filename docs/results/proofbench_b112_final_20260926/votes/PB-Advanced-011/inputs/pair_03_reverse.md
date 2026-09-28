# Problem

Find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that $$yf(yf(x)+1) = f(\frac{1}{x} + f(y))$$ for all $x, y \in \mathbb{R}^+$

# Proof A

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

# Proof B

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
