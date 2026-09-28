# Problem

Find all strictly increasing functions $g:\mathbb{R} \to \mathbb{R}$ such that:
 (a) $g$ is surjective
 (b) $g(g(x))=g(x)+20x.$

# Proof A

1: To find all strictly increasing, surjective functions $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$, we analyze the iterates of $g$.
2: 
3: First, we determine $g(0)$. The equation $g(g(0)) = g(0) + 20(0)$ implies $g(g(0)) = g(0)$. Since $g$ is strictly increasing, it is injective, which implies $g(0) = 0$.
4: 
5: For any $x \in \mathbb{R}$, define the sequence $(a_n)_{n \ge 0}$ by $a_0 = x$ and $a_{n+1} = g(a_n)$. The given equation $g(g(x)) = g(x) + 20x$ implies the linear recurrence relation:
6: \[ a_{n+2} = a_{n+1} + 20a_n. \]
7: The characteristic equation for this linear homogeneous recurrence is $r^2 - r - 20 = 0$, which factors as $(r-5)(r+4) = 0$. The roots are $r_1 = 5$ and $r_2 = -4$. The general solution is:
8: \[ a_n = A(x) 5^n + B(x) (-4)^n \]
9: where $A(x)$ and $B(x)$ are constants depending on the initial value $x$. Using $a_0 = x$ and $a_1 = g(x)$, we have:
10: 1. $x = A(x) + B(x)$
11: 2. $g(x) = 5A(x) - 4B(x)$
12: Solving this system, we find $A(x) = \frac{g(x) + 4x}{9}$ and $B(x) = \frac{5x - g(x)}{9}$.
13: 
14: Since $g$ is strictly increasing and surjective, the inverse function $g^{-1}$ exists and is also strictly increasing. Let $y_n = g^{-n}(x)$ for $x \in \mathbb{R}$. From the original equation, we have $20x = g(g(x)) - g(x)$. Substituting $x = y_{n+2}$, we get:
15: \[ 20y_{n+2} = g(g(y_{n+2})) - g(y_{n+2}) = y_n - y_{n+1} \implies 20y_{n+2} + y_{n+1} - y_n = 0. \]
16: The characteristic equation for this recurrence is $20r^2 + r - 1 = 0$. Using the quadratic formula:
17: \[ r = \frac{-1 \pm \sqrt{1 - 4(20)(-1)}}{40} = \frac{-1 \pm 9}{40}, \]
18: which gives roots $r_1 = \frac{1}{5}$ and $r_2 = -\frac{1}{4}$. The general solution is:
19: \[ y_n = C(x) \left(\frac{1}{5}\right)^n + D(x) \left(-\frac{1}{4}\right)^n. \]
20: Since $g^{-1}$ is strictly increasing, the sequence $(y_n)$ must be strictly monotonic for $x \neq 0$. We examine the difference between consecutive terms:
21: \[ y_{n+1} - y_n = C(x) \left[ \left(\frac{1}{5}\right)^{n+1} - \left(\frac{1}{5}\right)^n \right] + D(x) \left[ \left(-\frac{1}{4}\right)^{n+1} - \left(-\frac{1}{4}\right)^n \right] \]
22: \[ y_{n+1} - y_n = -\frac{4}{5} C(x) \left(\frac{1}{5}\right)^n - \frac{5}{4} D(x) \left(-\frac{1}{4}\right)^n. \]
23: We can rewrite this as:
24: \[ y_{n+1} - y_n = \left(-\frac{1}{4}\right)^n \left[ -\frac{4}{5} C(x) \left(-\frac{4}{5}\right)^n - \frac{5}{4} D(x) \right]. \]
25: As $n \to \infty$, the term $(-4/5)^n$ approaches $0$. Thus, the expression in the brackets approaches $-5/4 D(x)$. If $D(x) \neq 0$, the sign of the bracket is eventually constant (the sign of $-D(x)$), while the factor $(-1/4)^n$ alternates sign. This implies that $y_{n+1} - y_n$ will alternate sign for sufficiently large $n$, contradicting the requirement that $(y_n)$ is strictly monotonic.
26: 
27: Therefore, we must have $D(x) = 0$ for all $x$. This implies:
28: \[ y_n = C(x) \left(\frac{1}{5}\right)^n. \]
29: For $n=0$, $y_0 = x = C(x)$. For $n=1$, $y_1 = g^{-1}(x) = \frac{x}{5}$.
30: Thus, $g(x) = 5x$.
31: 
32: Checking this solution: $g(g(x)) = 5(5x) = 25x$ and $g(x) + 20x = 5x + 20x = 25x$. The function $g(x) = 5x$ is strictly increasing and surjective.
33: 
34: The only such function is $g(x) = 5x$.

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
