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

1: To prove that $2x+2y+1$ is a perfect square given that $x$ and $y$ are positive integers satisfying $2x^2 + x = 3y^2 + y$, we transform the given equation into a Pell-like equation.
2: 
3: **1. Transformation to a Pell Equation**
4: Multiply the given equation $2x^2 + x = 3y^2 + y$ by 8:
5: \[ 16x^2 + 8x = 24y^2 + 8y \]
6: Adding 1 to both sides completes the square on the left:
7: \[ (4x+1)^2 = 24y^2 + 8y + 1 \]
8: To further simplify, multiply the entire equation by 3:
9: \[ 3(4x+1)^2 = 72y^2 + 24y + 3 = 2(36y^2 + 12y + 1) + 1 = 2(6y+1)^2 + 1 \]
10: Let $k = 4x+1$ and $u = 6y+1$. The equation becomes:
11: \[ 3k^2 - 2u^2 = 1 \]
12: 
13: **2. Solving the Pell Equation**
14: To find all positive integer solutions to $3k^2 - 2u^2 = 1$, we multiply by 3 to obtain $9k^2 - 6u^2 = 3$. Let $X = 3k$ and $Y = u$, so we have the equation $X^2 - 6Y^2 = 3$. The fundamental solution to the associated Pell equation $z^2 - 6w^2 = 1$ is $(z_1, w_1) = (5, 2)$. According to the theory of Pell-like equations, any fundamental solution $(X_0, Y_0)$ to $X^2 - 6Y^2 = N$ must satisfy $0 \le Y_0 \le \frac{w_1 \sqrt{|N|}}{\sqrt{2(z_1+1)}}$. For $N=3$, this gives:
15: \[ 0 \le Y_0 \le \frac{2\sqrt{3}}{\sqrt{2(5+1)}} = \frac{2\sqrt{3}}{\sqrt{12}} = 1 \]
16: Testing $Y_0 = 0$ gives $X_0^2 = 3$ (no integer solution), and $Y_0 = 1$ gives $X_0^2 = 9$, so $X_0 = 3$. Thus, the only fundamental solution is $(X_0, Y_0) = (3, 1)$, which corresponds to $(k_0, u_0) = (1, 1)$. All solutions $(k_n, u_n)$ are generated by:
17: \[ k_n\sqrt{3} + u_n\sqrt{2} = (\sqrt{3} + \sqrt{2})(5 + 2\sqrt{6})^n \]
18: From this, we obtain the recurrence relations:
19: \[ k_{n+1} = 5k_n + 4u_n, \quad u_{n+1} = 6k_n + 5u_n \]
20: with $k_0 = 1$ and $u_0 = 1$. For $x$ and $y$ to be integers, we must satisfy $k_n \equiv 1 \pmod 4$ and $u_n \equiv 1 \pmod 6$.
21: - Modulo 4: $k_{n+1} \equiv 5k_n + 4u_n \equiv k_n \pmod 4$. Since $k_0 = 1$, $k_n \equiv 1 \pmod 4$ for all $n \ge 0$.
22: - Modulo 6: $u_{n+1} \equiv 6k_n + 5u_n \equiv -u_n \pmod 6$. Since $u_0 = 1$, $u_n \equiv (-1)^n \pmod 6$.
23: Thus, $u_n \equiv 1 \pmod 6$ if and only if $n$ is even. Let $n = 2m$ for some integer $m \ge 0$.
24: 
25: **3. Proving $2x+2y+1$ is a Square**
26: Express $2x+2y+1$ in terms of $k$ and $u$:
27: \[ 2x + 2y + 1 = 2\left(\frac{k-1}{4}\right) + 2\left(\frac{u-1}{6}\right) + 1 = \frac{k-1}{2} + \frac{u-1}{3} + 1 = \frac{3k + 2u + 1}{6} \]
28: Using the closed forms for $k_n$ and $u_n$ with $\beta = 5+2\sqrt{6}$ and $\bar{\beta} = 5-2\sqrt{6}$:
29: \[ k_n = \frac{3+\sqrt{6}}{6}\beta^n + \frac{3-\sqrt{6}}{6}\bar{\beta}^n, \quad u_n = \frac{2+\sqrt{6}}{4}\beta^n + \frac{2-\sqrt{6}}{4}\bar{\beta}^n \]
30: For $n = 2m$, we calculate $3k_{2m} + 2u_{2m}$:
31: \[ 3k_{2m} + 2u_{2m} = \left( \frac{3+\sqrt{6}}{2} + \frac{2+\sqrt{6}}{2} \right)\beta^{2m} + \left( \frac{3-\sqrt{6}}{2} + \frac{2-\sqrt{6}}{2} \right)\bar{\beta}^{2m} = \frac{5+2\sqrt{6}}{2}\beta^{2m} + \frac{5-2\sqrt{6}}{2}\bar{\beta}^{2m} \]
32: Now, evaluate $k_m^2$:
33: \[ k_m^2 = \left( \frac{3+\sqrt{6}}{6}\beta^m + \frac{3-\sqrt{6}}{6}\bar{\beta}^m \right)^2 = \frac{(3+\sqrt{6})^2}{36}\beta^{2m} + \frac{(3-\sqrt{6})^2}{36}\bar{\beta}^{2m} + \frac{2(3+\sqrt{6})(3-\sqrt{6})}{36}(\beta\bar{\beta})^m \]
34: Since $(3 \pm \sqrt{6})^2 = 15 \pm 6\sqrt{6} = 3(5 \pm 2\sqrt{6})$ and $\beta\bar{\beta} = 1$:
35: \[ k_m^2 = \frac{3(5+2\sqrt{6})}{36}\beta^{2m} + \frac{3(5-2\sqrt{6})}{36}\bar{\beta}^{2m} + \frac{2(3)}{36} = \frac{5+2\sqrt{6}}{12}\beta^{2m} + \frac{5-2\sqrt{6}}{12}\bar{\beta}^{2m} + \frac{1}{6} \]
36: Multiplying by 6 gives:
37: \[ 6k_m^2 = \frac{5+2\sqrt{6}}{2}\beta^{2m} + \frac{5-2\sqrt{6}}{2}\bar{\beta}^{2m} + 1 = 3k_{2m} + 2u_{2m} + 1 \]
38: Thus:
39: \[ 2x + 2y + 1 = \frac{3k_{2m} + 2u_{2m} + 1}{6} = \frac{6k_m^2}{6} = k_m^2 \]
40: Since $k_m$ is an integer, $2x+2y+1$ is a perfect square. \(\square\)
