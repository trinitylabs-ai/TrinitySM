To prove the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for positive reals $a, b, c$ such that $a+b+c=1$, we proceed as follows:

**1. Transformation of Variables**
Let $x = \sqrt{a}$, $y = \sqrt{b}$, and $z = \sqrt{c}$. Since $a, b, c > 0$, it follows that $x, y, z > 0$. The given constraint $a+b+c=1$ becomes:
\[x^2 + y^2 + z^2 = 1\]
The inequality to prove becomes:
\[x + y + z \geq 3\sqrt{3}(x^2y^2 + y^2z^2 + z^2x^2)\]

**2. Expressing in Terms of Elementary Symmetric Polynomials**
Let $p = x + y + z$, $q = xy + yz + zx$, and $r = xyz$.
The constraint $x^2 + y^2 + z^2 = 1$ can be written as $p^2 - 2q = 1$, which implies:
\[q = \frac{p^2 - 1}{2}\]
The term $x^2y^2 + y^2z^2 + z^2x^2$ can be expressed as:
\[x^2y^2 + y^2z^2 + z^2x^2 = (xy + yz + zx)^2 - 2xyz(x + y + z) = q^2 - 2pr\]
Substituting these into the inequality, we want to show:
\[p \geq 3\sqrt{3}(q^2 - 2pr) \iff p + 6\sqrt{3}pr \geq 3\sqrt{3}q^2\]
Substituting $q = \frac{p^2 - 1}{2}$:
\[p + 6\sqrt{3}pr \geq 3\sqrt{3} \left( \frac{p^2 - 1}{2} \right)^2 = \frac{3\sqrt{3}}{4}(p^2 - 1)^2\]

**3. Range of $p$**
From $x^2+y^2+z^2=1$ and $x,y,z > 0$, we have $p^2 = 1 + 2q$. Since $q \leq \frac{p^2}{3}$, it follows that $p^2 \leq 1 + \frac{2}{3}p^2 \implies p^2 \leq 3 \implies p \leq \sqrt{3}$. Also, $p^2 > 1 \implies p > 1$. Thus, $p \in (1, \sqrt{3}]$.

**4. Application of Schur's Inequality**
Schur's Inequality states that for $x, y, z \geq 0$, $\sum x^3 + 3xyz \geq \sum xy(x+y)$. In terms of $p, q, r$, this is:
\[p^3 - 3pq + 3r + 3r \geq pq - 3r \implies 9r \geq 4pq - p^3 = p(4q - p^2)\]
Substituting $q = \frac{p^2 - 1}{2}$, we have $4q - p^2 = 2(p^2 - 1) - p^2 = p^2 - 2$. Thus:
\[r \geq \max\left(0, \frac{p(p^2 - 2)}{9}\right)\]

**5. Case Analysis**
**Case 1: $1 < p \leq \sqrt{2}$**
In this range, $p^2 - 2 \leq 0$, so the lower bound on $r$ is $r \geq 0$. The inequality $p + 6\sqrt{3}pr \geq \frac{3\sqrt{3}}{4}(p^2 - 1)^2$ is satisfied if it holds for $r=0$. Let $f(p) = p - \frac{3\sqrt{3}}{4}(p^2 - 1)^2$.
$f(1) = 1 > 0$ and $f(\sqrt{2}) = \sqrt{2} - \frac{3\sqrt{3}}{4} \approx 1.414 - 1.299 > 0$.
Since $f'(p) = 1 - 3\sqrt{3}p(p^2 - 1)$, $f$ increases then decreases on $(1, \sqrt{2}]$. Thus, $f(p) > 0$ for all $p \in (1, \sqrt{2}]$.

**Case 2: $\sqrt{2} < p \leq \sqrt{3}$**
Here, $r \geq \frac{p(p^2 - 2)}{9}$. Substituting this into the inequality:
\[p + 6\sqrt{3}p \left( \frac{p(p^2 - 2)}{9} \right) \geq \frac{3\sqrt{3}}{4}(p^2 - 1)^2 \iff p + \frac{2\sqrt{3}}{3} p^2(p^2 - 2) \geq \frac{3\sqrt{3}}{4}(p^2 - 1)^2\]
Multiplying by 12:
\[12p + 8\sqrt{3}p^4 - 16\sqrt{3}p^2 \geq 9\sqrt{3}(p^4 - 2p^2 + 1) \iff 0 \geq \sqrt{3}p^4 - 2\sqrt{3}p^2 - 12p + 9\sqrt{3}\]
Let $g(p) = \sqrt{3}p^4 - 2\sqrt{3}p^2 - 12p + 9\sqrt{3}$.
$g(\sqrt{3}) = 9\sqrt{3} - 6\sqrt{3} - 12\sqrt{3} + 9\sqrt{3} = 0$.
$g'(p) = 4\sqrt{3}p^3 - 4\sqrt{3}p - 12$ and $g''(p) = 12\sqrt{3}p^2 - 4\sqrt{3} = 4\sqrt{3}(3p^2 - 1) > 0$ for $p > 1$.
Since $g$ is convex and $g'(\sqrt{3}) = 36 - 12 - 12 = 12 > 0$, it follows that $g(p) \leq g(\sqrt{3}) = 0$ for all $p \in [\sqrt{2}, \sqrt{3}]$.

Thus, the inequality holds for all $p \in (1, \sqrt{3}]$, with equality if and only if $p = \sqrt{3}$, which corresponds to $a=b=c=1/3$.

\(\square\)
