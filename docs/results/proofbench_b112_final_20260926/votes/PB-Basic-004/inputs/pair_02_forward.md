# Problem

Find all strictly increasing functions $g:\mathbb{R} \to \mathbb{R}$ such that:
 (a) $g$ is surjective
 (b) $g(g(x))=g(x)+20x.$

# Proof A

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

# Proof B

1: To find all strictly increasing, surjective functions $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$, we proceed as follows:
2: 
3: **1. Recurrence Relation**
4: For any $x_0 \in \mathbb{R}$, define a sequence $(x_n)_{n \in \mathbb{Z}}$ by $x_{n+1} = g(x_n)$. Since $g$ is surjective and strictly increasing, it is a homeomorphism of $\mathbb{R}$, meaning $g^{-1}$ exists and is also strictly increasing. Thus, the sequence is well-defined for all $n \in \mathbb{Z}$.
5: The given functional equation $g(g(x)) = g(x) + 20x$ translates to the linear recurrence:
6: $$x_{n+2} - x_{n+1} - 20x_n = 0$$
7: The characteristic equation is $r^2 - r - 20 = 0$, which factors as $(r-5)(r+4) = 0$. The general solution is:
8: $$x_n = A(x_0) 5^n + B(x_0) (-4)^n$$
9: where $A(x_0)$ and $B(x_0)$ are constants depending on the starting value $x_0$.
10: 
11: **2. Expressions for $A(x)$ and $B(x)$**
12: For $n=0$ and $n=1$:
13: $x_0 = A(x_0) + B(x_0)$
14: $g(x_0) = 5 A(x_0) - 4 B(x_0)$
15: Solving this system for $A(x_0)$ and $B(x_0)$, we find:
16: $$A(x) = \frac{g(x) + 4x}{9}, \quad B(x) = \frac{5x - g(x)}{9}$$
17: Note that $A(x) + B(x) = x$.
18: 
19: **3. Constraints from Monotonicity**
20: Since $g$ is strictly increasing, if $x < y$, then $x_n < y_n$ for all $n \in \mathbb{Z}$.
21: $$A(x) 5^n + B(x) (-4)^n < A(y) 5^n + B(y) (-4)^n$$
22: Dividing by $5^n$:
23: $$A(x) + B(x) \left(-\frac{4}{5}\right)^n < A(y) + B(y) \left(-\frac{4}{5}\right)^n$$
24: Let $\Delta A = A(y) - A(x)$ and $\Delta B = B(y) - B(x)$. The inequality $\Delta A + \Delta B (-4/5)^n > 0$ must hold for all $n \in \mathbb{Z}$.
25: As $n \to \infty$, $(-4/5)^n \to 0$, which implies $\Delta A \ge 0$.
26: As $n \to -\infty$, let $n = -m$ where $m \to \infty$. The term $(-4/5)^{-m} = (-5/4)^m$ oscillates in sign and its magnitude grows without bound. If $\Delta B \neq 0$, then for either even or odd $m$, $\Delta B (-5/4)^m$ will be a large negative number, eventually making $\Delta A + \Delta B (-5/4)^m < 0$.
27: Thus, we must have $\Delta B = 0$ for all $x < y$. This means $B(x)$ is a constant function, $B(x) = C$ for some $C \in \mathbb{R}$.
28: 
29: **4. Forcing $B(x) = 0$**
30: Since $B(x) = C$, we have $g(x) = 5x - 9C$ (from the expression for $B(x)$).
31: We substitute this into the original functional equation $g(g(x)) = g(x) + 20x$:
32: $$g(5x - 9C) = (5x - 9C) + 20x$$
33: $$5(5x - 9C) - 9C = 25x - 9C$$
34: $$25x - 45C - 9C = 25x - 9C$$
35: $$25x - 54C = 25x - 9C$$
36: This implies $45C = 0$, so $C = 0$.
37: Therefore, $B(x) = 0$ for all $x$.
38: 
39: **5. Final Solution**
40: Substituting $B(x) = 0$ into $g(x) = 5x - 9B(x)$:
41: $$g(x) = 5x$$
42: Checking this solution: $g$ is strictly increasing and surjective. Furthermore, $g(g(x)) = 5(5x) = 25x$ and $g(x) + 20x = 5x + 20x = 25x$. The equation is satisfied.
43: 
44: The only such function is $g(x) = 5x$.
