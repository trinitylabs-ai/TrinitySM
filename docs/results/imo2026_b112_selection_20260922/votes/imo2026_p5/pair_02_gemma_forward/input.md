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
