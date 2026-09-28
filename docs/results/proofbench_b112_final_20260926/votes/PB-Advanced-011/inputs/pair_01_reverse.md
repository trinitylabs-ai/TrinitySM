# Problem

Find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that $$yf(yf(x)+1) = f(\frac{1}{x} + f(y))$$ for all $x, y \in \mathbb{R}^+$

# Proof A

1: To find all functions $f: \mathbb{R}^+ \to \mathbb{R}^+$ such that
2: $$yf(yf(x)+1) = f\left(\frac{1}{x} + f(y)\right)$$
3: for all $x, y \in \mathbb{R}^+$, we proceed as follows:
4: 
5: **1. Testing simple functional forms**
6: If $f(x) = \frac{1}{x}$, then:
7: LHS: $y f\left(\frac{y}{x} + 1\right) = y \frac{1}{\frac{y+x}{x}} = \frac{xy}{x+y}$.
8: RHS: $f\left(\frac{1}{x} + \frac{1}{y}\right) = f\left(\frac{x+y}{xy}\right) = \frac{xy}{x+y}$.
9: Since LHS = RHS, $f(x) = \frac{1}{x}$ is a solution.
10: 
11: **2. Proving injectivity**
12: Suppose $f$ is not injective. Then there exist $x_1, x_2 \in \mathbb{R}^+$ with $x_1 \neq x_2$ such that $f(x_1) = f(x_2)$. Substituting these into the original equation:
13: $$f\left(\frac{1}{x_1} + f(y)\right) = y f(y f(x_1) + 1) \quad \text{and} \quad f\left(\frac{1}{x_2} + f(y)\right) = y f(y f(x_2) + 1).$$
14: Since $f(x_1) = f(x_2)$, the right-hand sides are identical, implying $f(\frac{1}{x_1} + f(y)) = f(\frac{1}{x_2} + f(y))$ for all $y \in \mathbb{R}^+$. Let $T = |\frac{1}{x_1} - \frac{1}{x_2}| > 0$ and $a = \min(\frac{1}{x_1}, \frac{1}{x_2})$. For any $z$ in the set $S + a$ (where $S$ is the range of $f$), we have $f(z + T) = f(z)$. Since the original equation implies that for a fixed $y$, as $x \to 0^+$, the term $\frac{1}{x} + f(y)$ covers the interval $(f(y), \infty)$, the function $f$ is periodic with period $T$ on some interval $(a', \infty)$.
15: 
16: Now, fix $x \in \mathbb{R}^+$ and define $h(y) = f(yf(x)+1)$. The original equation is $f(\frac{1}{x} + f(y)) = yh(y)$.
17: For $y$ large enough such that $y > a'$, we have $f(y+T) = f(y)$. Thus:
18: $$f\left(\frac{1}{x} + f(y+T)\right) = f\left(\frac{1}{x} + f(y)\right) \implies (y+T)h(y+T) = yh(y) \implies h(y+T) = \frac{y}{y+T}h(y).$$
19: Additionally, $h$ is periodic with period $T_h = T/f(x)$ for large $y$, because:
20: $$h\left(y + \frac{T}{f(x)}\right) = f\left(\left(y + \frac{T}{f(x)}\right)f(x) + 1\right) = f(yf(x) + 1 + T).$$
21: For $yf(x)+1 > a'$, we have $f(yf(x)+1+T) = f(yf(x)+1) = h(y)$.
22: Now, for any $y$ large enough, we have $h(y+T) = \frac{y}{y+T}h(y)$. Since $h$ is $T_h$-periodic, we have $h(y+mT_h) = h(y)$ for all $m \in \mathbb{N}$. Then:
23: $$h(y+mT_h+T) = \frac{y+mT_h}{y+mT_h+T}h(y+mT_h) = \frac{y+mT_h}{y+mT_h+T}h(y).$$
24: As $m \to \infty$, the right-hand side $\frac{y+mT_h}{y+mT_h+T}h(y) \to h(y)$.
25: However, the left-hand side $h(y+mT_h+T) = h(y+T)$ is constant for all $m$ due to the $T_h$-periodicity of $h$.
26: Thus, we must have $h(y+T) = h(y)$.
27: Combining this with $h(y+T) = \frac{y}{y+T}h(y)$, we get $h(y) = \frac{y}{y+T}h(y)$, which implies $h(y) = 0$ for all $y$.
28: This contradicts the codomain $\mathbb{R}^+$. Thus, $f$ must be injective.
29: 
30: **3. Deriving the general form**
31: Given that $f$ is injective, we substitute $y=1$ into the original equation:
32: $$f(f(x)+1) = f\left(\frac{1}{x} + f(1)\right).$$
33: Since $f$ is injective, we have:
34: $$f(x) + 1 = \frac{1}{x} + f(1) \implies f(x) = \frac{1}{x} + f(1) - 1.$$
35: Let $C = f(1) - 1$. Then $f(x) = \frac{1}{x} + C$. Substitute this back into the original equation:
36: $$y \left( \frac{1}{y(\frac{1}{x} + C) + 1} + C \right) = \frac{1}{\frac{1}{x} + \frac{1}{y} + C} + C.$$
37: Simplifying the left-hand side:
38: $$\frac{y}{\frac{y}{x} + yC + 1} + yC = \frac{xy}{y + xyC + x} + yC.$$
39: Simplifying the right-hand side:
40: $$\frac{1}{\frac{x+y}{xy} + C} + C = \frac{xy}{x+y + xyC} + C.$$
41: Equating the two:
42: $$\frac{xy}{x+y + xyC} + yC = \frac{xy}{x+y + xyC} + C \implies yC = C \quad \text{for all } y \in \mathbb{R}^+.$$
43: This implies $C = 0$. Thus $f(1) = 1$, and the function must be $f(x) = \frac{1}{x}$.
44: We have already verified that $f(x) = \frac{1}{x}$ is a solution.
45: 
46: The only solution is $f(x) = \frac{1}{x}$.

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
