# Problem

Show that $x^2 + y^2 + z^2 + t^2 \ge xyzt$ for any positive real numbers $x, y, z, t$ that satisfy $2(x + y + z + t) \ge xyzt$.

# Proof A

1: To prove that $x^2 + y^2 + z^2 + t^2 \ge xyzt$ for any positive real numbers $x, y, z, t$ satisfying $2(x + y + z + t) \ge xyzt$, we define the sum $S = x + y + z + t$.
2: 
3: First, we establish a lower bound for the left-hand side of the inequality. By the Cauchy-Schwarz inequality:
4: \[ (1^2 + 1^2 + 1^2 + 1^2)(x^2 + y^2 + z^2 + t^2) \ge (x + y + z + t)^2 \]
5: \[ 4(x^2 + y^2 + z^2 + t^2) \ge S^2 \]
6: \[ x^2 + y^2 + z^2 + t^2 \ge \frac{S^2}{4} \]
7: 
8: Next, we consider the upper bounds for the right-hand side, $xyzt$. We are given the condition:
9: \[ xyzt \le 2(x + y + z + t) = 2S \]
10: Furthermore, by the Arithmetic Mean-Geometric Mean (AM-GM) inequality:
11: \[ \sqrt[4]{xyzt} \le \frac{x + y + z + t}{4} = \frac{S}{4} \]
12: Raising both sides to the fourth power, we obtain:
13: \[ xyzt \le \left(\frac{S}{4}\right)^4 = \frac{S^4}{256} \]
14: Thus, for any set of positive real numbers $x, y, z, t$, the product $xyzt$ is bounded by the minimum of these two values:
15: \[ xyzt \le \min\left(2S, \frac{S^4}{256}\right) \]
16: 
17: To show that $x^2 + y^2 + z^2 + t^2 \ge xyzt$, it is sufficient to show that $\frac{S^2}{4} \ge \min\left(2S, \frac{S^4}{256}\right)$ for all $S > 0$. We analyze this by partitioning the possible values of $S$ around the point where the two bounds for $xyzt$ are equal:
18: \[ 2S = \frac{S^4}{256} \implies S^3 = 512 \implies S = 8 \]
19: 
20: **Case 1: $S \ge 8$**
21: When $S \ge 8$, we compare the lower bound of the left-hand side with the given condition $xyzt \le 2S$. We have:
22: \[ \frac{S^2}{4} - 2S = \frac{S^2 - 8S}{4} = \frac{S(S - 8)}{4} \]
23: Since $S \ge 8$, it follows that $S(S - 8) \ge 0$, so $\frac{S^2}{4} \ge 2S$.
24: Therefore, $x^2 + y^2 + z^2 + t^2 \ge \frac{S^2}{4} \ge 2S \ge xyzt$.
25: 
26: **Case 2: $0 < S < 8$**
27: When $0 < S < 8$, we compare the lower bound of the left-hand side with the AM-GM bound $xyzt \le \frac{S^4}{256}$. We have:
28: \[ \frac{S^2}{4} - \frac{S^4}{256} = \frac{64S^2 - S^4}{256} = \frac{S^2(64 - S^2)}{256} \]
29: Since $0 < S < 8$, we have $S^2 < 64$, which implies $S^2(64 - S^2) > 0$. Thus, $\frac{S^2}{4} > \frac{S^4}{256}$.
30: Therefore, $x^2 + y^2 + z^2 + t^2 \ge \frac{S^2}{4} > \frac{S^4}{256} \ge xyzt$.
31: 
32: In both cases, the inequality $x^2 + y^2 + z^2 + t^2 \ge xyzt$ holds. Equality is achieved when $S=8$ and $x=y=z=t=2$, giving $16 \ge 16$.
33: 
34: \(\square\)

# Proof B

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
