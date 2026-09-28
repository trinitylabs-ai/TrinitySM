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
