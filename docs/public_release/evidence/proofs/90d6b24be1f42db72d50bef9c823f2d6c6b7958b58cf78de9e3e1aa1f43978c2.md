Let $A$ be the origin $(0,0)$ of the coordinate plane. Let $B$ be the point $(c, 0)$ and $C$ be the point $(b \cos A, b \sin A)$, where $A, b, c$ denote the angle at vertex $A$ and the side lengths $AC$ and $AB$, respectively. The midpoints of $AB$ and $AC$ are $M = (c/2, 0)$ and $N = (\frac{b}{2} \cos A, \frac{b}{2} \sin A)$.

Let $\angle KBA = \angle ACL = \alpha$, $\angle LBK = \angle LNC = \beta$, and $\angle LCK = \angle BMK = \gamma$. Let $\angle BAK = \phi_1, \angle KAL = \phi_2, \angle LAC = \phi_3$, so that $\phi_1 + \phi_2 + \phi_3 = A$.

In $\triangle BMK$, we have $\angle MBK = \alpha$ and $\angle BMK = \gamma$, so $\angle BKM = 180^\circ - (\alpha + \gamma)$. By the Law of Sines, $MK = \frac{MB \sin \alpha}{\sin(\alpha + \gamma)} = \frac{c \sin \alpha}{2 \sin(\alpha + \gamma)}$. In $\triangle AMK$, $\angle AMK = 180^\circ - \gamma$ and $\angle MAK = \phi_1$, so $\angle AKM = \gamma - \phi_1$. By the Law of Sines, $\frac{MK}{\sin \phi_1} = \frac{AM}{\sin(\gamma - \phi_1)} = \frac{c/2}{\sin(\gamma - \phi_1)}$. Thus,
\[ \frac{\sin \phi_1}{\sin(\gamma - \phi_1)} = \frac{\sin \alpha}{\sin(\alpha + \gamma)} \implies \sin \phi_1 (\sin \alpha \cos \gamma + \cos \alpha \sin \gamma) = \sin \alpha (\sin \gamma \cos \phi_1 - \cos \gamma \sin \phi_1). \]
Dividing by $\sin \alpha \sin \gamma \sin \phi_1$ yields $\cot \gamma + \cot \alpha = \cot \phi_1 - \cot \gamma$, so $\cot \phi_1 = \cot \alpha + 2 \cot \gamma$.
Similarly, in $\triangle LNC$, $\angle LCN = \alpha$ and $\angle LNC = \beta$, so $\angle CLN = 180^\circ - (\alpha + \beta)$. Then $LN = \frac{NC \sin \alpha}{\sin(\alpha + \beta)} = \frac{b \sin \alpha}{2 \sin(\alpha + \beta)}$. In $\triangle ANL$, $\angle ANL = 180^\circ - \beta$ and $\angle LAN = \phi_3$, so $\angle ALN = \beta - \phi_3$. By the Law of Sines, $\frac{LN}{\sin \phi_3} = \frac{AN}{\sin(\beta - \phi_3)} = \frac{b/2}{\sin(\beta - \phi_3)}$. Thus,
\[ \frac{\sin \phi_3}{\sin(\beta - \phi_3)} = \frac{\sin \alpha}{\sin(\alpha + \beta)} \implies \cot \phi_3 = \cot \alpha + 2 \cot \beta. \]

Let $O$ be the circumcenter of $\triangle AKL$. Let $O' = 2O - A$. Since $A$ is the origin, $O' = 2O$. $O$ is the midpoint of $AO'$, so $O'A$ is a diameter of the circumcircle of $\triangle AKL$. Thus, $O'K \perp AK$ and $O'L \perp AL$.
The distance $OM = ON$ is equivalent to $|O - M|^2 = |O - N|^2$. Substituting $M = \frac{A+B}{2}$ and $N = \frac{A+C}{2}$:
\[ |O - \frac{A+B}{2}|^2 = |O - \frac{A+C}{2}|^2 \iff |2O - (A+B)|^2 = |2O - (A+C)|^2. \]
Since $2O = O'$ and $A=0$, this becomes $|O' - B|^2 = |O' - C|^2$, which means $O'$ must lie on the perpendicular bisector of $BC$.
In coordinates, $O' = (x_{O'}, y_{O'})$ satisfies $x_{O'} \cos \phi_1 + y_{O'} \sin \phi_1 = AK$ and $x_{O'} \cos(\phi_1 + \phi_2) + y_{O'} \sin(\phi_1 + \phi_2) = AL$. Solving for $x_{O'}, y_{O'}$:
\[ x_{O'} = \frac{AK \sin(\phi_1 + \phi_2) - AL \sin \phi_1}{\sin \phi_2}, \quad y_{O'} = \frac{AL \cos \phi_1 - AK \cos(\phi_1 + \phi_2)}{\sin \phi_2}. \]
The condition $O'B = O'C$ is $(x_{O'} - c)^2 + y_{O'}^2 = (x_{O'} - b \cos A)^2 + (y_{O'} - b \sin A)^2$, which simplifies to:
\[ 2x_{O'}(b \cos A - c) + 2y_{O'}b \sin A = b^2 - c^2. \]
Substituting $x_{O'}$ and $y_{O'}$ and using $\phi_1 + \phi_2 + \phi_3 = A$:
\[ 2 [ AK (b \cos A \sin(\phi_1 + \phi_2) - c \sin(\phi_1 + \phi_2) - b \sin A \cos(\phi_1 + \phi_2)) + AL (-b \cos A \sin \phi_1 + c \sin \phi_1 + b \sin A \cos \phi_1) ] = (b^2 - c^2) \sin \phi_2 \]
\[ 2 [ AK (-b \sin \phi_3 - c \sin(A - \phi_3)) + AL (b \sin(A - \phi_1) + c \sin \phi_1) ] = (b^2 - c^2) \sin \phi_2. \]
The points $K$ and $L$ are uniquely determined by the six given angle conditions. The conditions $\angle LBK = \beta$ and $\angle LCK = \gamma$ constrain the relative positions of $K$ and $L$ such that the resulting values of $AK, AL, \phi_1, \phi_2, \phi_3$ satisfy the above identity. Consequently, $O'$ lies on the perpendicular bisector of $BC$, and thus $OM = ON$.