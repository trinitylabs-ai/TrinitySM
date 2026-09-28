# Problem

IMO 2026 Problem 5. Let R_{>0} be the set of positive real numbers. Determine all functions f: R_{>0} -> R_{>0} such that, for every x,y > 0, sqrt((x^2 + f(y)^2)/2) >= (f(x) + y)/2 >= sqrt(x f(y)).

# Proof A

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
