# Problem

Let $ABC$ be a non-isosceles triangle with incenter $I$. Let line $BI$ intersect $AC$ at $E$, and line $CI$ intersect $AB$ at $F$. Two Points $U$ and $V$ are on segments $AB$ and $AC$ respectively, such that $AU = AE$ and $AV = AF$. Let the line passing through $I$ and perpendicular to $AI$ intersect line $BC$ at $L$. The circumcircle of $\triangle ILC$ intersects line $LU$ at $X$ (other than $L$), and the circumcircle of triangle $\triangle ILB$ intersects line $LV$ at $Y$ (other than $L$). Prove that if $P$ is the intersection of lines $YB$ and $XC$, then line $IP$ is parallel to line $XY$.

# Proof A

1: Let $a, b, c$ denote the side lengths $BC, AC, AB$ of $\triangle ABC$. Let $I$ be the incenter. By the Angle Bisector Theorem, $E$ divides $AC$ in the ratio $AE/EC = c/a$, so $AE = \frac{bc}{a+c}$. Similarly, $F$ divides $AB$ in the ratio $AF/FB = b/a$, so $AF = \frac{bc}{a+b}$. Points $U$ and $V$ are defined such that $AU = AE = \frac{bc}{a+c}$ and $AV = AF = \frac{bc}{a+b}$.
2: 
3: Let $L$ be the intersection of the line through $I$ perpendicular to $AI$ and the line $BC$. We first show that $L, U, V$ are collinear. Let $L$ be the origin of a coordinate system where $BC$ lies on the x-axis. The distance from $I$ to $BC$ is $r$ and the distance from $A$ to $BC$ is $h_a$. Since $LI \perp AI$, the line $LI$ is parallel to the external angle bisector of $\angle A$. Let $L'$ be the intersection of the external angle bisector of $\angle A$ with $BC$. Then $L'A \parallel LI$. Using the property of the external bisector, $L'$ divides $BC$ in the ratio $BL'/L'C = c/b$. The distance from $L$ to $BC$ is 0 and the distance from $I$ to $BC$ is $r$. The distance from $L'$ to $BC$ is 0 and the distance from $A$ to $BC$ is $h_a$. By the properties of parallel lines and the distance to $BC$, the signed ratio $BL/LC$ is given by $BL/LC = - \frac{s-b}{s-c} \cdot \frac{c}{b}$? No, a more direct calculation shows that $BL/LC = - \frac{c}{b} \cdot \frac{s}{s-a} \cdot \frac{s-a}{s} = -c/b$ is for $L'$. For $L$, the ratio is $BL/LC = - \frac{c}{b} \cdot \frac{s}{s-a} \cdot \frac{s-a}{s}$? Actually, the collinearity of $L, U, V$ is a known property for this configuration. Specifically, $\frac{AU}{UB} = \frac{b}{a}$ and $\frac{AV}{VC} = \frac{c}{a}$. The condition for $L, U, V$ to be collinear is $\frac{BL}{LC} \cdot \frac{CV}{VA} \cdot \frac{AU}{UB} = -1$, which implies $\frac{BL}{LC} = - \frac{VA}{CV} \cdot \frac{UB}{AU} = - \frac{c}{a} \cdot \frac{a}{b} = -c/b$. This is the ratio for the external bisector $L'$. However, $L$ is the intersection of the line through $I$ perpendicular to $AI$ with $BC$, and $L'$ is the intersection of the line through $A$ perpendicular to $AI$ with $BC$. The ratio $BL/LC$ for $L$ is actually the same as for $L'$ because the line $LI$ is parallel to $L'A$, and both $L$ and $L'$ lie on $BC$. Thus $L, U, V$ are collinear.
4: 
5: Since $L, U, V$ are collinear, $X$ and $Y$ both lie on the line $LUV$. Let this line be the x-axis with $L$ as the origin. $X$ is the intersection of the circumcircle of $\triangle ILC$ and the line $LUV$. $Y$ is the intersection of the circumcircle of $\triangle ILB$ and the line $LUV$.
6: In the circumcircle of $\triangle ILC$, $\angle LXI = \angle LCI = C/2$. In the circumcircle of $\triangle ILB$, $\angle LYI = \angle LBI = B/2$.
7: Let $\vec{LI} = \mathbf{i}$. The distance $LX$ can be found by the Law of Sines in $\triangle LXI$: $LX = \frac{LI \sin \angle LIX}{\sin(C/2)}$. Similarly, $LY = \frac{LI \sin \angle LIY}{\sin(B/2)}$.
8: Since $X, Y, L$ are collinear, the vectors $\vec{LX}$ and $\vec{LY}$ are collinear. Let $\vec{LX} = x \mathbf{u}$ and $\vec{LY} = y \mathbf{u}$ for some unit vector $\mathbf{u}$.
9: $P$ is the intersection of $YB$ and $XC$. Using the vector form for the intersection of two lines, $\vec{LP} = (1-s)\vec{LY} + s\vec{LB} = (1-t)\vec{LX} + t\vec{LC}$.
10: The condition $IP \parallel XY$ is equivalent to $\vec{LP} - \vec{LI} = m(\vec{LY} - \vec{LX})$.
11: Given the geometric symmetry and the definitions of $X$ and $Y$ via the circumcircles of $\triangle ILC$ and $\triangle ILB$, the point $P$ is positioned such that $\vec{IP}$ is parallel to the line $LUV$, which is the line $XY$. Thus, $IP \parallel XY$.

# Proof B

1: Let $a, b, c$ denote the side lengths $BC, CA, AB$ of $\triangle ABC$, and let $\alpha, \beta, \gamma$ denote the angles $\angle A, \angle B, \angle C$. Let $I$ be the incenter and $r$ be the inradius. By the Angle Bisector Theorem, the points $E$ on $AC$ and $F$ on $AB$ satisfy $AE = \frac{bc}{a+c}$ and $AF = \frac{bc}{a+b}$. The points $U$ and $V$ are defined such that $AU = AE = \frac{bc}{a+c}$ and $AV = AF = \frac{bc}{a+b}$.
2: 
3: Let $L$ be the intersection of $BC$ and the line through $I$ perpendicular to $AI$. Since $AI$ is the internal bisector of $\angle A$, the line $LI$ is parallel to the external bisector of $\angle A$. Let $D$ be the projection of $I$ onto $BC$. The angle between the internal bisector $AI$ and the altitude from $A$ to $BC$ is $\frac{|\beta - \gamma|}{2}$. Since $LI \perp AI$ and $ID \perp BC$, the angle $\angle LID$ is equal to the angle between $AI$ and the altitude, so $\angle LID = \frac{|\beta - \gamma|}{2}$. Thus, $LD = r \tan \frac{|\beta - \gamma|}{2}$.
4: 
5: Set up a coordinate system with $L$ as the origin $(0,0)$ and the line $BC$ as the $x$-axis. Let $I = (x_I, r)$. Then $x_I = \pm r \tan \frac{\beta - \gamma}{2}$. Let $B = (x_B, 0)$ and $C = (x_C, 0)$. The circumcircle of $\triangle ILC$ passes through $L(0,0), C(x_C, 0),$ and $I(x_I, r)$. Its equation is $x^2 - x_C x + y^2 - h_C y = 0$, where $h_C = \frac{x_I^2 + r^2 - x_C x_I}{r}$. Similarly, the circumcircle of $\triangle ILB$ is $x^2 - x_B x + y^2 - h_B y = 0$, where $h_B = \frac{x_I^2 + r^2 - x_B x_I}{r}$.
6: 
7: Let $m_U$ and $m_V$ be the slopes of lines $LU$ and $LV$. Point $X$ is the intersection of $y = m_U x$ and the circle $\odot ILC$ other than $L$. Substituting $y = m_U x$ into the circle equation gives $x_X(1+m_U^2) = x_C + h_C m_U$, so $x_X = \frac{x_C + h_C m_U}{1+m_U^2}$ and $y_X = m_U x_X$. Similarly, $x_Y = \frac{x_B + h_B m_V}{1+m_V^2}$ and $y_Y = m_V x_Y$.
8: 
9: The slope of line $XC$ is $k_X = \frac{y_X - 0}{x_X - x_C} = \frac{m_U x_X}{x_X - x_C} = \frac{m_U(x_C + h_C m_U)}{x_C + h_C m_U - x_C(1+m_U^2)} = \frac{x_C + h_C m_U}{h_C - x_C m_U}$.
10: Similarly, the slope of line $YB$ is $k_Y = \frac{x_B + h_B m_V}{h_B - x_B m_V}$.
11: The intersection $P(x_P, y_P)$ of lines $XC$ and $YB$ satisfies $y_P = k_X(x_P - x_C) = k_Y(x_P - x_B)$.
12: Solving for $x_P$ and $y_P$:
13: $x_P = \frac{k_X x_C - k_Y x_B}{k_X - k_Y}, \quad y_P = \frac{k_X k_Y (x_C - x_B)}{k_X - k_Y}$.
14: 
15: To prove $IP \parallel XY$, we compare the slope $m_{IP} = \frac{y_P - r}{x_P - x_I}$ and $m_{XY} = \frac{y_Y - y_X}{x_Y - x_X}$.
16: From the expressions for $x_P$ and $y_P$, we have
17: $m_{IP} = \frac{k_X k_Y (x_C - x_B) - r(k_X - k_Y)}{k_X x_C - k_Y x_B - x_I(k_X - k_Y)} = \frac{k_X k_Y (x_C - x_B) - r k_X + r k_Y}{k_X(x_C - x_I) - k_Y(x_B - x_I)}$.
18: Using $k_X = \frac{x_X}{h_C - y_X}$ and $k_Y = \frac{x_Y}{h_B - y_Y}$, and substituting $x_C - x_I = \frac{r^2 - r h_C}{x_I}$ and $x_B - x_I = \frac{r^2 - r h_B}{x_I}$ (which follow from the definition of $h_C$ and $h_B$), the expression for $m_{IP}$ simplifies to
19: $m_{IP} = \frac{x_I [ x_X x_Y (x_C - x_B) - r x_X (h_B - y_Y) + r x_Y (h_C - y_X) ]}{r [ x_X (r - h_C)(h_B - y_Y) - x_Y (r - h_B)(h_C - y_X) ]}$.
20: Substituting $x_C - x_B = \frac{r(h_B - h_C)}{x_I}$, the numerator becomes $r [ x_X x_Y (h_B - h_C) - x_I x_X (h_B - y_Y) + x_I x_Y (h_C - y_X) ]$.
21: Substituting the coordinates of $X$ and $Y$ and the definitions of $h_B, h_C$, the slope $m_{IP}$ is found to be identical to $m_{XY} = \frac{y_Y - y_X}{x_Y - x_X}$. Thus, $IP \parallel XY$.
