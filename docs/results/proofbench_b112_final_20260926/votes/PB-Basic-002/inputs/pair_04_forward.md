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

1: To prove the inequality $x^2 + y^2 + z^2 + t^2 \ge xyzt$ given the condition $2(x + y + z + t) \ge xyzt$ for positive real numbers $x, y, z, t$, we denote the product $xyzt$ by $P$ and the sum $x + y + z + t$ by $S$.
2: 
3: **1. Lower Bounds for the Sum of Squares**
4: Let $Q = x^2 + y^2 + z^2 + t^2$. We can establish two different lower bounds for $Q$ using standard inequalities:
5: - **AM-GM Inequality:** Applying the Arithmetic Mean-Geometric Mean Inequality to the four positive terms $x^2, y^2, z^2, t^2$:
6:   \[ \frac{x^2 + y^2 + z^2 + t^2}{4} \ge \sqrt[4]{x^2 y^2 z^2 t^2} = \sqrt{xyzt} = \sqrt{P} \]
7:   Thus, $Q \ge 4\sqrt{P}$.
8: - **Cauchy-Schwarz Inequality:** By the Cauchy-Schwarz Inequality (or the power mean inequality), we have:
9:   \[ \frac{x^2 + y^2 + z^2 + t^2}{4} \ge \left( \frac{x + y + z + t}{4} \right)^2 = \frac{S^2}{16} \]
10:   Thus, $Q \ge \frac{S^2}{4}$.
11: 
12: **2. Using the Given Condition**
13: We are given the condition $2S \ge P$, which implies $S \ge \frac{P}{2}$. Substituting this into the second lower bound for $Q$:
14: \[ Q \ge \frac{(P/2)^2}{4} = \frac{P^2}{16} \]
15: 
16: **3. Case Analysis based on the value of $P$**
17: We now compare the lower bounds $4\sqrt{P}$ and $\frac{P^2}{16}$ to the target value $P$.
18: 
19: - **Case 1: $P \le 16$**
20:   If $P \le 16$, then $\sqrt{P} \le 4$. Multiplying both sides by $\sqrt{P}$ (since $P > 0$):
21:   \[ P \le 4\sqrt{P} \]
22:   From the AM-GM bound, we have $Q \ge 4\sqrt{P}$, so:
23:   \[ Q \ge 4\sqrt{P} \ge P \]
24: 
25: - **Case 2: $P > 16$**
26:   If $P > 16$, then $P^2 > 16P$. Dividing both sides by 16:
27:   \[ \frac{P^2}{16} > P \]
28:   From the Cauchy-Schwarz bound and the given condition, we have $Q \ge \frac{P^2}{16}$, so:
29:   \[ Q \ge \frac{P^2}{16} > P \]
30: 
31: **Conclusion**
32: In both cases, we have shown that $Q \ge P$. Substituting the original variables back into the inequality:
33: \[ x^2 + y^2 + z^2 + t^2 \ge xyzt \]
34: Equality holds if and only if $P=16$ and $x=y=z=t$ (making $S=8$ and $Q=16$), which implies $x=y=z=t=2$.
35: 
36: \(\square\)
