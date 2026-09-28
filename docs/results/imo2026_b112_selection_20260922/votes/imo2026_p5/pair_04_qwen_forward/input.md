# Problem

IMO 2026 Problem 5. Let R_{>0} be the set of positive real numbers. Determine all functions f: R_{>0} -> R_{>0} such that, for every x,y > 0, sqrt((x^2 + f(y)^2)/2) >= (f(x) + y)/2 >= sqrt(x f(y)).

# Proof A

1: To find all functions $f: \mathbb{R}_{>0} \to \mathbb{R}_{>0}$ such that for every $x, y > 0$,
2: \[ \sqrt{\frac{x^2 + f(y)^2}{2}} \ge \frac{f(x) + y}{2} \ge \sqrt{x f(y)}, \]
3: we analyze the two given inequalities.
4: 
5: **1. Derivation of a Functional Identity**
6: The right inequality $\frac{f(x) + y}{2} \ge \sqrt{x f(y)}$ implies $f(x) \ge 2\sqrt{x f(y)} - y$.
7: The left inequality $\sqrt{\frac{x^2 + f(y)^2}{2}} \ge \frac{f(x) + y}{2}$ implies $f(x) \le \sqrt{2(x^2 + f(y)^2)} - y$.
8: Substituting $x = f(y)$ into these two inequalities:
9: From the right: $f(f(y)) \ge 2\sqrt{f(y) f(y)} - y = 2f(y) - y$.
10: From the left: $f(f(y)) \le \sqrt{2(f(y)^2 + f(y)^2)} - y = \sqrt{4f(y)^2} - y = 2f(y) - y$.
11: Thus, for all $y > 0$, we have the identity:
12: \[ f(f(y)) = 2f(y) - y. \]
13: 
14: **2. Properties of $g(x) = f(x) - x$**
15: Let $g(x) = f(x) - x$. The identity $f(f(y)) = 2f(y) - y$ can be rewritten as:
16: \[ f(f(y)) - f(y) = f(y) - y \implies g(f(y)) = g(y). \]
17: By induction, the $n$-th iterate of $f$ is $f^{(n)}(y) = y + n g(y)$ for all $n \in \mathbb{N}$. Since the codomain of $f$ is $\mathbb{R}_{>0}$, we must have $y + n g(y) > 0$ for all $n \in \mathbb{N}$ and all $y > 0$. This implies $g(y) \ge 0$ for all $y > 0$. Thus $f(x) \ge x$ for all $x > 0$.
18: 
19: **3. Constraining the Range of $g$**
20: Let $S = f(\mathbb{R}_{>0})$ be the range of $f$. For any $x > 0$ and $z \in S$, let $z = f(y)$. Then $y = z - g(y) = z - g(z)$ because $g(f(y)) = g(y)$. Substituting $z$ and $y$ into the original inequalities:
21: \[ 2\sqrt{xz} - (z - g(z)) \le x + g(x) \le \sqrt{2(x^2 + z^2)} - (z - g(z)). \]
22: Rearranging, we obtain:
23: \[ g(z) - (\sqrt{z} - \sqrt{x})^2 \le g(x) \le g(z) + \sqrt{2(x^2 + z^2)} - (x + z). \]
24: Let $h(x, z) = \sqrt{2(x^2 + z^2)} - (x + z)$. Note that $h(x, z) \ge 0$ and $h(x, z) \to 0$ as $z \to x$.
25: For any $z_1, z_2 \in S$, let $c_1 = g(z_1)$ and $c_2 = g(z_2)$. If $c_1, c_2 > 0$, then $u_n = z_1 + n c_1 \in S$ and $v_m = z_2 + m c_2 \in S$ for all $n, m \in \mathbb{N}$, with $g(u_n) = c_1$ and $g(v_m) = c_2$. For any $n$, we can choose $m$ such that $|u_n - v_m| \le c_2$. Then
26: \[ |c_1 - c_2| \le \max(h(u_n, v_m), (\sqrt{u_n} - \sqrt{v_m})^2). \]
27: As $n \to \infty$, $u_n \to \infty$ and $v_m \to \infty$. Since $|u_n - v_m|$ is bounded, $h(u_n, v_m) \to 0$ and $(\sqrt{u_n} - \sqrt{v_m})^2 \to 0$. Thus $c_1 = c_2$.
28: This implies that $g(S)$ contains at most one positive value $c > 0$. Since $g(\mathbb{R}_{>0}) = g(S)$ (because $g(x) = g(f(x))$), we have $g(y) \in \{0, c\}$ for all $y > 0$.
29: 
30: **4. Proving $g$ is Constant**
31: Suppose $g$ takes both values $0$ and $c > 0$. Let $Z = \{z \in \mathbb{R}_{>0} : g(z) = 0\}$.
32: If $z_1 \in Z$, then $f(z_1) = z_1$. Substituting $x = z_1$ into the right inequality $\frac{f(x) + y}{2} \ge \sqrt{x f(y)}$ gives:
33: \[ \frac{z_1 + y}{2} \ge \sqrt{z_1(y + g(y))} \implies g(y) \le \frac{(z_1 - y)^2}{4 z_1}. \]
34: If $g(y) = c$, then $c \le \frac{(z_1 - y)^2}{4 z_1}$, so $|z_1 - y| \ge 2\sqrt{z_1 c}$. This means the interval $J_{z_1} = (z_1 - 2\sqrt{z_1 c}, z_1 + 2\sqrt{z_1 c}) \cap \mathbb{R}_{>0}$ is contained in $Z$.
35: Since $Z$ contains an interval, we can iteratively apply this property. If $(a, b) \subset Z$, then for any $z \in (a, b)$, $z + 2\sqrt{zc} \in Z$. The sequence $b_{n+1} = b_n + 2\sqrt{b_n c}$ diverges to $\infty$, so $Z$ must contain an interval $(L, \infty)$ for some $L > 0$.
36: However, if $g(y) = c$, then for all $z \in Z$, we must have $c \le \frac{(z - y)^2}{4 z}$, which simplifies to $z^2 - 2z(y + 2c) + y^2 \ge 0$. The roots of this quadratic in $z$ are $z = y + 2c \pm 2\sqrt{yc + c^2} = (\sqrt{y+c} \pm \sqrt{c})^2$. Thus, $Z \cap ((\sqrt{y+c} - \sqrt{c})^2, (\sqrt{y+c} + \sqrt{c})^2) = \emptyset$.
37: For sufficiently large $y$, the interval $((\sqrt{y+c} - \sqrt{c})^2, (\sqrt{y+c} + \sqrt{c})^2)$ is contained in $(L, \infty)$. This contradicts the fact that $Z$ contains $(L, \infty)$.
38: Thus, $g$ must be constant.
39: 
40: **5. Final Verification**
41: If $g(x) = c$, then $f(x) = x + c$ for some $c \ge 0$. Substituting this into the original inequalities:
42: \[ \sqrt{\frac{x^2 + (y+c)^2}{2}} \ge \frac{x+c+y}{2} \ge \sqrt{x(y+c)}. \]
43: The left inequality is the Root-Mean-Square vs Arithmetic-Mean inequality, and the right inequality is the Arithmetic-Mean vs Geometric-Mean inequality. Both are always true for $x, y > 0$ and $c \ge 0$.
44: 
45: The solutions are $f(x) = x + c$ for any $c \ge 0$.

# Proof B

1: To determine all functions $f: \mathbb{R}_{>0} \to \mathbb{R}_{>0}$ such that for every $x, y > 0$,
2: \[ \sqrt{\frac{x^2 + f(y)^2}{2}} \ge \frac{f(x) + y}{2} \ge \sqrt{x f(y)}, \]
3: we analyze the given inequalities. Let $A(x, y) = \sqrt{\frac{x^2 + f(y)^2}{2}}$, $B(x, y) = \frac{f(x) + y}{2}$, and $C(x, y) = \sqrt{x f(y)}$. The condition is $A \ge B \ge C$. Since all terms are positive, we square them:
4: (i) $A^2 \ge B^2 \implies 2x^2 + 2f(y)^2 \ge (f(x) + y)^2$
5: (ii) $B^2 \ge C^2 \implies (f(x) + y)^2 \ge 4x f(y)$
6: 
7: Note that $A^2 - C^2 = \frac{x^2 + f(y)^2}{2} - x f(y) = \frac{(x - f(y))^2}{2}$.
8: If $x = f(y)$, then $A^2 - C^2 = 0$. Since $A \ge B \ge C$, we must have $A = B = C$. In particular, $B = C$ implies:
9: \[ \frac{f(f(y)) + y}{2} = \sqrt{f(y) f(y)} = f(y) \implies f(f(y)) = 2f(y) - y. \]
10: Let $c(y) = f(y) - y$. Then $f(f(y)) = f(y) + c(f(y))$, so $2f(y) - y = f(y) + c(f(y))$, which implies $c(f(y)) = f(y) - y = c(y)$. By induction, $c(f^{(n)}(y)) = c(y)$ for all $n \in \mathbb{N}$, where $f^{(n)}$ denotes the $n$-th iterate of $f$. Also, $f^{(n)}(y) = y + nc(y)$. Since the codomain of $f$ is $\mathbb{R}_{>0}$, we must have $y + nc(y) > 0$ for all $n \in \mathbb{N}$, which implies $c(y) \ge 0$ for all $y > 0$.
11: 
12: If $c(y) = 0$ for all $y > 0$, then $f(x) = x$ for all $x > 0$. If there exists $y_0 > 0$ such that $c(y_0) > 0$, let $c = c(y_0)$. Then $f^{(n)}(y_0) = y_0 + nc$. Let $y_n = f^{(n)}(y_0)$.
13: From (ii), $f(x) \ge 2\sqrt{x f(y)} - y$. Substituting $y = y_n$:
14: \[ f(x) \ge 2\sqrt{x(y_n + c)} - y_n. \]
15: Let $z_n = y_n + c = y_0 + (n+1)c$. Then $y_n = z_n - c$, so $f(x) \ge 2\sqrt{x z_n} - z_n + c$.
16: For a fixed $x$, we can choose $n$ such that $z_n \le x < z_{n+1}$. Then $z_n \in (x-c, x]$. The function $g(z) = 2\sqrt{xz} - z$ is increasing on $(0, x)$, so $g(z_n) \ge g(x-c)$. Thus:
17: \[ f(x) \ge 2\sqrt{x(x-c)} - (x-c) + c = 2\sqrt{x^2 - xc} - x + 2c. \]
18: As $x \to \infty$, $2\sqrt{x^2 - xc} - x = 2x(1 - \frac{c}{2x} - \frac{c^2}{8x^2} + O(x^{-3})) - x = x - c - \frac{c^2}{4x} + O(x^{-2})$.
19: Thus, $f(x) \ge x + c - \frac{c^2}{4x} + O(x^{-2})$, implying $\liminf_{x \to \infty} (f(x) - x) \ge c$.
20: 
21: From (i), $f(x) \le \sqrt{2x^2 + 2f(y)^2} - y$. Substituting $y = y_n$:
22: \[ f(x) \le \sqrt{2x^2 + 2(y_n + c)^2} - y_n = \sqrt{2x^2 + 2z_n^2} - z_n + c. \]
23: The function $h(z) = \sqrt{2x^2 + 2z^2} - z$ has a minimum at $z = x$ with $h(x) = x$. Since $z_n \in (x-c, x+c]$, $h(z_n) \le \max(h(x-c), h(x+c))$.
24: As $x \to \infty$, $h(x \pm c) = \sqrt{2x^2 + 2(x \pm c)^2} - (x \pm c) = \sqrt{4x^2 \pm 4xc + 2c^2} - x \mp c = 2x\sqrt{1 \pm \frac{c}{x} + \frac{c^2}{2x^2}} - x \mp c = x + \frac{c^2}{4x} + O(x^{-2})$.
25: Thus, $f(x) \le x + c + \frac{c^2}{4x} + O(x^{-2})$, implying $\limsup_{x \to \infty} (f(x) - x) \le c$.
26: 
27: Therefore, for any $y_0$ such that $c(y_0) > 0$, the limit $\lim_{x \to \infty} (f(x) - x)$ exists and equals $c(y_0)$. This means $c(y)$ must be the same constant $c$ for all $y$ such that $c(y) > 0$.
28: If $c(y) = 0$ for some $y$, then $f(y) = y$. Substituting this into (i) and (ii) for all $x > 0$:
29: $2\sqrt{xy} - y \le f(x) \le \sqrt{2x^2 + 2y^2} - y$.
30: For a fixed $x$, the value of $2\sqrt{xy} - y$ is maximized at $y=x$ with value $x$, and $\sqrt{2x^2 + 2y^2} - y$ is minimized at $y=x$ with value $x$. Thus $f(x) = x$ for all $x$, which is the case $c = 0$.
31: If $c(y) > 0$ for all $y$, then $c(y) = c$ for all $y$. In both cases, $f(x) = x + c$ for some $c \ge 0$.
32: 
33: Checking $f(x) = x + c$ in the original inequalities:
34: $A^2 - B^2 = \frac{x^2 + (y+c)^2}{2} - \frac{(x+y+c)^2}{4} = \frac{2x^2 + 2y^2 + 4yc + 2c^2 - (x^2 + y^2 + c^2 + 2xy + 2xc + 2yc)}{4} = \frac{(x-y-c)^2}{4} \ge 0$.
35: $B^2 - C^2 = \frac{(x+y+c)^2}{4} - x(y+c) = \frac{x^2 + y^2 + c^2 + 2xy + 2xc + 2yc - 4xy - 4xc}{4} = \frac{(x-y-c)^2}{4} \ge 0$.
36: Both are non-negative for all $x, y > 0$ and $c \ge 0$.
37: 
38: The functions satisfying the condition are $f(x) = x + c$ for any $c \ge 0$.
