# Problem

Let $a,b,c$ be positive reals such that $a+b+c = 1$, prove that $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$.

# Proof A

1: To prove that for positive reals $a, b, c$ such that $a+b+c=1$, the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ holds, we proceed as follows:
2: 
3: First, we use the algebraic identity for the sum of pairwise products:
4: \[ (a+b+c)^2 = a^2+b^2+c^2 + 2(ab+bc+ca). \]
5: Given that $a+b+c=1$, we can express the sum of pairwise products as:
6: \[ ab+bc+ca = \frac{1 - (a^2+b^2+c^2)}{2}. \]
7: Substituting this expression into the right-hand side of the inequality we wish to prove, we have:
8: \[ 3\sqrt{3}(ab+bc+ca) = 3\sqrt{3} \left( \frac{1 - (a^2+b^2+c^2)}{2} \right) = \frac{3\sqrt{3}}{2}(1 - \sum a^2). \]
9: The original inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ is therefore equivalent to:
10: \[ \sum \sqrt{a} \geq \frac{3\sqrt{3}}{2}(1 - \sum a^2). \]
11: Since $a+b+c=1$, we can write $1$ as $\sum a$. The inequality becomes:
12: \[ \sum \sqrt{a} \geq \frac{3\sqrt{3}}{2} \sum a - \frac{3\sqrt{3}}{2} \sum a^2, \]
13: which can be rearranged as:
14: \[ \sum \left( \sqrt{a} - \frac{3\sqrt{3}}{2} a + \frac{3\sqrt{3}}{2} a^2 \right) \geq 0. \]
15: Let $g(x) = \sqrt{x} - \frac{3\sqrt{3}}{2} x + \frac{3\sqrt{3}}{2} x^2$ for $x \in (0, 1)$. To prove the inequality, it suffices to show that $g(x) \geq 0$ for all $x \in (0, 1)$. We factor out $\sqrt{x}$ from the expression:
16: \[ g(x) = \sqrt{x} \left( 1 - \frac{3\sqrt{3}}{2} \sqrt{x} + \frac{3\sqrt{3}}{2} x^{3/2} \right). \]
17: Let $t = \sqrt{x}$. Since $x \in (0, 1)$, we have $t \in (0, 1)$. The term in the parentheses is:
18: \[ f(t) = 1 - \frac{3\sqrt{3}}{2} (t - t^3). \]
19: To find the maximum value of the function $h(t) = t - t^3$ on the interval $(0, 1)$, we compute its derivative:
20: \[ h'(t) = 1 - 3t^2. \]
21: Setting $h'(t) = 0$ yields $t = \frac{1}{\sqrt{3}}$. The maximum value of $h(t)$ on this interval is:
22: \[ h\left(\frac{1}{\sqrt{3}}\right) = \frac{1}{\sqrt{3}} - \left(\frac{1}{\sqrt{3}}\right)^3 = \frac{1}{\sqrt{3}} - \frac{1}{3\sqrt{3}} = \frac{2}{3\sqrt{3}}. \]
23: Using this maximum value, we find the minimum value of $f(t)$:
24: \[ f(t) = 1 - \frac{3\sqrt{3}}{2} h(t) \geq 1 - \frac{3\sqrt{3}}{2} \left( \frac{2}{3\sqrt{3}} \right) = 1 - 1 = 0. \]
25: Since $t = \sqrt{x} > 0$ and $f(\sqrt{x}) \geq 0$, it follows that $g(x) = \sqrt{x} f(\sqrt{x}) \geq 0$ for all $x \in (0, 1)$. Summing these values for $a, b, c$, we obtain:
26: \[ \sum g(a) = \sum \sqrt{a} - \frac{3\sqrt{3}}{2} \sum a + \frac{3\sqrt{3}}{2} \sum a^2 = \sum \sqrt{a} - \frac{3\sqrt{3}}{2}(1 - \sum a^2) \geq 0. \]
27: Thus, $\sum \sqrt{a} \geq 3\sqrt{3} \sum ab$. Equality holds if and only if $f(\sqrt{a}) = f(\sqrt{b}) = f(\sqrt{c}) = 0$, which implies $\sqrt{a} = \sqrt{b} = \sqrt{c} = \frac{1}{\sqrt{3}}$, or $a=b=c=1/3$.
28: 
29: \(\square\)

# Proof B

1: To prove that $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for positive reals $a,b,c$ such that $a+b+c=1$, we proceed as follows:
2: 
3: First, we express the term $ab+bc+ca$ in terms of the given constraint $a+b+c=1$. We know that:
4: \[(a+b+c)^2 = a^2+b^2+c^2 + 2(ab+bc+ca) = 1\]
5: Thus, we have $ab+bc+ca = \frac{1 - (a^2+b^2+c^2)}{2}$. Substituting this into the target inequality, we seek to prove:
6: \[\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3} \left( \frac{1 - (a^2+b^2+c^2)}{2} \right)\]
7: Rearranging the terms to group variables, this is equivalent to:
8: \[\sqrt{a}+\sqrt{b}+\sqrt{c} + \frac{3\sqrt{3}}{2}(a^2+b^2+c^2) \geq \frac{3\sqrt{3}}{2}\]
9: Since $a+b+c=1$, we can write the constant on the right side as $\frac{3\sqrt{3}}{2}(a+b+c)$. The inequality then becomes:
10: \[\sum_{cyc} \left( \sqrt{a} + \frac{3\sqrt{3}}{2} a^2 \right) \geq \sum_{cyc} \frac{3\sqrt{3}}{2} a\]
11: This is equivalent to showing that:
12: \[\sum_{cyc} \left( \sqrt{a} + \frac{3\sqrt{3}}{2} a^2 - \frac{3\sqrt{3}}{2} a \right) \geq 0\]
13: Let $h(x) = \sqrt{x} + \frac{3\sqrt{3}}{2}(x^2 - x)$ for $x \in (0, 1)$. We aim to show that $h(x) \geq 0$ for all $x \in (0, 1)$.
14: The derivative of $h(x)$ is:
15: \[h'(x) = \frac{1}{2\sqrt{x}} + 3\sqrt{3}x - \frac{3\sqrt{3}}{2} = \frac{1 + 6\sqrt{3}x\sqrt{x} - 3\sqrt{3}\sqrt{x}}{2\sqrt{x}}\]
16: To find the critical points, we set the numerator to zero. Let $u = \sqrt{x}$, where $u \in (0, 1)$. We solve:
17: \[N(u) = 6\sqrt{3}u^3 - 3\sqrt{3}u + 1 = 0\]
18: Testing $u = \frac{1}{\sqrt{3}}$, we find $N\left(\frac{1}{\sqrt{3}}\right) = 6\sqrt{3}\left(\frac{1}{3\sqrt{3}}\right) - 3\sqrt{3}\left(\frac{1}{\sqrt{3}}\right) + 1 = 2 - 3 + 1 = 0$.
19: Since $u = \frac{1}{\sqrt{3}}$ is a root, we factor $N(u)$ as:
20: \[N(u) = \left(u - \frac{1}{\sqrt{3}}\right)(6\sqrt{3}u^2 + 6u - \sqrt{3})\]
21: The roots of the quadratic factor $6\sqrt{3}u^2 + 6u - \sqrt{3} = 0$ are:
22: \[u = \frac{-6 \pm \sqrt{36 - 4(6\sqrt{3})(-\sqrt{3})}}{12\sqrt{3}} = \frac{-6 \pm \sqrt{36 + 72}}{12\sqrt{3}} = \frac{-6 \pm \sqrt{108}}{12\sqrt{3}} = \frac{-6 \pm 6\sqrt{3}}{12\sqrt{3}} = \frac{-1 \pm \sqrt{3}}{2\sqrt{3}}\]
23: The only positive root is $u_0 = \frac{\sqrt{3}-1}{2\sqrt{3}}$.
24: Analyzing the sign of $N(u)$ for $u \in (0, 1)$:
25: - For $u \in (0, u_0)$, $N(u) > 0$ (since $N(0) = 1$), so $h(x)$ is increasing.
26: - For $u \in (u_0, 1/\sqrt{3})$, $N(u) < 0$, so $h(x)$ is decreasing.
27: - For $u \in (1/\sqrt{3}, 1)$, $N(u) > 0$, so $h(x)$ is increasing.
28: 
29: We evaluate $h(x)$ at the boundaries and the local minimum:
30: $h(0) = 0$ and $h(1/3) = \sqrt{1/3} + \frac{3\sqrt{3}}{2}(\frac{1}{9} - \frac{1}{3}) = \frac{1}{\sqrt{3}} + \frac{3\sqrt{3}}{2}(-\frac{2}{9}) = \frac{1}{\sqrt{3}} - \frac{\sqrt{3}}{3} = 0$.
31: Since $h(x)$ increases from $0$ to $h(u_0^2)$, then decreases to $h(1/3) = 0$, and then increases again, we conclude that $h(x) \geq 0$ for all $x \in (0, 1)$.
32: 
33: Summing the inequalities $h(a) \geq 0, h(b) \geq 0, h(c) \geq 0$, we obtain:
34: \[\sum \sqrt{a} + \frac{3\sqrt{3}}{2} \sum a^2 - \frac{3\sqrt{3}}{2} \sum a \geq 0\]
35: Substituting $\sum a = 1$ and $\sum a^2 = 1 - 2(ab+bc+ca)$:
36: \[\sum \sqrt{a} + \frac{3\sqrt{3}}{2}(1 - 2(ab+bc+ca)) - \frac{3\sqrt{3}}{2} \geq 0\]
37: \[\sum \sqrt{a} + \frac{3\sqrt{3}}{2} - 3\sqrt{3}(ab+bc+ca) - \frac{3\sqrt{3}}{2} \geq 0\]
38: \[\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)\]
39: Equality holds if and only if $a=b=c=1/3$.
