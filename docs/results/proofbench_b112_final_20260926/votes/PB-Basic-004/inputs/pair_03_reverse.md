# Problem

Find all strictly increasing functions $g:\mathbb{R} \to \mathbb{R}$ such that:
 (a) $g$ is surjective
 (b) $g(g(x))=g(x)+20x.$

# Proof A

1: To find all strictly increasing functions $g: \mathbb{R} \to \mathbb{R}$ that are surjective and satisfy the functional equation $g(g(x)) = g(x) + 20x$, we proceed as follows:
2: 
3: **1. Properties of $g$**
4: Since $g$ is strictly increasing and surjective, $g$ must be continuous. If $g$ had a jump discontinuity at any point $c$, then the left-hand limit $L_1 = \lim_{x \to c^-} g(x)$ and the right-hand limit $L_2 = \lim_{x \to c^+} g(x)$ would exist and satisfy $L_1 < L_2$. The range of $g$ would then omit the interval $(L_1, L_2)$, except possibly for the single value $g(c)$, which contradicts the surjectivity of $g$. Thus, $g$ is a continuous bijection from $\mathbb{R}$ to $\mathbb{R}$.
5: 
6: **2. Recurrence Relation of Iterates**
7: For any $x_0 \in \mathbb{R}$, we define a sequence $(x_n)_{n \in \mathbb{Z}}$ such that $x_{n+1} = g(x_n)$ for all $n$. Since $g$ is a bijection, this sequence is well-defined for all integers $n$. The given functional equation $g(g(x)) = g(x) + 20x$ implies that for all $n$:
8: \[ x_{n+2} = x_{n+1} + 20x_n \]
9: This is a linear homogeneous recurrence relation with constant coefficients. The characteristic equation is:
10: \[ r^2 - r - 20 = 0 \implies (r-5)(r+4) = 0 \]
11: The roots are $r_1 = 5$ and $r_2 = -4$. The general solution for the sequence is:
12: \[ x_n = A(x_0) 5^n + B(x_0) (-4)^n \]
13: where $A(x_0)$ and $B(x_0)$ are constants determined by the initial value $x_0$ and $x_1 = g(x_0)$. Specifically:
14: \[ x_0 = A(x_0) + B(x_0) \]
15: \[ g(x_0) = 5A(x_0) - 4B(x_0) \]
16: 
17: **3. Monotonicity and Asymptotic Behavior**
18: Because $g$ is strictly increasing, the sequence $(x_n)_{n \in \mathbb{Z}}$ must be monotonic for any $x_0$. 
19: - If $g(x_0) > x_0$, then $x_1 > x_0$. Since $g$ is strictly increasing, $g(x_1) > g(x_0) \implies x_2 > x_1$. By induction, $x_{n+1} > x_n$ for all $n \ge 0$. For $n < 0$, if $x_0 \le x_{-1}$, then $g(x_0) \le g(x_{-1}) \implies x_1 \le x_0$, which contradicts $x_1 > x_0$. Thus, $x_{n+1} > x_n$ for all $n \in \mathbb{Z}$.
20: - Similarly, if $g(x_0) < x_0$, then $x_{n+1} < x_n$ for all $n \in \mathbb{Z}$.
21: - If $g(x_0) = x_0$, then $x_n$ is constant for all $n$.
22: 
23: Consider the difference between consecutive terms:
24: \[ \Delta_n = x_{n+1} - x_n = A(x_0)(5^{n+1} - 5^n) + B(x_0)((-4)^{n+1} - (-4)^n) \]
25: \[ \Delta_n = 4 A(x_0) 5^n - 5 B(x_0) (-4)^n \]
26: For the sequence to be monotonic, $\Delta_n$ must have a constant sign (or be identically zero) for all $n \in \mathbb{Z}$. Let us examine the behavior as $n \to -\infty$. Let $n = -m$ where $m \to \infty$:
27: \[ \Delta_{-m} = \frac{4 A(x_0)}{5^m} - \frac{5 B(x_0)}{(-4)^m} = \frac{1}{4^m} \left[ 4 A(x_0) \left(\frac{4}{5}\right)^m - 5 B(x_0) (-1)^{-m} \right] \]
28: As $m \to \infty$, the term $4 A(x_0) (4/5)^m$ decays to zero. Thus, for sufficiently large $m$, the sign of $\Delta_{-m}$ is determined by the sign of $-5 B(x_0) (-1)^{-m}$. Since $(-1)^{-m}$ alternates in sign for each successive integer $m$, the sign of $\Delta_{-m}$ will alternate as $m \to \infty$ unless $B(x_0) = 0$.
29: 
30: **4. Conclusion and Verification**
31: For $\Delta_n$ to maintain a constant sign for all $n \in \mathbb{Z}$, we must have $B(x_0) = 0$ for all $x_0 \in \mathbb{R}$. Substituting $B(x_0) = 0$ into the expressions for $x_0$ and $g(x_0)$:
32: \[ x_0 = A(x_0) \]
33: \[ g(x_0) = 5 A(x_0) = 5x_0 \]
34: Thus, the only possible function is $g(x) = 5x$. We verify this solution:
35: - $g$ is strictly increasing: $5x > 5y$ for $x > y$.
36: - $g$ is surjective: For any $y \in \mathbb{R}$, $x = y/5$ satisfies $g(x) = y$.
37: - Functional equation: $g(g(x)) = 5(5x) = 25x$ and $g(x) + 20x = 5x + 20x = 25x$.
38: The conditions are all satisfied.
39: 
40: The only such function is $g(x) = 5x$.

# Proof B

1: To find all strictly increasing surjective functions $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$, we proceed as follows:
2: 
3: 1.  **Fixed Points and Monotonicity**:
4:     First, we determine the fixed points of $g$. If $g(x) = x$, then substituting into the functional equation gives $x = x + 20x$, which implies $20x = 0$, so $x = 0$. Thus, the only possible fixed point of $g$ is 0.
5:     Now, substitute $x = 0$ into the original equation: $g(g(0)) = g(0) + 20(0) = g(0)$. This shows that $g(0)$ is a fixed point of $g$. Since 0 is the only fixed point, it must be that $g(0) = 0$.
6: 
7:     Since $g$ is strictly increasing, for any $x > 0$, we have $g(x) > g(0) = 0$.
8:     Furthermore, for $x > 0$, we must have $g(x) > x$. If $g(x) \leq x$, then since $g$ is strictly increasing, $g(g(x)) \leq g(x)$. However, the given equation $g(g(x)) = g(x) + 20x$ implies $g(g(x)) - g(x) = 20x > 0$ for $x > 0$, which is a contradiction. Thus, $g(x) > x$ for all $x > 0$.
9:     Similarly, for $x < 0$, we have $g(x) < g(0) = 0$. If $g(x) \geq x$, then $g(g(x)) \geq g(x)$. However, $g(g(x)) - g(x) = 20x < 0$ for $x < 0$, a contradiction. Thus, $g(x) < x$ for all $x < 0$.
10: 
11: 2.  **Linear Recurrence Relation**:
12:     For any $x \in \mathbb{R}$, let $a_0 = x$ and $a_{n+1} = g(a_n)$ for $n \geq 0$. The given functional equation $g(g(x)) = g(x) + 20x$ implies the linear recurrence relation $a_{n+2} = a_{n+1} + 20a_n$. The characteristic equation is $r^2 - r - 20 = 0$, which factors as $(r-5)(r+4) = 0$, yielding roots $r_1 = 5$ and $r_2 = -4$. The general solution for the sequence is:
13:     \[ a_n = A(x) 5^n + B(x) (-4)^n \]
14:     Using $n=0$ and $n=1$, we have $a_0 = A(x) + B(x) = x$ and $a_1 = g(x) = 5A(x) - 4B(x)$. Solving for $A(x)$ and $B(x)$:
15:     \[ A(x) = \frac{g(x) + 4x}{9}, \quad B(x) = \frac{5x - g(x)}{9} \]
16: 
17: 3.  **Bi-infinite Orbit Analysis**:
18:     Since $g$ is strictly increasing and surjective, it is a homeomorphism of $\mathbb{R}$. Thus, the inverse function $g^{-1}$ exists and is also strictly increasing. For any $x_0 \in \mathbb{R}$, we define a bi-infinite sequence $x_n = g^{(n)}(x_0)$ for all $n \in \mathbb{Z}$. The recurrence $x_{n+2} = x_{n+1} + 20x_n$ holds for all $n \in \mathbb{Z}$. The general solution is:
19:     \[ x_n = A(x_0) 5^n + B(x_0) (-4)^n \]
20:     For $x_0 > 0$, we have $x_n > 0$ for all $n \in \mathbb{Z}$ because $g(x) > 0$ for $x > 0$ and $g^{-1}(x) > 0$ for $x > 0$.
21:     Consider the behavior as $n \to -\infty$. Let $n = -m$ where $m \to \infty$:
22:     \[ x_{-m} = A(x_0) \left(\frac{1}{5}\right)^m + B(x_0) \left(-\frac{1}{4}\right)^m \]
23:     We factor out the term with the larger absolute base, $|-1/4| = 0.25 > |1/5| = 0.2$:
24:     \[ x_{-m} = B(x_0) \left(-\frac{1}{4}\right)^m \left[ 1 + \frac{A(x_0)}{B(x_0)} \left(-\frac{4}{5}\right)^m \right] \]
25:     As $m \to \infty$, the term $(-4/5)^m \to 0$. Therefore, for sufficiently large $m$, the term in the brackets is positive. This implies that the sign of $x_{-m}$ is the same as the sign of $B(x_0) (-1/4)^m$.
26:     If $B(x_0) \neq 0$, the sign of $x_{-m}$ alternates as $m$ increases, which contradicts the fact that $x_{-m} > 0$ for all $m$. Thus, we must have $B(x_0) = 0$ for all $x_0 > 0$.
27:     A symmetric argument for $x_0 < 0$ (where $x_n < 0$ for all $n \in \mathbb{Z}$) shows that $B(x_0) = 0$ for all $x_0 < 0$. Since $g(0) = 0$, we also have $B(0) = 0$.
28: 
29: 4.  **Conclusion and Verification**:
30:     Since $B(x) = 0$ for all $x \in \mathbb{R}$, we have $g(x) = 5A(x) - 4(0) = 5A(x)$. From $x = A(x) + B(x)$, we have $A(x) = x$, so $g(x) = 5x$.
31:     Checking $g(x) = 5x$:
32:     (a) $g$ is strictly increasing and surjective.
33:     (b) $g(g(x)) = 5(5x) = 25x$ and $g(x) + 20x = 5x + 20x = 25x$.
34:     The condition is satisfied.
35: 
36: The only such function is $g(x) = 5x$.
