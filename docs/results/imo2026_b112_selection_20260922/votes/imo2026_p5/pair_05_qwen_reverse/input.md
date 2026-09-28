# Problem

IMO 2026 Problem 5. Let R_{>0} be the set of positive real numbers. Determine all functions f: R_{>0} -> R_{>0} such that, for every x,y > 0, sqrt((x^2 + f(y)^2)/2) >= (f(x) + y)/2 >= sqrt(x f(y)).

# Proof A

1: To determine all functions $f: \mathbb{R}_{>0} \to \mathbb{R}_{>0}$ such that for all $x, y > 0$,
2: $$\sqrt{\frac{x^2 + f(y)^2}{2}} \ge \frac{f(x) + y}{2} \ge \sqrt{x f(y)},$$
3: we proceed as follows.
4: 
5: **1. Deriving a functional equation**
6: Setting $x = f(y)$ in the given chain of inequalities, we obtain:
7: $$\sqrt{\frac{f(y)^2 + f(y)^2}{2}} \ge \frac{f(f(y)) + y}{2} \ge \sqrt{f(y) f(y)} \implies f(y) \ge \frac{f(f(y)) + y}{2} \ge f(y).$$
8: This forces equality throughout, so $f(f(y)) = 2f(y) - y$ for all $y > 0$.
9: Let $c(x) = f(x) - x$. Then $f(x) = x + c(x)$. The equation $f(f(x)) = 2f(x) - x$ becomes:
10: $$f(x) + c(f(x)) = 2(x + c(x)) - x = x + 2c(x) \implies x + c(x) + c(f(x)) = x + 2c(x) \implies c(f(x)) = c(x).$$
11: Iterating this, we have $f^{(n)}(x) = x + n c(x)$. Since the codomain of $f$ is $\mathbb{R}_{>0}$, we must have $x + n c(x) > 0$ for all $n \in \mathbb{N}$ and $x > 0$, which implies $c(x) \ge 0$ for all $x > 0$.
12: 
13: **2. Establishing bounds on $c(x)$**
14: Let $z = f(y)$. Then $y = z - c(y) = z - c(z)$ because $c(y) = c(f(y)) = c(z)$.
15: Substituting these into the first inequality $\sqrt{\frac{x^2 + f(y)^2}{2}} \ge \frac{f(x) + y}{2}$:
16: $$\sqrt{\frac{x^2 + z^2}{2}} \ge \frac{x + c(x) + z - c(z)}{2} \implies c(x) - c(z) \le \sqrt{2x^2 + 2z^2} - (x + z).$$
17: Let $h(x, z) = \sqrt{2x^2 + 2z^2} - (x + z)$.
18: Substituting into the second inequality $\frac{f(x) + y}{2} \ge \sqrt{x f(y)}$:
19: $$\frac{x + c(x) + z - c(z)}{2} \ge \sqrt{xz} \implies c(z) - c(x) \le x + z - 2\sqrt{xz} = (\sqrt{x} - \sqrt{z})^2.$$
20: Let $g(x, z) = (\sqrt{x} - \sqrt{z})^2$.
21: Thus, for any $x > 0$ and $z \in \text{Im}(f)$, we have $-g(x, z) \le c(x) - c(z) \le h(x, z)$.
22: 
23: **3. Proving $c(x)$ is constant**
24: Fix $z_0 \in \text{Im}(f)$. As $x \to z_0$, both $g(x, z_0) \to 0$ and $h(x, z_0) \to 0$. By the Squeeze Theorem, $\lim_{x \to z_0} c(x) = c(z_0)$. Thus $c$ is continuous at every point of $\text{Im}(f)$. Since $f(x) = x + c(x)$, $f$ is also continuous at every point of $\text{Im}(f)$.
25: 
26: Now, let $z_1, z_2 \in \text{Im}(f)$. Then $z_1 + n c(z_1)$ and $z_2 + m c(z_2)$ are also in $\text{Im}(f)$ for all $n, m \in \mathbb{N}$. Since $c(z + n c(z)) = c(z)$, we have:
27: $$|c(z_1) - c(z_2)| = |c(z_1 + n c(z_1)) - c(z_2 + m c(z_2))| \le \max(g(z_1 + n c(z_1), z_2 + m c(z_2)), h(z_1 + n c(z_1), z_2 + m c(z_2))).$$
28: If $c(z_1) = c > 0$ and $c(z_2) = c' > 0$, we can choose $n, m \in \mathbb{N}$ such that $z_1 + nc$ and $z_2 + mc'$ are arbitrarily close (this is possible because the set $\{nc - mc' : n, m \in \mathbb{N}\}$ is dense in $\mathbb{R}$ if $c/c'$ is irrational, and can be made exactly $z_2 - z_1$ or close to it if $c/c'$ is rational). As $z_1 + nc \to z_2 + mc'$, both $g$ and $h$ tend to 0. This implies $|c - c'| = 0$, so $c(z)$ is constant on the set $S = \{z \in \text{Im}(f) : c(z) > 0\}$. Let this constant be $c > 0$.
29: 
30: If there exists $z_2 \in \text{Im}(f)$ such that $c(z_2) = 0$, then for any $z_1 \in S$, we have $c(z_1) - c(z_2) = c \le h(z_1, z_2)$. Since $c(z_2) = 0$, $f$ is continuous at $z_2$, so $\text{Im}(f)$ contains points $z_1$ arbitrarily close to $z_2$. As $z_1 \to z_2$, $h(z_1, z_2) \to 0$, which contradicts $c \le h(z_1, z_2)$ for $c > 0$.
31: Thus, either $c(z) = 0$ for all $z \in \text{Im}(f)$ or $c(z) = c > 0$ for all $z \in \text{Im}(f)$. In either case, $c$ is constant on $\text{Im}(f)$.
32: Since $c(x) = c(f(x))$ and $f(x) \in \text{Im}(f)$, it follows that $c(x)$ is constant for all $x > 0$. Let $c(x) = c$ for $c \ge 0$.
33: 
34: **4. Verification**
35: Substituting $f(x) = x + c$ with $c \ge 0$ into the original inequalities:
36: - $\sqrt{\frac{x^2 + (y+c)^2}{2}} \ge \frac{x+c+y}{2} \iff 2x^2 + 2(y+c)^2 \ge (x+y+c)^2 \iff (x - (y+c))^2 \ge 0$.
37: - $\frac{x+c+y}{2} \ge \sqrt{x(y+c)} \iff (x+y+c)^2 \ge 4x(y+c) \iff (x - (y+c))^2 \ge 0$.
38: Both are true for all $x, y > 0$ and $c \ge 0$.
39: 
40: The solutions are $f(x) = x + c$ for any constant $c \ge 0$.

# Proof B

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
