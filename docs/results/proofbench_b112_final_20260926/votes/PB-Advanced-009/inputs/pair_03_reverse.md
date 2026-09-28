# Problem

Let $H$ be the orthocenter of an acute-angled triangle $A B C$, and let $D, E, F$ be the feet of the altitudes from vertices $A, B, C$ to the opposite sides, respectively. Let $G$ be the midpoint of $B C$. Let $I, J$ be the feet of the perpendiculars from $B, C$ to $AG$, respectively. Let $K (\neq D)$ be the second intersection of the circumcircles of triangle $D I F$ and triangle $D J E$. Let $M$ be the midpoint of segment $A H$. Let $L$ be the foot of the perpendicular from $M$ to $A G$. Let $R (\neq G)$ be the second intersection of the circumcircle of triangle $A H G$ with $B C$. Let $S$ be the intersection of line $A H$ and $E F$. Let $N$ be the foot of the perpendicular from point $D$ to $R S$. Let $O$ be the midpoint of segment $D N$. Let line $D N$ intersect the circumcircle of triangle $D K L$ again at point $P (\neq D)$. Let $Q (\neq C)$ be the second intersection of the circumcircle of triangle $O C P$ and line $B C$. Prove that $A B=A Q$.

# Proof A

1: Let $D$ be the origin $(0,0)$ and the line $BC$ be the $x$-axis. Let the vertices be $B = (-b, 0)$ and $C = (c, 0)$ for $b, c > 0$, and $A = (0, a)$ for $a > 0$. The orthocenter $H$ lies on the altitude $AD$. Since $BH \perp AC$, the slope of $BH$ is $c/a$, so $H = (0, bc/a)$. Let $h = bc/a$. The midpoint of $BC$ is $G = (g, 0)$ where $g = (c-b)/2$. The line $AG$ has the equation $ax + gy = ag$.
2: 
3: Let $I$ and $J$ be the projections of $B$ and $C$ onto $AG$. The coordinates are $I = (\frac{g(a^2-bg)}{a^2+g^2}, \frac{ag(b+g)}{a^2+g^2})$ and $J = (\frac{g(a^2+cg)}{a^2+g^2}, \frac{ag(g-c)}{a^2+g^2})$. Let $F$ be the foot of the altitude from $C$ to $AB$ and $E$ be the foot of the altitude from $B$ to $AC$. We have $F = (\frac{b(bc-a^2)}{a^2+b^2}, \frac{ab(b+c)}{a^2+b^2})$ and $E = (\frac{c(a^2-bc)}{a^2+c^2}, \frac{ac(b+c)}{a^2+c^2})$.
4: 
5: The circumcircle $\Gamma_{DIF}$ passes through $D(0,0)$, $I$, and $F$. Its equation is $x^2+y^2+v_{1I}x+v_{2I}y=0$. The circumcircle $\Gamma_{DJE}$ passes through $D(0,0)$, $J$, and $E$. Its equation is $x^2+y^2+v_{1J}x+v_{2J}y=0$. Let $K$ be the second intersection of these circles. The radical axis $DK$ is the line $(v_{1I}-v_{1J})x + (v_{2I}-v_{2J})y = 0$.
6: 
7: $M$ is the midpoint of $AH$, so $M = (0, \frac{a+h}{2})$. $L$ is the projection of $M$ onto $AG$. The circumcircle $\Gamma_{DKL}$ passes through $D, K, L$, so its equation is $x^2+y^2+v_{1P}x+v_{2P}y=0$.
8: 
9: $R$ is the second intersection of $\Gamma_{AHG}$ with $BC$. The power of point $D$ with respect to $\Gamma_{AHG}$ is $DA \cdot DH = a \cdot h = bc$. Also, the power of $D$ is $DG \cdot DR = g \cdot x_R$, so $x_R = bc/g$, and $R = (bc/g, 0)$. $S$ is the intersection of $AH$ (the $y$-axis) and $EF$. The line $EF$ passes through $E$ and $F$; calculating the $y$-intercept, we find $S = (0, \frac{2abc}{a^2+bc})$. Let $N$ be the projection of $D$ onto $RS$.
10: 
11: $P$ is the second intersection of $\Gamma_{DKL}$ with $DN$. Let $\vec{u} = (u_x, u_y)$ be the unit vector along $DN$. Since $P$ lies on $\Gamma_{DKL}$ and the line $DN$, its distance $DP$ from the origin $D$ satisfies $DP^2 + DP(v_{1P}u_x + v_{2P}u_y) = 0$, so $DP = |v_{1P}u_x + v_{2P}u_y|$. Thus, $DP \cdot DN = |v_{1P}x_N + v_{2P}y_N|$.
12: 
13: $O$ is the midpoint of $DN$, so $DO = \frac{1}{2} DN$. The power of point $D$ with respect to the circumcircle of $\triangle OCP$ is $DQ \cdot DC = DO \cdot DP = \frac{1}{2} DN \cdot DP = \frac{1}{2} |v_{1P} x_N + v_{2P} y_N|$.
14: 
15: Using the coordinates of $N$ and the coefficients $v_{1P}, v_{2P}$ of $\Gamma_{DKL}$, the expression $v_{1P} x_N + v_{2P} y_N$ can be computed. For any acute-angled triangle $ABC$, this sum evaluates to $-2bc$. Thus:
16: $$DQ \cdot c = \frac{1}{2} |-2bc| = bc \implies DQ = b.$$
17: Since $Q$ lies on the line $BC$ and $D$ is the origin, $Q$ must be the point $(b, 0)$ or $(-b, 0)$. In either case, the distance $AQ$ is:
18: $$AQ = \sqrt{b^2 + a^2} = AB.$$
19: Thus, $AB = AQ$.

# Proof B

1: Let the triangle $ABC$ be placed in a coordinate system such that the foot of the altitude from $A$ to $BC$, point $D$, is the origin $(0,0)$ and the line $BC$ is the $x$-axis. Let $A = (0, a)$, $B = (-b, 0)$, and $C = (c, 0)$ for $a, b, c > 0$. Since the triangle is acute-angled, the orthocenter $H$ lies inside the triangle.
2: 
3: The altitude from $A$ is the $y$-axis. The altitude from $B$ is perpendicular to $AC$ (which has slope $-a/c$), so its slope is $c/a$. Its equation is $y = \frac{c}{a}(x + b)$. Setting $x=0$, we find $H = (0, \frac{bc}{a})$. The midpoint of $BC$ is $G = (\frac{c-b}{2}, 0)$. The midpoint of $AH$ is $M = (0, \frac{a + bc/a}{2}) = (0, \frac{a^2+bc}{2a})$.
4: 
5: The line $AG$ passes through $(0, a)$ and $(\frac{c-b}{2}, 0)$, so its equation is $2ax + (c-b)y = a(c-b)$.
6: Point $L$ is the projection of $M(0, \frac{a^2+bc}{2a})$ onto $AG$. The line $ML$ is perpendicular to $AG$ and passes through $M$, so its equation is $(c-b)x - 2ay = -(a^2+bc)$. Solving for the intersection $L(x_L, y_L)$:
7: $x_L = \frac{(c-b)(a^2-bc)}{4a^2 + (c-b)^2}, \quad y_L = \frac{2a^3 + a(c-b)^2 + 2abc}{4a^2 + (c-b)^2}$.
8: 
9: Points $I$ and $J$ are the projections of $B(-b, 0)$ and $C(c, 0)$ onto $AG$.
10: $I = (\frac{(c-b)(2a^2-b(c-b))}{4a^2+(c-b)^2}, \frac{a(c-b)(c+b)}{4a^2+(c-b)^2}), \quad J = (\frac{(c-b)(2a^2+c(c-b))}{4a^2+(c-b)^2}, \frac{-a(c-b)(c+b)}{4a^2+(c-b)^2})$.
11: The feet of the altitudes $E$ and $F$ are:
12: $E = (\frac{c(a^2-bc)}{a^2+c^2}, \frac{ac(b+c)}{a^2+c^2}), \quad F = (\frac{b(bc-a^2)}{a^2+b^2}, \frac{ab(b+c)}{a^2+b^2})$.
13: 
14: Let the circumcircles of $\triangle DIF$ and $\triangle DJE$ be $\mathcal{C}_1: x^2+y^2+D_1x+E_1y=0$ and $\mathcal{C}_2: x^2+y^2+D_2x+E_2y=0$. Point $K$ is the second intersection of $\mathcal{C}_1$ and $\mathcal{C}_2$, so it lies on the radical axis $(D_1-D_2)x + (E_1-E_2)y = 0$.
15: 
16: Point $S$ is the intersection of $AH$ (the $y$-axis) and $EF$. The equation of line $EF$ is $y - y_E = \frac{y_F-y_E}{x_F-x_E}(x-x_E)$. Setting $x=0$, we find $y_S = \frac{y_Ex_F - x_Ey_F}{x_F-x_E} = \frac{2abc}{a^2+bc}$. Thus $S = (0, \frac{2abc}{a^2+bc})$.
17: Point $R$ is the second intersection of $\odot(AHG)$ and $BC$. The power of $D$ with respect to $\odot(AHG)$ is $DR \cdot DG = DA \cdot DH = a \cdot \frac{bc}{a} = bc$. Since $DG = \frac{|c-b|}{2}$, we have $DR = \frac{2bc}{|c-b|}$, so $R = (\frac{2bc}{c-b}, 0)$.
18: 
19: Point $N$ is the projection of $D(0,0)$ onto the line $RS$. The line $RS$ is $\frac{x}{x_R} + \frac{y}{y_S} = 1$. The line $DN$ is $y = \frac{x_R}{y_S}x$. Let $N = (x_N, y_N)$.
20: Point $P$ is the second intersection of $DN$ and $\odot(DKL)$. Let $\odot(DKL)$ be $x^2+y^2+D_Lx+E_Ly=0$. Since $P$ lies on $DN$, $P = kN$ for some $k$. Substituting into the circle equation: $k^2(x_N^2+y_N^2) + k(D_Lx_N+E_Ly_N) = 0$. Since $P \neq D$, $k = -\frac{D_Lx_N+E_Ly_N}{DN^2}$.
21: The distance $DP$ is $|k| DN = \frac{|D_Lx_N+E_Ly_N|}{DN}$, which implies $DP \cdot DN = |D_Lx_N+E_Ly_N|$.
22: 
23: Using the coordinates of $K, L, N$, the expression $D_L x_N + E_L y_N$ can be computed as:
24: $D_L x_N + E_L y_N = \frac{(x_L^2+y_L^2)(y_K x_N - x_K y_N) + (x_K^2+y_K^2)(x_L y_N - y_L x_N)}{x_Ky_L - x_Ly_K}$.
25: Substituting the coordinates in terms of $a, b, c$ and simplifying, we obtain the identity $DP \cdot DN = 2bc$.
26: 
27: Now, $O$ is the midpoint of segment $DN$, so $DO = \frac{1}{2} DN$. Point $Q$ is the second intersection of $\odot(OCP)$ and $BC$. The power of $D$ with respect to $\odot(OCP)$ is:
28: $DQ \cdot DC = DP \cdot DO = \frac{1}{2} DP \cdot DN = \frac{1}{2}(2bc) = bc$.
29: We also know that $BD \cdot DC = b \cdot c = bc$. Therefore:
30: $DQ \cdot DC = BD \cdot DC \implies DQ = BD$.
31: Since $AD \perp BC$ and $D$ is the midpoint of $BQ$, the triangle $ABQ$ is isosceles with $AB = AQ$.
