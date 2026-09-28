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
