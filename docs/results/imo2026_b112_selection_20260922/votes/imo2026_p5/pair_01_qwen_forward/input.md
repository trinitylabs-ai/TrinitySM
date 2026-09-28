# Problem

IMO 2026 Problem 5. Let R_{>0} be the set of positive real numbers. Determine all functions f: R_{>0} -> R_{>0} such that, for every x,y > 0, sqrt((x^2 + f(y)^2)/2) >= (f(x) + y)/2 >= sqrt(x f(y)).

# Proof A

1: To determine all functions $f: \mathbb{R}_{>0} \to \mathbb{R}_{>0}$ such that for every $x, y > 0$,
2: $$\sqrt{\frac{x^2 + f(y)^2}{2}} \ge \frac{f(x) + y}{2} \ge \sqrt{x f(y)},$$
3: we analyze the constraints imposed by these inequalities.
4: 
5: **1. Verification of Candidate Solutions**
6: Let $f(x) = x + c$ for some constant $c \ge 0$. For $f$ to map $\mathbb{R}_{>0}$ to $\mathbb{R}_{>0}$, we must have $c \ge 0$.
7: Substituting $f(x) = x + c$ into the right-hand inequality:
8: $$\frac{x + c + y}{2} \ge \sqrt{x(y + c)}.$$
9: This is the Arithmetic Mean-Geometric Mean (AM-GM) inequality for $x$ and $y + c$, which holds for all $x, y > 0$ and $c \ge 0$.
10: Substituting $f(x) = x + c$ into the left-hand inequality:
11: $$\sqrt{\frac{x^2 + (y + c)^2}{2}} \ge \frac{x + c + y}{2}.$$
12: This is the Root Mean Square-Arithmetic Mean (RMS-AM) inequality for $x$ and $y + c$, which holds for all $x, y > 0$ and $c \ge 0$.
13: Thus, $f(x) = x + c$ for any $c \ge 0$ is a solution.
14: 
15: **2. Derivation of Functional Properties**
16: For any $y > 0$, let $x = f(y)$. The given inequalities become:
17: $$\sqrt{\frac{f(y)^2 + f(y)^2}{2}} \ge \frac{f(f(y)) + y}{2} \ge \sqrt{f(y) f(y)} \implies f(y) \ge \frac{f(f(y)) + y}{2} \ge f(y).$$
18: This forces $f(f(y)) + y = 2f(y)$. Let $c(y) = f(y) - y$. The equation $f(f(y)) - f(y) = f(y) - y$ implies $c(f(y)) = c(y)$.
19: By induction, $f^{(n)}(y) = y + n c(y)$ for all $n \in \mathbb{N}$. Since $f: \mathbb{R}_{>0} \to \mathbb{R}_{>0}$, we must have $y + n c(y) > 0$ for all $n \in \mathbb{N}$ and $y > 0$, which implies $c(y) \ge 0$ for all $y > 0$.
20: 
21: Next, consider the right-hand inequality $\frac{f(x) + y}{2} \ge \sqrt{x f(y)}$. Rearranging for $f(x)$:
22: $$f(x) \ge 2\sqrt{x f(y)} - y.$$
23: Substituting $f(x) = x + c(x)$ and $y = f(y) - c(y)$:
24: $$x + c(x) \ge 2\sqrt{x f(y)} - (f(y) - c(y)) \implies c(x) \ge c(y) - (f(y) - 2\sqrt{x f(y)} + x) = c(y) - (\sqrt{f(y)} - \sqrt{x})^2.$$
25: Let $z = f(y)$. Since $c(z) = c(f(y)) = c(y)$, we have $c(x) \ge c(z) - (\sqrt{z} - \sqrt{x})^2$ for all $x > 0$ and $z \in \text{Range}(f)$.
26: If $x$ is also in the range of $f$, we have $c(z) \ge c(x) - (\sqrt{x} - \sqrt{z})^2$. Thus, for all $x, z \in \text{Range}(f)$:
27: $$|c(x) - c(z)| \le (\sqrt{x} - \sqrt{z})^2.$$
28: 
29: **3. Constancy of $c(x)$ on $S$**
30: Let $S = \{x \in \mathbb{R}_{>0} : c(x) > 0\}$ and $Z = \{x \in \mathbb{R}_{>0} : c(x) = 0\}$.
31: Suppose $S$ is non-empty. For any $y_1, y_2 \in S$, the sequences $z_{1,n} = f^{(n)}(y_1) = y_1 + n c(y_1)$ and $z_{2,m} = f^{(m)}(y_2) = y_2 + m c(y_2)$ are in $\text{Range}(f)$ for $n, m \ge 1$.
32: Using the range inequality:
33: $$|c(y_1) - c(y_2)| = |c(z_{1,n}) - c(z_{2,m})| \le (\sqrt{z_{1,n}} - \sqrt{z_{2,m}})^2 = \frac{(z_{1,n} - z_{2,m})^2}{(\sqrt{z_{1,n}} + \sqrt{z_{2,m}})^2}.$$
34: For a fixed $n$, we can choose $m$ such that $z_{2,m} \le z_{1,n} < z_{2,m+1}$, which implies $0 \le z_{1,n} - z_{2,m} < c(y_2)$. Thus, $|z_{1,n} - z_{2,m}| \le \max(c(y_1), c(y_2))$. As $n \to \infty$, $z_{1,n} \to \infty$ and $z_{2,m} \to \infty$, so the right-hand side tends to 0. Thus, $c(y_1) = c(y_2)$ for all $y_1, y_2 \in S$. Let this constant value be $c > 0$.
35: 
36: **4. Analysis of the Fixed-Point Set $Z$**
37: Suppose $Z$ is non-empty. For any $z \in Z$ and $x \in S$, we have $f(z) = z \in \text{Range}(f)$ and $f(x) = x + c \in \text{Range}(f)$. Applying the range inequality:
38: $$|c(f(x)) - c(f(z))| \le (\sqrt{f(x)} - \sqrt{f(z)})^2 \implies |c - 0| \le (\sqrt{x + c} - \sqrt{z})^2.$$
39: This implies $\sqrt{c} \le |\sqrt{x + c} - \sqrt{z}|$.
40: Case A: $\sqrt{x + c} \ge \sqrt{z} + \sqrt{c} \implies x + c \ge z + c + 2\sqrt{zc} \implies x \ge z + 2\sqrt{zc}$.
41: Case B: $\sqrt{x + c} \le \sqrt{z} - \sqrt{c} \implies x + c \le z + c - 2\sqrt{zc} \implies x \le z - 2\sqrt{zc}$.
42: Thus, for any $z \in Z$, the interval $(z - 2\sqrt{zc}, z + 2\sqrt{zc}) \cap \mathbb{R}_{>0}$ contains no elements of $S$. Since $S \cup Z = \mathbb{R}_{>0}$, this interval must be a subset of $Z$.
43: This implies that $Z$ is an open set in $\mathbb{R}_{>0}$. If $Z$ is non-empty, let $z_0 \in Z$. Then $Z$ contains $I_0 = (z_0 - 2\sqrt{z_0 c}, z_0 + 2\sqrt{z_0 c}) \cap \mathbb{R}_{>0}$. We can pick $z_1 \in Z$ arbitrarily close to the right endpoint $z_0 + 2\sqrt{z_0 c}$, and the interval around $z_1$ will extend the set $Z$ further to the right. By induction, $Z$ is not bounded above. Similarly, $Z$ can be extended to the left until it covers $(0, \infty)$. Thus, $Z = \mathbb{R}_{>0}$.
44: Consequently, either $S = \emptyset$ (so $c(x) = 0$ for all $x$) or $Z = \emptyset$ (so $c(x) = c$ for all $x$).
45: 
46: In both cases, $f(x) = x + c$ for some constant $c \ge 0$.
47: The functions are $f(x) = x + c$ for any $c \ge 0$.

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
