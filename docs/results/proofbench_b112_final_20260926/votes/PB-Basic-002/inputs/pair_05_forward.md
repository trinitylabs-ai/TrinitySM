# Problem

Show that $x^2 + y^2 + z^2 + t^2 \ge xyzt$ for any positive real numbers $x, y, z, t$ that satisfy $2(x + y + z + t) \ge xyzt$.

# Proof A

1: To prove that $x^2 + y^2 + z^2 + t^2 \ge xyzt$ for any positive real numbers $x, y, z, t$ satisfying $2(x + y + z + t) \ge xyzt$, we let $P = xyzt$.
2: 
3: **Case 1: $P \le 16$**
4: By the Arithmetic Mean-Geometric Mean (AM-GM) inequality, we have:
5: \[ \frac{x^2 + y^2 + z^2 + t^2}{4} \ge \sqrt[4]{x^2 y^2 z^2 t^2} = \sqrt{xyzt} = \sqrt{P} \]
6: Thus, $x^2 + y^2 + z^2 + t^2 \ge 4\sqrt{P}$.
7: We consider the inequality $4\sqrt{P} \ge P$. Let $u = \sqrt{P}$. Then $4u \ge u^2$, which is equivalent to $u(u - 4) \le 0$. This inequality holds if and only if $0 \le u \le 4$, which corresponds to $0 \le P \le 16$.
8: Therefore, if $P \le 16$, then $x^2 + y^2 + z^2 + t^2 \ge 4\sqrt{P} \ge P = xyzt$.
9: 
10: **Case 2: $P > 16$**
11: We are given the constraint $2(x + y + z + t) \ge P$. To prove $x^2 + y^2 + z^2 + t^2 \ge P$, it is sufficient to show that $x^2 + y^2 + z^2 + t^2 \ge 2(x + y + z + t)$ whenever $P > 16$.
12: Let $f(x, y, z, t) = x^2 + y^2 + z^2 + t^2 - 2(x + y + z + t)$. We wish to find the minimum of $f$ subject to the constraint $g(x, y, z, t) = xyzt - P = 0$ for a fixed $P > 16$.
13: Using the method of Lagrange multipliers, we set $\nabla f = \lambda \nabla g$:
14: \[ \begin{cases} 2x - 2 = \lambda yzt = \lambda \frac{P}{x} \\ 2y - 2 = \lambda xzt = \lambda \frac{P}{y} \\ 2z - 2 = \lambda xyt = \lambda \frac{P}{z} \\ 2t - 2 = \lambda xyz = \lambda \frac{P}{t} \end{cases} \implies 2x^2 - 2x = 2y^2 - 2y = 2z^2 - 2z = 2t^2 - 2t = \lambda P \]
15: This implies that $x, y, z, t$ must be roots of the quadratic equation $2u^2 - 2u - \lambda P = 0$. A quadratic equation has at most two distinct roots, $a$ and $b$.
16: 1. If $x = y = z = t = k$, then $k^4 = P$, so $k = P^{1/4}$. The value of $f$ is:
17:    \[ f(k, k, k, k) = 4k^2 - 8k = 4k(k - 2) = 4P^{1/4}(P^{1/4} - 2) \]
18:    Since $P > 16$, we have $P^{1/4} > 2$, so $f(k, k, k, k) > 0$.
19: 2. If some variables are $a$ and others are $b$ with $a \neq b$, then $a^2 - a = b^2 - b \implies (a - b)(a + b - 1) = 0$. Since $a \neq b$, we must have $a + b = 1$. This implies $a, b \in (0, 1)$. However, if $a, b \in (0, 1)$, then $P = a^m b^n \le 1$ (where $m+n=4$), which contradicts our assumption that $P > 16$.
20: 
21: As $x, y, z, t \to \infty$ or any variable $\to 0$ (while keeping $P$ constant), $f \to \infty$. Thus, the minimum occurs at the critical point $x = y = z = t = P^{1/4}$. Since $f(P^{1/4}, \dots, P^{1/4}) > 0$ for $P > 16$, we have:
22: \[ x^2 + y^2 + z^2 + t^2 > 2(x + y + z + t) \]
23: Combined with the given constraint $2(x + y + z + t) \ge P$, we obtain:
24: \[ x^2 + y^2 + z^2 + t^2 > 2(x + y + z + t) \ge P = xyzt \]
25: 
26: In both cases, the inequality $x^2 + y^2 + z^2 + t^2 \ge xyzt$ is satisfied.

# Proof B

1: To prove that $x^2 + y^2 + z^2 + t^2 \ge xyzt$ for any positive real numbers $x, y, z, t$ such that $2(x + y + z + t) \ge xyzt$, we consider two cases based on the value of the product $P = xyzt$.
2: 
3: **Case 1: $xyzt \le 16$**
4: By the Arithmetic Mean-Geometric Mean (AM-GM) inequality, we have:
5: \[ x^2 + y^2 + z^2 + t^2 \ge 4 \sqrt[4]{x^2 y^2 z^2 t^2} = 4 \sqrt{xyzt} \]
6: Let $P = xyzt$. We wish to determine when $4\sqrt{P} \ge P$. This inequality is equivalent to $\sqrt{P}(4 - \sqrt{P}) \ge 0$. Since $x, y, z, t$ are positive, $P > 0$, and the inequality holds if and only if $\sqrt{P} \le 4$, which is equivalent to $P \le 16$. 
7: Thus, if $xyzt \le 16$, then $x^2 + y^2 + z^2 + t^2 \ge 4\sqrt{xyzt} \ge xyzt$.
8: 
9: **Case 2: $xyzt > 16$**
10: We are given the condition $2(x + y + z + t) \ge xyzt$. To prove that $x^2 + y^2 + z^2 + t^2 \ge xyzt$, it is sufficient to show that:
11: \[ x^2 + y^2 + z^2 + t^2 \ge 2(x + y + z + t) \]
12: Rearranging this expression:
13: \[ x^2 - 2x + y^2 - 2y + z^2 - 2z + t^2 - 2t \ge 0 \]
14: \[ (x-1)^2 + (y-1)^2 + (z-1)^2 + (t-1)^2 - 4 \ge 0 \]
15: \[ (x-1)^2 + (y-1)^2 + (z-1)^2 + (t-1)^2 \ge 4 \]
16: We now prove that $xyzt > 16$ implies $\sum (x-1)^2 > 4$. We prove the contrapositive: if $\sum (x-1)^2 \le 4$, then $xyzt \le 16$.
17: Let $\delta_1 = x-1, \delta_2 = y-1, \delta_3 = z-1, \delta_4 = t-1$. We want to maximize the product $f(\delta_1, \delta_2, \delta_3, \delta_4) = (1+\delta_1)(1+\delta_2)(1+\delta_3)(1+\delta_4)$ subject to $\sum_{i=1}^4 \delta_i^2 \le 4$ and $\delta_i > -1$.
18: Consider the function $g(\delta) = \ln(1+\delta)$. Since $g''(\delta) = -1/(1+\delta)^2 < 0$, the function is strictly concave. The objective function is $\ln f = \sum \ln(1+\delta_i)$. By Jensen's Inequality or the property of symmetric concave functions over a symmetric convex set, the maximum occurs when $\delta_1 = \delta_2 = \delta_3 = \delta_4 = \delta$.
19: Substituting this into the constraint:
20: \[ 4\delta^2 \le 4 \implies \delta^2 \le 1 \implies -1 < \delta \le 1 \]
21: Then the maximum value of the product is:
22: \[ f = (1+\delta)^4 \le (1+1)^4 = 16 \]
23: Thus, if $\sum (x-1)^2 \le 4$, then $xyzt \le 16$. By contraposition, if $xyzt > 16$, then $\sum (x-1)^2 > 4$.
24: This implies $x^2 + y^2 + z^2 + t^2 > 2(x + y + z + t)$. Combining this with the given condition $2(x + y + z + t) \ge xyzt$, we obtain:
25: \[ x^2 + y^2 + z^2 + t^2 > 2(x + y + z + t) \ge xyzt \]
26: 
27: In both cases, the inequality $x^2 + y^2 + z^2 + t^2 \ge xyzt$ holds for all positive real numbers $x, y, z, t$ satisfying the given constraint.
28: 
29: \(\square\)
