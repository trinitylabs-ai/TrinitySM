# Problem

Show that $x^2 + y^2 + z^2 + t^2 \ge xyzt$ for any positive real numbers $x, y, z, t$ that satisfy $2(x + y + z + t) \ge xyzt$.

# Proof A

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
