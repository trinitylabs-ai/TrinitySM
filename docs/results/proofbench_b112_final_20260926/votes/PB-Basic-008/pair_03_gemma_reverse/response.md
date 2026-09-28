# Proof comparison

## Proof A
Established theorem: For positive reals $a, b, c$ such that $a+b+c=1$, the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ holds.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks: The proof uses the identity $ab+bc+ca = \frac{1 - (a^2+b^2+c^2)}{2}$ (lines 4-6) to rewrite the inequality as $\sum \sqrt{a} \geq \frac{3\sqrt{3}}{2}(1 - \sum a^2)$. By substituting $1 = \sum a$, this becomes $\sum (\sqrt{a} - \frac{3\sqrt{3}}{2} a + \frac{3\sqrt{3}}{2} a^2) \geq 0$ (lines 12-14). The proof then analyzes $g(x) = \sqrt{x} - \frac{3\sqrt{3}}{2} x + \frac{3\sqrt{3}}{2} x^2$ for $x \in (0, 1)$. By substituting $t = \sqrt{x}$, it defines $f(t) = 1 - \frac{3\sqrt{3}}{2}(t - t^3)$ (lines 16-18). The function $h(t) = t - t^3$ has a maximum of $2/(3\sqrt{3})$ at $t = 1/\sqrt{3}$ on the interval $(0, 1)$ (lines 19-22), which implies $f(t) \geq 1 - \frac{3\sqrt{3}}{2}(\frac{2}{3\sqrt{3}}) = 0$ (line 24). Thus $g(x) \geq 0$ for all $x \in (0, 1)$, and the sum $\sum g(a) \geq 0$ proves the theorem.

## Proof B
Established theorem: For positive reals $a, b, c$ such that $a+b+c=1$, the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ holds.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks: The proof employs Lagrange multipliers to show that any interior critical point must satisfy $h(a)=h(b)=h(c)=\lambda$ for $h(x) = \frac{1}{2\sqrt{x}} + 3\sqrt{3}x - 3\sqrt{3}$ (lines 6-10). Since $h(x)$ is strictly decreasing then strictly increasing, the equation $h(x)=\lambda$ has at most two solutions, implying at least two of $a, b, c$ must be equal (line 10). The case $a=b$ is analyzed via $k(a) = 2\sqrt{a} + \sqrt{1-2a} - 3\sqrt{3}(2a - 3a^2)$ (line 14). The proof correctly identifies $a=1/3$ as a local minimum with $k(1/3)=0$ (lines 17-19) and uses the properties of $k'(a)$ to show that the absolute minimum on $[0, 1/2]$ is $0$ (lines 21-25). Finally, the boundary case $c=0$ is analyzed by substituting $x = \sqrt{a} + \sqrt{1-a}$ and showing the resulting concave function $q(x) = x - \frac{3\sqrt{3}}{4}(x^2-1)^2$ is positive on $[1, \sqrt{2}]$ (lines 28-35).

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct. Proof A is significantly more elegant and direct, reducing the multivariate inequality to a simple single-variable inequality $g(x) \geq 0$ that holds for each variable independently. Proof B is a correct but more laborious application of Lagrange multipliers and boundary analysis. Proof A's approach is more efficient and provides a cleaner derivation.