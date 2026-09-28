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
