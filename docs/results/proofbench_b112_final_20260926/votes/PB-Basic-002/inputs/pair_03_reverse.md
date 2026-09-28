# Problem

Show that $x^2 + y^2 + z^2 + t^2 \ge xyzt$ for any positive real numbers $x, y, z, t$ that satisfy $2(x + y + z + t) \ge xyzt$.

# Proof A

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

# Proof B

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
