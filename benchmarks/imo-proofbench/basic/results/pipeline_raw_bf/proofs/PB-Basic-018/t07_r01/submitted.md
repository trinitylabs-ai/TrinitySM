To prove that $2x+2y+1$ is a perfect square for positive integers $x$ and $y$ satisfying $2x^2 + x = 3y^2 + y$, we begin by treating the equation as a quadratic in $x$:
\[2x^2 + x - (3y^2 + y) = 0\]
Using the quadratic formula to solve for $x$, we have:
\[x = \frac{-1 + \sqrt{1 - 4(2)(-(3y^2 + y))}}{4} = \frac{-1 + \sqrt{24y^2 + 8y + 1}}{4}\]
For $x$ to be an integer, the discriminant $24y^2 + 8y + 1$ must be a perfect square. Let $24y^2 + 8y + 1 = k^2$ for some integer $k \ge 0$. Then $x = \frac{k-1}{4}$, which implies $k = 4x+1$. Multiplying the equation $k^2 = 24y^2 + 8y + 1$ by 3, we obtain:
\[3k^2 = 72y^2 + 24y + 3 = 2(36y^2 + 12y + 1) + 1 = 2(6y+1)^2 + 1\]
This can be rearranged as a Pell-like equation:
\[3k^2 - 2(6y+1)^2 = 1\]
Let $u = k = 4x+1$ and $v = 6y+1$. The equation is $3u^2 - 2v^2 = 1$. The general solutions $(u_n, v_n)$ for this equation are given by:
\[u_n\sqrt{3} + v_n\sqrt{2} = (\sqrt{3} + \sqrt{2})(5 + 2\sqrt{6})^n\]
We wish to prove that $S = 2x + 2y + 1$ is a perfect square. Substituting $x = \frac{u-1}{4}$ and $y = \frac{v-1}{6}$, we find:
\[S = 2\left(\frac{u-1}{4}\right) + 2\left(\frac{v-1}{6}\right) + 1 = \frac{u-1}{2} + \frac{v-1}{3} + 1 = \frac{3u - 3 + 2v - 2 + 6}{6} = \frac{3u + 2v + 1}{6}\]
Let $\alpha = 5 + 2\sqrt{6}$. The general solutions for $u_n$ and $v_n$ are:
\[u_n = \frac{(\sqrt{3}+\sqrt{2})\alpha^n + (\sqrt{3}-\sqrt{2})\alpha^{-n}}{2\sqrt{3}}, \quad v_n = \frac{(\sqrt{3}+\sqrt{2})\alpha^n - (\sqrt{3}-\sqrt{2})\alpha^{-n}}{2\sqrt{2}}\]
Calculating the linear combination $3u_n + 2v_n$:
\[3u_n + 2v_n = \frac{\sqrt{3}}{2} [(\sqrt{3}+\sqrt{2})\alpha^n + (\sqrt{3}-\sqrt{2})\alpha^{-n}] + \frac{1}{\sqrt{2}} [(\sqrt{3}+\sqrt{2})\alpha^n - (\sqrt{3}-\sqrt{2})\alpha^{-n}]\]
\[= \alpha^n \left( \frac{3+\sqrt{6}}{2} + \frac{\sqrt{6}+2}{2} \right) + \alpha^{-n} \left( \frac{3-\sqrt{6}}{2} - \frac{\sqrt{6}-2}{2} \right) = \frac{5+2\sqrt{6}}{2}\alpha^n + \frac{5-2\sqrt{6}}{2}\alpha^{-n} = \frac{\alpha^{n+1} + \alpha^{-(n+1)}}{2}\]
Thus, the expression for $S$ becomes:
\[S_n = \frac{\frac{\alpha^{n+1} + \alpha^{-(n+1)}}{2} + 1}{6} = \frac{\alpha^{n+1} + \alpha^{-(n+1)} + 2}{12} = \frac{(\alpha^{(n+1)/2} + \alpha^{-(n+1)/2})^2}{12}\]
For $x, y$ to be positive integers, we require $v_n \equiv 1 \pmod{6}$. From the recurrence $v_{n+1} = 6u_n + 5v_n \equiv -v_n \pmod{6}$, and $v_0 = 1$, we see that $v_n \equiv 1 \pmod{6}$ if and only if $n$ is even. Let $n = 2m$. Then:
\[S_{2m} = \frac{(\alpha^{m+1/2} + \alpha^{-(m+1/2)})^2}{12}\]
Note that $\alpha = (\sqrt{3} + \sqrt{2})^2$. Let $\phi = \sqrt{3} + \sqrt{2}$. Then $\alpha^{m+1/2} + \alpha^{-(m+1/2)} = \phi^{2m+1} + \phi^{-(2m+1)}$. For any odd integer $k = 2m+1$, we can write $\phi^k = b_k\sqrt{3} + a_k\sqrt{2}$ for some integers $a_k, b_k$. Then $\phi^{-k} = b_k\sqrt{3} - a_k\sqrt{2}$ because $3b_k^2 - 2a_k^2 = 1$. It follows that:
\[\phi^k + \phi^{-k} = (b_k\sqrt{3} + a_k\sqrt{2}) + (b_k\sqrt{3} - a_k\sqrt{2}) = 2b_k\sqrt{3}\]
Substituting this into the formula for $S_{2m}$:
\[S_{2m} = \frac{(2b_k\sqrt{3})^2}{12} = \frac{12b_k^2}{12} = b_k^2\]
Since $b_k$ is an integer, $2x+2y+1$ is a perfect square. \(\square\)
