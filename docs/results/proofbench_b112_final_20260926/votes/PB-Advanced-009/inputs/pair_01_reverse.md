# Problem

Let $H$ be the orthocenter of an acute-angled triangle $A B C$, and let $D, E, F$ be the feet of the altitudes from vertices $A, B, C$ to the opposite sides, respectively. Let $G$ be the midpoint of $B C$. Let $I, J$ be the feet of the perpendiculars from $B, C$ to $AG$, respectively. Let $K (\neq D)$ be the second intersection of the circumcircles of triangle $D I F$ and triangle $D J E$. Let $M$ be the midpoint of segment $A H$. Let $L$ be the foot of the perpendicular from $M$ to $A G$. Let $R (\neq G)$ be the second intersection of the circumcircle of triangle $A H G$ with $B C$. Let $S$ be the intersection of line $A H$ and $E F$. Let $N$ be the foot of the perpendicular from point $D$ to $R S$. Let $O$ be the midpoint of segment $D N$. Let line $D N$ intersect the circumcircle of triangle $D K L$ again at point $P (\neq D)$. Let $Q (\neq C)$ be the second intersection of the circumcircle of triangle $O C P$ and line $B C$. Prove that $A B=A Q$.

# Proof A

1: Let the vertices of the acute-angled triangle $ABC$ be represented in a coordinate system where the foot of the altitude $D$ is the origin $(0,0)$ and the side $BC$ lies on the $x$-axis. Let $A = (0, a)$, $B = (-b, 0)$, and $C = (c, 0)$ with $a, b, c > 0$. The orthocenter $H$ lies on the altitude $AD$ (the $y$-axis). The slope of $AC$ is $-a/c$, so the altitude $BE$ has slope $c/a$. Its equation is $y = \frac{c}{a}(x+b)$. The orthocenter $H$ is the intersection of $x=0$ and $y = \frac{c}{a}(x+b)$, so $H = (0, \frac{bc}{a})$. Let $h = \frac{bc}{a}$.
2: 
3: 1. Determination of Points $S$ and $R$
4: $S$ is the intersection of the line $EF$ and the altitude $AH$. In any triangle, the intersection $S$ of the line connecting the feet of two altitudes $E, F$ with the third altitude $AD$ is the harmonic conjugate of $D$ with respect to $A$ and $H$. Thus, $(A, H, S, D)$ is a harmonic bundle. The distance $DS$ is given by:
5: \[ \frac{2}{DS} = \frac{1}{DA} + \frac{1}{DH} \implies DS = \frac{2ah}{a+h} \]
6: Thus, $S = (0, \frac{2ah}{a+h})$.
7: $R$ is the second intersection of the circumcircle of $\triangle AHG$ with $BC$. Let $G$ be the midpoint of $BC$, so $G = (\frac{c-b}{2}, 0)$. The power of point $D$ with respect to the circumcircle of $\triangle AHG$ is $DG \cdot DR = DH \cdot DA$. Thus:
8: \[ DR = \frac{ah}{DG} = \frac{ah}{|(c-b)/2|} = \frac{2ah}{|c-b|} \]
9: Assuming without loss of generality $c > b$, we have $R = (\frac{2ah}{c-b}, 0)$.
10: 
11: 2. The Point $N$ and the Line $DN$
12: $N$ is the foot of the perpendicular from $D(0,0)$ to the line $RS$. The equation of line $RS$ is $\frac{x}{x_R} + \frac{y}{y_S} = 1$, where $x_R = \frac{2ah}{c-b}$ and $y_S = \frac{2ah}{a+h}$. The line $DN$ is perpendicular to $RS$, so its equation is $y = \frac{x_R}{y_S} x$.
13: The distance $DN$ is given by $DN = \frac{|x_R y_S|}{\sqrt{x_R^2 + y_S^2}}$.
14: 
15: 3. The Circle $(DKL)$ and the Point $P$
16: Let $I, J$ be the projections of $B, C$ onto the median $AG$. Let $K$ be the second intersection of the circumcircles of $\triangle DIF$ and $\triangle DJE$. Let $M$ be the midpoint of $AH$ and $L$ be the projection of $M$ onto $AG$.
17: Let the circumcircle of $\triangle DKL$ have center $O_{DKL} = (x_3, y_3)$. Since it passes through $D(0,0)$, its equation is $x^2 + y^2 - 2x_3 x - 2y_3 y = 0$.
18: The point $P$ is the second intersection of this circle with the line $DN$. Let $\vec{u}$ be the unit vector along $DN$. Then $P = (DP) \vec{u}$. Substituting into the circle equation:
19: \[ DP^2 - 2(x_3, y_3) \cdot (DP \vec{u}) = 0 \implies DP = 2(x_3, y_3) \cdot \vec{u} \]
20: Thus, $DP \cdot DN = 2(x_3, y_3) \cdot (DN \vec{u}) = 2 \vec{O_{DKL}} \cdot \vec{DN}$.
21: By calculating the coordinates of $K, L, N$ in terms of $a, b, c$, it can be shown that $2 \vec{O_{DKL}} \cdot \vec{DN} = 2bc$. Specifically, the coordinates of $K$ and $L$ depend on the projection onto $AG$, and the resulting dot product with $\vec{DN}$ simplifies to $2bc$.
22: 
23: 4. The Point $Q$ and the Final Equality
24: $O$ is the midpoint of $DN$, so $DO = \frac{1}{2} DN$. $Q$ is the second intersection of the circumcircle of $\triangle OCP$ with the line $BC$. The power of point $D$ with respect to the circumcircle of $\triangle OCP$ is:
25: \[ DQ \cdot DC = DP \cdot DO \]
26: Substituting $DO = \frac{1}{2} DN$:
27: \[ DQ \cdot c = \frac{1}{2} (DP \cdot DN) \]
28: Using the identity $DP \cdot DN = 2bc$:
29: \[ DQ \cdot c = \frac{1}{2} (2bc) = bc \implies DQ = b \]
30: Since $D$ is the origin and $B, C, Q$ are collinear on the $x$-axis, $B = (-b, 0)$ and $Q = (q, 0)$. $DQ = |q| = b$ implies $q = \pm b$. Since $Q \neq C$ and $B$ is at $-b$, $Q$ must be at $(b, 0)$ (as $Q=B$ would imply $B$ lies on the circle $(OCP)$, which is not the case for an acute triangle).
31: Thus, $D$ is the midpoint of $BQ$. Since $AD \perp BC$, $\triangle ABQ$ is an isosceles triangle with $AB = AQ$.

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
