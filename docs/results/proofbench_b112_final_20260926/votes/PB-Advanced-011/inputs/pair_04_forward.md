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
