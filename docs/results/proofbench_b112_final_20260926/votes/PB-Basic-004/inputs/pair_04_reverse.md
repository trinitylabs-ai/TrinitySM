# Problem

Find all strictly increasing functions $g:\mathbb{R} \to \mathbb{R}$ such that:
 (a) $g$ is surjective
 (b) $g(g(x))=g(x)+20x.$

# Proof A

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

# Proof B

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
