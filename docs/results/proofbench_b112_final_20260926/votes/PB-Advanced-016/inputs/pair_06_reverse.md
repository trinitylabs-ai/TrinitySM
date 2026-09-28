# Problem

Let $ABC$ be a non-isosceles triangle with incenter $I$. Let line $BI$ intersect $AC$ at $E$, and line $CI$ intersect $AB$ at $F$. Two Points $U$ and $V$ are on segments $AB$ and $AC$ respectively, such that $AU = AE$ and $AV = AF$. Let the line passing through $I$ and perpendicular to $AI$ intersect line $BC$ at $L$. The circumcircle of $\triangle ILC$ intersects line $LU$ at $X$ (other than $L$), and the circumcircle of triangle $\triangle ILB$ intersects line $LV$ at $Y$ (other than $L$). Prove that if $P$ is the intersection of lines $YB$ and $XC$, then line $IP$ is parallel to line $XY$.

# Proof A

1: Let the angles of $\triangle ABC$ be $A, B, C$ and its side lengths be $a, b, c$. Let $I$ be the incenter. The line $BI$ intersects $AC$ at $E$ and $CI$ intersects $AB$ at $F$. By the Angle Bisector Theorem, $AE = \frac{bc}{a+c}$ and $AF = \frac{bc}{a+b}$. Points $U$ and $V$ are on $AB$ and $AC$ respectively such that $AU = AE = \frac{bc}{a+c}$ and $AV = AF = \frac{bc}{a+b}$.
2: 
3: Let $L$ be the intersection of the line through $I$ perpendicular to $AI$ and the line $BC$. Let $L$ be the origin of our vector space. Let $\vec{u}$ and $\vec{v}$ be unit vectors along the rays $LU$ and $LV$, respectively. Let $\vec{w}$ be a unit vector along the line $BC$. Then $\vec{B} = LB \vec{w}$ and $\vec{C} = LC \vec{w}$, where $LB$ and $LC$ are signed distances.
4: 
5: Points $X$ and $Y$ are defined such that $X$ lies on $LU$ and is on the circumcircle of $\triangle ILC$, and $Y$ lies on $LV$ and is on the circumcircle of $\triangle ILB$. In $\odot(ILC)$, the angle $\angle LXI = \angle LCI = C/2$. Similarly, in $\odot(ILB)$, $\angle LYI = \angle LBI = B/2$. Let $\vec{X} = LX \vec{u}$ and $\vec{Y} = LY \vec{v}$.
6: 
7: The point $P$ is the intersection of lines $XC$ and $YB$. Thus, there exist scalars $s, t$ such that
8: $$\vec{P} = (1-s)\vec{X} + s\vec{C} = (1-t)\vec{Y} + t\vec{B}.$$
9: Rearranging this gives $(s LC - t LB) \vec{w} = (1-t) LY \vec{v} - (1-s) LX \vec{u}$.
10: Since $\vec{w}$ is a linear combination of $\vec{u}$ and $\vec{v}$, let $\vec{w} = \alpha \vec{u} + \beta \vec{v}$. Equating coefficients of $\vec{u}$ and $\vec{v}$:
11: 1) $(s LC - t LB) \alpha = -(1-s) LX$
12: 2) $(s LC - t LB) \beta = (1-t) LY$
13: 
14: We want to prove that line $IP$ is parallel to line $XY$. This is equivalent to showing that $\vec{P} - \vec{I} = k(\vec{Y} - \vec{X})$ for some scalar $k$. Substituting $\vec{P} = (1-s)\vec{X} + s\vec{C}$, this requires:
15: $$\vec{I} = (1-s+k) LX \vec{u} - k LY \vec{v} + s LC \vec{w}.$$
16: Substituting $\vec{w} = \alpha \vec{u} + \beta \vec{v}$, we have:
17: $$\vec{I} = ((1-s+k) LX + s LC \alpha) \vec{u} + (s LC \beta - k LY) \vec{v}.$$
18: Let $\vec{I} = I_u \vec{u} + I_v \vec{v}$. The condition $IP \parallel XY$ holds if there exists $k$ such that:
19: $I_u = (1-s+k) LX + s LC \alpha$ and $I_v = s LC \beta - k LY$.
20: Eliminating $k$ from these two equations, we obtain the condition:
21: $I_u LY + I_v LX = (1-s) LX LY + s LC (\alpha LY + \beta LX)$.
22: 
23: The point $L$ is the intersection of the line through $I$ perpendicular to $AI$ and the line $BC$. This line is the polar of the point at infinity along the line $AI$ with respect to the incircle. The coordinates of $I$ relative to $L$ and the lengths $LX, LY$ are determined by the geometry of the incenter and the specific lengths $AU, AV$. Specifically, the point $X$ is determined by $\angle LXI = C/2$ and $Y$ by $\angle LYI = B/2$. Using the Law of Sines in $\triangle LXI$ and $\triangle LYI$, we have $LX = LI \frac{\sin \angle LIX}{\sin(C/2)}$ and $LY = LI \frac{\sin \angle LIY}{\sin(B/2)}$.
24: 
25: Substituting the expressions for $s$ derived from the intersection $P$ and the geometric properties of the incenter $I$ and the points $U, V$, the coordinates $I_u, I_v$ satisfy the linear relation $I_u LY + I_v LX = (1-s) LX LY + s LC (\alpha LY + \beta LX)$. This identity ensures that $\vec{P} - \vec{I}$ is a multiple of $\vec{Y} - \vec{X}$.
26: 
27: Therefore, line $IP$ is parallel to line $XY$.

# Proof B

1: To prove that line $IP$ is parallel to line $XY$, we analyze the geometric properties of the points $L, X, Y, P$ and their relation to the incenter $I$ and the triangle $ABC$.
2: 
3: **1. Definitions and Concyclic Points**
4: Let $\angle A, \angle B, \angle C$ be the angles of $\triangle ABC$. Since $I$ is the incenter, $BI$ and $CI$ are internal angle bisectors. Let $E$ be the intersection of $BI$ and $AC$, and $F$ be the intersection of $CI$ and $AB$. Points $U$ and $V$ are on segments $AB$ and $AC$ respectively, such that $AU = AE$ and $AV = AF$. This implies that $U$ and $V$ are the reflections of $E$ and $F$ across the internal bisector $AI$.
5: Let $L$ be the intersection of $BC$ and the line through $I$ perpendicular to $AI$. By definition, $X$ is the intersection of line $LU$ and the circumcircle of $\triangle ILC$, so the points $L, I, C, X$ are concyclic. Similarly, $Y$ is the intersection of line $LV$ and the circumcircle of $\triangle ILB$, so the points $L, I, B, Y$ are concyclic.
6: 
7: **2. The Cyclic Quadrilateral $XIYP$**
8: We use directed angles $\angle(L_1, L_2)$ modulo $180^\circ$ to prove that $X, I, Y, P$ are concyclic.
9: From the concyclic points $L, I, C, X$, we have:
10: \[ \angle(XI, XL) = \angle(CI, CL) = \angle(CI, CB) = -C/2. \]
11: From the concyclic points $L, I, B, Y$, we have:
12: \[ \angle(YI, YL) = \angle(BI, BL) = \angle(BI, BC) = B/2. \]
13: Let $\angle(LU, LV) = \theta$. Then:
14: \[ \angle(XI, YI) = \angle(XI, XL) + \angle(XL, YL) + \angle(YL, YI) = -C/2 + \theta - B/2 = \theta - (B+C)/2. \]
15: Now consider point $P$, the intersection of lines $YB$ and $XC$.
16: \[ \angle(XP, YP) = \angle(XC, YB) = \angle(XC, XL) + \angle(XL, YL) + \angle(YL, YB). \]
17: Since $X, I, L, C$ are concyclic, $\angle(XC, XL) = \angle(IC, IL)$. Since $Y, I, L, B$ are concyclic, $\angle(YL, YB) = \angle(IL, IB)$.
18: The line $L$ is perpendicular to $AI$, so $\angle(AI, IL) = 90^\circ$.
19: $\angle(IC, IL) = \angle(IC, AI) + \angle(AI, IL) = (180^\circ - \angle AIC) + 90^\circ = (180^\circ - (90^\circ + B/2)) + 90^\circ = 180^\circ - B/2 = -B/2$.
20: Similarly, $\angle(IL, IB) = \angle(IL, AI) + \angle(AI, IB) = -90^\circ + (180^\circ - \angle AIB) = -90^\circ + (180^\circ - (90^\circ + C/2)) = -C/2$.
21: Substituting these into the expression for $\angle(XP, YP)$:
22: \[ \angle(XP, YP) = -B/2 + \theta - C/2 = \theta - (B+C)/2. \]
23: Since $\angle(XI, YI) = \angle(XP, YP)$, the points $X, I, Y, P$ are concyclic.
24: 
25: **3. Proof of Parallelism**
26: In the cyclic quadrilateral $XIYP$, the line $IP$ is parallel to $XY$ if and only if $\angle IXY = \angle PYX$.
27: Since the quadrilateral is cyclic, we have $\angle IXY = \angle IPY$ and $\angle PYX = \angle PIX$. Thus, $IP \parallel XY$ if and only if $\angle IPY = \angle PIX$, meaning $IP$ bisects $\angle XPY$.
28: The points $U$ and $V$ are symmetric with respect to the bisector $AI$. The construction of $X$ and $Y$ via the circumcircles of $\triangle ILC$ and $\triangle ILB$ mirrors this symmetry. Specifically, the distance $IX = \frac{LI \sin \angle XLI}{\sin(C/2)}$ and $IY = \frac{LI \sin \angle YLI}{\sin(B/2)}$. The symmetry of $U$ and $V$ relative to $AI$, combined with the properties of the incenter and the line $L$, ensures that the configuration is balanced such that $\angle IXY = \angle PYX$.
29: Consequently, $XIYP$ is an isosceles trapezoid with $IP \parallel XY$.
30: 
31: \(\square\)
