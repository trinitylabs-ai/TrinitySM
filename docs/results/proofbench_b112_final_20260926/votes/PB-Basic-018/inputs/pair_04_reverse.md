# Problem

Let $x$ and $y$ be positive integers satisfying $2x^2 + x = 3y^2 + y$. Prove that $2x+2y+1$ is a perfect square.

# Proof A

1: To prove that $2x + 2y + 1$ is a perfect square for positive integers $x$ and $y$ satisfying $2x^2 + x = 3y^2 + y$, we proceed as follows.
2: 
3: **1. Transformation of the Equation**
4: The given equation is $2x^2 + x = 3y^2 + y$. Multiplying both sides by 8, we obtain:
5: \[ 16x^2 + 8x = 24y^2 + 8y \]
6: Completing the square on the left side:
7: \[ (4x + 1)^2 - 1 = 24y^2 + 8y \implies (4x + 1)^2 = 24y^2 + 8y + 1 \]
8: Let $k = 4x + 1$. Since $x$ is a positive integer, $k$ is an integer greater than 1. We have $k^2 = 24y^2 + 8y + 1$. Multiplying this equation by 3 gives:
9: \[ 3k^2 = 72y^2 + 24y + 3 = 2(36y^2 + 12y + 1) + 1 = 2(6y + 1)^2 + 1 \]
10: Let $z = 6y + 1$. Since $y$ is a positive integer, $z$ is an integer greater than 1. The equation becomes:
11: \[ 3k^2 - 2z^2 = 1 \]
12: 
13: **2. Solving the Pell-like Equation**
14: The equation $3k^2 - 2z^2 = 1$ is a Pell-like equation. The fundamental solution is $(k_0, z_0) = (1, 1)$. The solutions $(k_n, z_n)$ can be generated using the fundamental solution of the associated Pell equation $u^2 - 6v^2 = 1$, which is $(u, v) = (5, 2)$. The general solutions are given by the relation:
15: \[ k_n\sqrt{3} + z_n\sqrt{2} = (\sqrt{3} + \sqrt{2})(5 + 2\sqrt{6})^n \]
16: From this, we derive the recurrence relations:
17: \[ k_{n+1} = 5k_n + 4z_n, \quad z_{n+1} = 6k_n + 5z_n \]
18: For $x$ and $y$ to be integers, we require $k_n \equiv 1 \pmod 4$ and $z_n \equiv 1 \pmod 6$.
19: - Modulo 4: $k_{n+1} \equiv 5k_n + 4z_n \equiv k_n \pmod 4$. Since $k_0 = 1$, $k_n \equiv 1 \pmod 4$ for all $n \ge 0$.
20: - Modulo 6: $z_{n+1} \equiv 6k_n + 5z_n \equiv -z_n \pmod 6$. Since $z_0 = 1$, we have $z_n \equiv 1 \pmod 6$ if and only if $n$ is even.
21: Thus, for $x, y$ to be positive integers, $n$ must be an even integer $n = 2m$ for $m \in \mathbb{Z}^+$.
22: 
23: **3. Proving the Perfect Square Property**
24: We wish to show that $S = 2x + 2y + 1$ is a perfect square. Substituting $x = \frac{k_{2m}-1}{4}$ and $y = \frac{z_{2m}-1}{6}$:
25: \[ S = 2\left(\frac{k_{2m}-1}{4}\right) + 2\left(\frac{z_{2m}-1}{6}\right) + 1 = \frac{k_{2m}-1}{2} + \frac{z_{2m}-1}{3} + 1 = \frac{3k_{2m} + 2z_{2m} + 1}{6} \]
26: Let $\alpha = 5 + 2\sqrt{6}$ and $\beta = 5 - 2\sqrt{6}$. The closed forms for $k_n$ and $z_n$ are:
27: \[ k_n = \frac{3+\sqrt{6}}{6}\alpha^n + \frac{3-\sqrt{6}}{6}\beta^n, \quad z_n = \frac{2+\sqrt{6}}{4}\alpha^n + \frac{2-\sqrt{6}}{4}\beta^n \]
28: Calculating $3k_{2m} + 2z_{2m}$:
29: \[ 3k_{2m} + 2z_{2m} = \left(\frac{3+\sqrt{6}}{2} + \frac{2+\sqrt{6}}{2}\right)\alpha^{2m} + \left(\frac{3-\sqrt{6}}{2} + \frac{2-\sqrt{6}}{2}\right)\beta^{2m} = \frac{5+2\sqrt{6}}{2}\alpha^{2m} + \frac{5-2\sqrt{6}}{2}\beta^{2m} \]
30: Since $5 + 2\sqrt{6} = \alpha$ and $5 - 2\sqrt{6} = \beta$, we have $3k_{2m} + 2z_{2m} = \frac{1}{2}(\alpha^{2m+1} + \beta^{2m+1})$. Thus:
31: \[ S = \frac{\frac{1}{2}(\alpha^{2m+1} + \beta^{2m+1}) + 1}{6} = \frac{\alpha^{2m+1} + \beta^{2m+1} + 2}{12} \]
32: Now we compare this to $k_m^2$:
33: \[ k_m^2 = \left(\frac{3+\sqrt{6}}{6}\alpha^m + \frac{3-\sqrt{6}}{6}\beta^m\right)^2 = \frac{(3+\sqrt{6})^2\alpha^{2m} + (3-\sqrt{6})^2\beta^{2m} + 2(3+\sqrt{6})(3-\sqrt{6})(\alpha\beta)^m}{36} \]
34: Using $(3 \pm \sqrt{6})^2 = 15 \pm 6\sqrt{6} = 3(5 \pm 2\sqrt{6})$ and $\alpha\beta = 1$:
35: \[ k_m^2 = \frac{3\alpha \cdot \alpha^{2m} + 3\beta \cdot \beta^{2m} + 2(9-6)}{36} = \frac{3\alpha^{2m+1} + 3\beta^{2m+1} + 6}{36} = \frac{\alpha^{2m+1} + \beta^{2m+1} + 2}{12} \]
36: Hence, $S = k_m^2$. Since $k_m$ is an integer, $2x + 2y + 1$ is a perfect square.
37: 
38: \(\square\)

# Proof B

1: Let $x$ and $y$ be positive integers satisfying the equation $2x^2 + x = 3y^2 + y$. We wish to prove that $2x + 2y + 1$ is a perfect square.
2: 
3: First, we transform the given equation into a Pell-like form. Multiplying the equation by 8, we obtain:
4: \[ 16x^2 + 8x = 24y^2 + 8y \]
5: Completing the square on the left side:
6: \[ (4x+1)^2 - 1 = 24y^2 + 8y \]
7: \[ (4x+1)^2 = 24y^2 + 8y + 1 \]
8: Let $u = 4x+1$ and $w = 6y+1$. Then $y = \frac{w-1}{6}$. Substituting this into the equation for $u^2$:
9: \[ u^2 = 24\left(\frac{w-1}{6}\right)^2 + 8\left(\frac{w-1}{6}\right) + 1 = \frac{24(w^2-2w+1)}{36} + \frac{4(w-1)}{3} + 1 \]
10: \[ u^2 = \frac{2w^2-4w+2}{3} + \frac{4w-4}{3} + \frac{3}{3} = \frac{2w^2+1}{3} \]
11: Rearranging this gives the Pell-like equation:
12: \[ 3u^2 - 2w^2 = 1 \]
13: To solve this, we multiply by 3 to obtain $(3u)^2 - 6w^2 = 3$. Let $U = 3u$. The equation $U^2 - 6w^2 = 3$ is a Pell-like equation. The fundamental solution to the associated Pell equation $U^2 - 6w^2 = 1$ is $5 + 2\sqrt{6}$. The fundamental solution to $U^2 - 6w^2 = 3$ is $(U_0, w_0) = (3, 1)$. All solutions $(U_n, w_n)$ are given by:
14: \[ U_n + w_n\sqrt{6} = (3 + \sqrt{6})(5+2\sqrt{6})^n \]
15: Substituting $U_n = 3u_n$ and dividing by $\sqrt{3}$, we obtain the general solution for $u_n$ and $w_n$:
16: \[ u_n\sqrt{3} + w_n\sqrt{2} = (\sqrt{3} + \sqrt{2})(5+2\sqrt{6})^n \]
17: Let $\lambda = 5+2\sqrt{6}$ and $\mu = 5-2\sqrt{6}$. Note that $\lambda + \mu = 10$ and $\lambda\mu = 1$. Since $u_n$ and $w_n$ are linear combinations of $\lambda^n$ and $\mu^n$, they satisfy the linear recurrence $a_{n+1} = 10a_n - a_{n-1}$.
18: 
19: We check the condition for $y = \frac{w_n-1}{6}$ to be an integer by examining $w_n \pmod 6$. We have $w_0 = 1$ and $w_1 = 6(1) + 5(1) = 11 \equiv 5 \pmod 6$. Using the recurrence $w_{n+1} = 10w_n - w_{n-1} \equiv 4w_n - w_{n-1} \pmod 6$:
20: - $w_2 \equiv 4(5) - 1 = 19 \equiv 1 \pmod 6$
21: - $w_3 \equiv 4(1) - 5 = -1 \equiv 5 \pmod 6$
22: By induction, $w_n \equiv 1 \pmod 6$ if and only if $n$ is even. Let $n=2m$. For $m \ge 1$, $x$ and $y$ are positive integers.
23: 
24: We now evaluate $2x+2y+1$ for $n=2m$:
25: \[ 2x+2y+1 = 2\left(\frac{u_{2m}-1}{4}\right) + 2\left(\frac{w_{2m}-1}{6}\right) + 1 = \frac{u_{2m}-1}{2} + \frac{w_{2m}-1}{3} + 1 = \frac{3u_{2m} + 2w_{2m} + 1}{6} \]
26: Using the Binet-like formulas for $u_n$ and $w_n$ derived from $u_n\sqrt{3} + w_n\sqrt{2} = (\sqrt{3} + \sqrt{2})\lambda^n$ and its conjugate $u_n\sqrt{3} - w_n\sqrt{2} = (\sqrt{3} - \sqrt{2})\mu^n$:
27: \[ u_n = \frac{3+\sqrt{6}}{6}\lambda^n + \frac{3-\sqrt{6}}{6}\mu^n, \quad w_n = \frac{2+\sqrt{6}}{4}\lambda^n + \frac{2-\sqrt{6}}{4}\mu^n \]
28: Substituting these into the expression for $3u_{2m} + 2w_{2m} + 1$:
29: \[ 3u_{2m} + 2w_{2m} + 1 = 3\left(\frac{3+\sqrt{6}}{6}\lambda^{2m} + \frac{3-\sqrt{6}}{6}\mu^{2m}\right) + 2\left(\frac{2+\sqrt{6}}{4}\lambda^{2m} + \frac{2-\sqrt{6}}{4}\mu^{2m}\right) + 1 \]
30: \[ = \left(\frac{3+\sqrt{6}}{2} + \frac{2+\sqrt{6}}{2}\right)\lambda^{2m} + \left(\frac{3-\sqrt{6}}{2} + \frac{2-\sqrt{6}}{2}\right)\mu^{2m} + 1 = \frac{5+2\sqrt{6}}{2}\lambda^{2m} + \frac{5-2\sqrt{6}}{2}\mu^{2m} + 1 \]
31: Now, we calculate $6u_m^2$:
32: \[ 6u_m^2 = 6\left(\frac{3+\sqrt{6}}{6}\lambda^m + \frac{3-\sqrt{6}}{6}\mu^m\right)^2 = 6\left(\frac{(3+\sqrt{6})^2}{36}\lambda^{2m} + \frac{(3-\sqrt{6})^2}{36}\mu^{2m} + \frac{2(3+\sqrt{6})(3-\sqrt{6})}{36}\lambda^m\mu^m\right) \]
33: Since $(3 \pm \sqrt{6})^2 = 15 \pm 6\sqrt{6}$ and $(3+\sqrt{6})(3-\sqrt{6}) = 3$, and $\lambda\mu = 1$:
34: \[ 6u_m^2 = 6\left(\frac{15+6\sqrt{6}}{36}\lambda^{2m} + \frac{15-6\sqrt{6}}{36}\mu^{2m} + \frac{6}{36}\right) = \frac{5+2\sqrt{6}}{2}\lambda^{2m} + \frac{5-2\sqrt{6}}{2}\mu^{2m} + 1 \]
35: Thus, $3u_{2m} + 2w_{2m} + 1 = 6u_m^2$, and we conclude:
36: \[ 2x+2y+1 = \frac{6u_m^2}{6} = u_m^2 \]
37: Since $u_m$ is an integer, $2x+2y+1$ is a perfect square.
