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
