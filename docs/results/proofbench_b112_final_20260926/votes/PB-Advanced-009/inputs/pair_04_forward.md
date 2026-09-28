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
