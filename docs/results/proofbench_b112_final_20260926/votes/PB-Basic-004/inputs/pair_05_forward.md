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
