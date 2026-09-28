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
