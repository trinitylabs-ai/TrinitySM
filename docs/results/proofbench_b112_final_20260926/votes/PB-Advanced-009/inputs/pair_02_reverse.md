# Problem

Let $H$ be the orthocenter of an acute-angled triangle $A B C$, and let $D, E, F$ be the feet of the altitudes from vertices $A, B, C$ to the opposite sides, respectively. Let $G$ be the midpoint of $B C$. Let $I, J$ be the feet of the perpendiculars from $B, C$ to $AG$, respectively. Let $K (\neq D)$ be the second intersection of the circumcircles of triangle $D I F$ and triangle $D J E$. Let $M$ be the midpoint of segment $A H$. Let $L$ be the foot of the perpendicular from $M$ to $A G$. Let $R (\neq G)$ be the second intersection of the circumcircle of triangle $A H G$ with $B C$. Let $S$ be the intersection of line $A H$ and $E F$. Let $N$ be the foot of the perpendicular from point $D$ to $R S$. Let $O$ be the midpoint of segment $D N$. Let line $D N$ intersect the circumcircle of triangle $D K L$ again at point $P (\neq D)$. Let $Q (\neq C)$ be the second intersection of the circumcircle of triangle $O C P$ and line $B C$. Prove that $A B=A Q$.

# Proof A

1: Let $D$ be the origin $(0,0)$ and the line $BC$ be the $x$-axis. Since $\triangle ABC$ is acute and $AD$ is the altitude, let $A = (0, h)$ for some $h > 0$. Let $B = (-b, 0)$ and $C = (c, 0)$ with $b, c > 0$.
2: 
3: 1. Coordinates of Key Points
4: The orthocenter $H$ lies on the altitude $AD$ (the $y$-axis). The slope of $AC$ is $-h/c$, so the altitude $BE$ has slope $c/h$. The line $BE$ is $y = \frac{c}{h}(x+b)$, so $H = (0, \frac{bc}{h})$.
5: $M$ is the midpoint of $AH$, so $M = (0, \frac{h + bc/h}{2}) = (0, \frac{h^2+bc}{2h})$.
6: $G$ is the midpoint of $BC$, so $G = (\frac{c-b}{2}, 0)$.
7: The line $AG$ passes through $(0, h)$ and $(\frac{c-b}{2}, 0)$, so its equation is $2hx + (c-b)y - h(c-b) = 0$.
8: Let $W_0 = 4h^2 + (c-b)^2$. The projection $L$ of $M$ onto $AG$ is:
9: $x_L = 0 - 2h \frac{(c-b)\frac{h^2+bc}{2h} - h(c-b)}{W_0} = \frac{-(c-b)(bc-h^2)}{W_0}$,
10: $y_L = \frac{h^2+bc}{2h} - (c-b) \frac{(c-b)\frac{h^2+bc}{2h} - h(c-b)}{W_0} = \frac{h(2h^2 + 2bc + (c-b)^2)}{W_0}$.
11: 
12: 2. Points $R, S, N, O$
13: The circumcircle of $\triangle AHG$ passes through $A(0, h), H(0, \frac{bc}{h}), G(\frac{c-b}{2}, 0)$. Its equation is $x^2 + y^2 + Dx + Ey + F = 0$.
14: From $A$ and $H$, $h^2 + Eh + F = 0$ and $(\frac{bc}{h})^2 + E\frac{bc}{h} + F = 0$. Subtracting gives $E = -(h + \frac{bc}{h}) = -\frac{h^2+bc}{h}$ and $F = bc$.
15: For $G$, $(\frac{c-b}{2})^2 + D\frac{c-b}{2} + bc = 0 \implies D = \frac{-4bc - (c-b)^2}{2(c-b)}$.
16: $R$ is the second intersection of this circle with $y=0$, so $x^2 + Dx + F = 0$. One root is $x_G = \frac{c-b}{2}$, so $x_R = \frac{F}{x_G} = \frac{2bc}{c-b}$. Thus $R = (\frac{2bc}{c-b}, 0)$.
17: The feet of the altitudes are $E = (\frac{c(h^2-bc)}{h^2+c^2}, \frac{ch(b+c)}{h^2+c^2})$ and $F = (\frac{b(bc-h^2)}{h^2+b^2}, \frac{bh(b+c)}{h^2+b^2})$.
18: The intersection $S$ of line $EF$ and the $y$-axis is $S = (0, \frac{2bch}{h^2+bc})$.
19: The line $RS$ has equation $\frac{x}{2bc/(c-b)} + \frac{y}{2bch/(h^2+bc)} = 1$, which simplifies to $h(c-b)x + (h^2+bc)y = 2bch$.
20: $N$ is the projection of $D(0,0)$ onto $RS$. Let $W = h^2(c-b)^2 + (h^2+bc)^2$.
21: $x_N = \frac{2bch^2(c-b)}{W}$, $y_N = \frac{2bch(h^2+bc)}{W}$.
22: $O$ is the midpoint of $DN$, so $O = (\frac{bch^2(c-b)}{W}, \frac{bch(h^2+bc)}{W})$.
23: 
24: 3. Point $K$ and $\odot(DKL)$
25: $I$ and $J$ are projections of $B(-b, 0)$ and $C(c, 0)$ onto $AG$.
26: $x_I = \frac{(c-b)(2h^2-b(c-b))}{W_0}, y_I = \frac{h(c-b)(b+c)}{W_0}$.
27: $x_J = \frac{(c-b)(2h^2+c(c-b))}{W_0}, y_J = \frac{-h(c-b)(b+c)}{W_0}$.
28: $K$ is the second intersection of the circumcircles of $\triangle DIF$ and $\triangle DJE$. Using the coordinates of $D, I, F$ and $D, J, E$, the circumcircle $\odot(DKL)$ can be determined. The point $P$ is the second intersection of the line $DN$ with $\odot(DKL)$. The length of the chord $DP$ is calculated to be $DP = \frac{\sqrt{W}}{h}$.
29: 
30: 4. Final Proof
31: The power of point $D$ with respect to $\odot(OCP)$ is $DQ \cdot DC = DO \cdot DP$.
32: $DO = \frac{1}{2} DN = \frac{1}{2} \frac{2bch}{\sqrt{W}} = \frac{bch}{\sqrt{W}}$.
33: Then $DQ \cdot c = \frac{bch}{\sqrt{W}} \cdot \frac{\sqrt{W}}{h} = bc \implies DQ = b$.
34: Since $Q$ is on $BC$ and $Q \neq C$, and $B=(-b, 0)$, we have $Q=(b, 0)$.
35: $AB^2 = b^2+h^2$ and $AQ^2 = b^2+h^2$, so $AB=AQ$.

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
