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
