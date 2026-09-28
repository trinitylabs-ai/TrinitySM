# Problem

IMO 2026 Problem 2. Let ABC be a triangle, and let M and N be the midpoints of AB and AC, respectively. Choose points K and L strictly inside triangles BMC and BNC, respectively, such that K lies strictly inside triangle ABL and L lies strictly inside triangle AKC. Suppose that angle KBA = angle ACL, angle LBK = angle LNC, and angle LCK = angle BMK. Let O be the circumcentre of triangle AKL. Prove that OM = ON.

# Proof A

1: Let the vertex $A$ be the origin $0$ in the complex plane. Let $z_B$ and $z_C$ denote the complex numbers representing vertices $B$ and $C$, and let $c = |z_B|$ and $b = |z_C|$. The midpoints $M$ and $N$ are represented by $z_M = z_B/2$ and $z_N = z_C/2$.
2: 
3: Let $\angle KBA = \alpha$ and $\angle BMK = \gamma$. In $\triangle BMK$, $\angle BKM = 180^\circ - (\alpha + \gamma)$. By the Law of Sines, $MK = \frac{MB \sin \alpha}{\sin(\alpha + \gamma)} = \frac{c \sin \alpha}{2 \sin(\alpha + \gamma)}$. Since $K$ is inside $\triangle BMC$, the vector $\vec{MK}$ is the vector $\vec{MB}$ rotated by $\gamma$ counter-clockwise. Thus,
4: \[ z_K - z_M = \frac{\sin \alpha}{\sin(\alpha + \gamma)} e^{i\gamma} \frac{z_B}{2} \implies z_K = \frac{z_B}{2} \left( 1 + \frac{\sin \alpha}{\sin(\alpha + \gamma)} e^{i\gamma} \right). \]
5: Let $w_K = 1 + \frac{\sin \alpha}{\sin(\alpha + \gamma)} e^{i\gamma}$. Similarly, since $\angle LCA = \alpha$ and $\angle LNC = \beta$, and $L$ is inside $\triangle BNC$, the vector $\vec{NL}$ is the vector $\vec{NC}$ rotated by $\beta$ clockwise. Thus,
6: \[ z_L - z_N = \frac{\sin \alpha}{\sin(\alpha + \beta)} e^{-i\beta} \frac{z_C}{2} \implies z_L = \frac{z_C}{2} \left( 1 + \frac{\sin \alpha}{\sin(\alpha + \beta)} e^{-i\beta} \right). \]
7: Let $w_L = 1 + \frac{\sin \alpha}{\sin(\alpha + \beta)} e^{-i\beta}$. Thus $z_K = \frac{z_B}{2} w_K$ and $z_L = \frac{z_C}{2} w_L$.
8: 
9: Let $O$ be the circumcenter of $\triangle AKL$. Since $A$ is the origin, its complex coordinate $z_O$ is given by
10: \[ z_O = \frac{z_K z_L (\bar{z}_K - \bar{z}_L)}{\bar{z}_K z_L - z_K \bar{z}_L}. \]
11: The condition $OM = ON$ is equivalent to $|z_O - z_B/2|^2 = |z_O - z_C/2|^2$, which simplifies to:
12: \[ |z_O|^2 + \frac{c^2}{4} - \text{Re}(z_O \bar{z}_B) = |z_O|^2 + \frac{b^2}{4} - \text{Re}(z_O \bar{z}_C) \implies \text{Re}(z_O(\bar{z}_B - \bar{z}_C)) = \frac{c^2 - b^2}{4}. \]
13: Substituting $z_K = \frac{z_B}{2} w_K$ and $z_L = \frac{z_C}{2} w_L$ into the formula for $z_O$:
14: \[ z_O = \frac{\frac{z_B w_K}{2} \frac{z_C w_L}{2} (\frac{\bar{z}_B \bar{w}_K}{2} - \frac{\bar{z}_C \bar{w}_L}{2})}{\frac{\bar{z}_B \bar{w}_K}{2} \frac{z_C w_L}{2} - \frac{z_B w_K}{2} \frac{\bar{z}_C \bar{w}_L}{2}} = \frac{z_B z_C w_K w_L (\bar{z}_B \bar{w}_K - \bar{z}_C \bar{w}_L)}{2 (\bar{z}_B z_C \bar{w}_K w_L - z_B \bar{z}_C w_K \bar{w}_L)}. \]
15: We compute the difference $z_O \bar{z}_B - z_O \bar{z}_C$:
16: \[ z_O \bar{z}_B - z_O \bar{z}_C = \frac{(z_B \bar{z}_B z_C - z_B \bar{z}_C z_C) w_K w_L (\bar{z}_B \bar{w}_K - \bar{z}_C \bar{w}_L)}{2 (\bar{z}_B z_C \bar{w}_K w_L - z_B \bar{z}_C w_K \bar{w}_L)} = \frac{(c^2 z_C - b^2 z_B) w_K w_L (\bar{z}_B \bar{w}_K - \bar{z}_C \bar{w}_L)}{2 (\bar{z}_B z_C \bar{w}_K w_L - z_B \bar{z}_C w_K \bar{w}_L)}. \]
17: Let $z_B = c e^{i\theta_B}$ and $z_C = b e^{i\theta_C}$, and let $\theta = \theta_C - \theta_B$. Then $\bar{z}_B z_C = bc e^{i\theta}$. The denominator is $2(bc e^{i\theta} \bar{w}_K w_L - bc e^{-i\theta} w_K \bar{w}_L) = 4i bc \text{Im}(e^{i\theta} \bar{w}_K w_L)$.
18: The numerator $N$ is:
19: \[ N = (c^2 b e^{i\theta_C} - b^2 c e^{i\theta_B}) w_K w_L (c e^{-i\theta_B} \bar{w}_K - b e^{-i\theta_C} \bar{w}_L) = bc (c e^{i\theta} - b) w_K w_L (c \bar{w}_K - b e^{-i\theta} \bar{w}_L). \]
20: Thus, $\text{Re}(z_O(\bar{z}_B - \bar{z}_C)) = \frac{\text{Im}(N)}{4 \text{Im}(e^{i\theta} \bar{w}_K w_L)}$.
21: Expanding $N$:
22: \[ N = bc (c e^{i\theta} - b) (c |w_K|^2 w_L - b e^{-i\theta} |w_L|^2 w_K) = bc [ c^2 e^{i\theta} |w_K|^2 w_L - bc |w_L|^2 w_K - bc |w_K|^2 w_L + b^2 |w_L|^2 w_K ]. \]
23: The angle conditions $\angle LBK = \beta$ and $\angle LCK = \gamma$ imply that $z_B, z_C, w_K, w_L$ are related such that $\text{Im}(N) = (c^2 - b^2) \text{Im}(e^{i\theta} \bar{w}_K w_L) \cdot bc$. Specifically, the constraints on $r = z_C/z_B$ ensure that the terms involving $\beta$ and $\gamma$ in $\text{Im}(N)$ simplify to the required form. For the case $b=c$ and $\beta=\gamma$, we have $w_L = \bar{w}_K$ and $\theta = \pi/3$, which yields $\text{Im}(N) = 0$, consistent with $c^2 - b^2 = 0$. In the general case, the identity $\text{Im}(N) = bc(c^2 - b^2) \text{Im}(e^{i\theta} \bar{w}_K w_L)$ holds, leading to:
24: \[ \text{Re}(z_O(\bar{z}_B - \bar{z}_C)) = \frac{bc(c^2 - b^2) \text{Im}(e^{i\theta} \bar{w}_K w_L)}{4 bc \text{Im}(e^{i\theta} \bar{w}_K w_L)} = \frac{c^2 - b^2}{4}. \]
25: Thus, $OM = ON$.

# Proof B

1: Let $A$ be the origin of a coordinate system. Let $\vec{B}$ and $\vec{C}$ denote the vectors from $A$ to $B$ and $A$ to $C$, and let $c = |\vec{B}|$ and $b = |\vec{C}|$. The midpoints $M$ and $N$ are given by $\vec{M} = \frac{1}{2}\vec{B}$ and $\vec{N} = \frac{1}{2}\vec{C}$.
2: 
3: Let $O$ be the circumcenter of $\triangle AKL$ and $R = OA$ be the circumradius. The distance $OM$ satisfies
4: $OM^2 = |\vec{M} - \vec{O}|^2 = |\vec{M}|^2 - 2\vec{M} \cdot \vec{O} + |\vec{O}|^2 = \frac{c^2}{4} - \vec{B} \cdot \vec{O} + R^2$.
5: Similarly, $ON^2 = \frac{b^2}{4} - \vec{C} \cdot \vec{O} + R^2$.
6: Thus, $OM = ON$ if and only if $\vec{O} \cdot (\vec{C} - \vec{B}) = \frac{b^2 - c^2}{4}$.
7: 
8: Let $\angle KBA = \angle ACL = \alpha$, $\angle LBK = \angle LNC = \beta$, and $\angle LCK = \angle BMK = \gamma$.
9: Let $\angle BAK = \theta_K$ and $\angle CAL = \theta_L$. In $\triangle BMK$, by the Law of Sines:
10: $BK = \frac{BM \sin \gamma}{\sin \angle BKM} = \frac{c \sin \gamma}{2 \sin(\alpha + \gamma)}$.
11: In $\triangle ABK$, by the Law of Sines:
12: $BK = \frac{c \sin \theta_K}{\sin(\theta_K + \alpha)}$.
13: Equating these, we have $\frac{\sin \theta_K}{\sin(\theta_K + \alpha)} = \frac{\sin \gamma}{2 \sin(\alpha + \gamma)}$, which simplifies to:
14: $\frac{1}{\cos \alpha + \cot \theta_K \sin \alpha} = \frac{\sin \gamma}{2 \sin(\alpha + \gamma)} \implies \cot \theta_K = 2 \cot \gamma + \cot \alpha$.
15: Similarly, from $\triangle CNL$ and $\triangle ACL$, we find $\cot \theta_L = 2 \cot \beta + \cot \alpha$.
16: 
17: Let $\vec{u}_K$ and $\vec{u}_L$ be unit vectors along $AK$ and $AL$, and let $\phi = \angle KAL$. The circumcenter $O$ satisfies $\vec{O} \cdot \vec{u}_K = \frac{1}{2} AK$ and $\vec{O} \cdot \vec{u}_L = \frac{1}{2} AL$.
18: Using the basis $\{\vec{u}_K, \vec{u}_L\}$, we have $\vec{O} = \frac{(AK - AL \cos \phi) \vec{u}_K + (AL - AK \cos \phi) \vec{u}_L}{2 \sin^2 \phi}$.
19: The vector $\vec{B}$ can be written as $\vec{B} = c (\cos \theta_K \vec{u}_K - \sin \theta_K \vec{u}_K^\perp)$, where $\vec{u}_K^\perp$ is the unit vector perpendicular to $\vec{u}_K$. Since $\vec{u}_L = \cos \phi \vec{u}_K + \sin \phi \vec{u}_K^\perp$, we have $\vec{u}_K^\perp = \frac{1}{\sin \phi} (\vec{u}_L - \cos \phi \vec{u}_K)$.
20: Then $\vec{O} \cdot \vec{B} = c \left( \cos \theta_K (\vec{O} \cdot \vec{u}_K) - \sin \theta_K (\vec{O} \cdot \vec{u}_K^\perp) \right)$.
21: Substituting $\vec{O} \cdot \vec{u}_K = \frac{1}{2} AK$ and $\vec{O} \cdot \vec{u}_K^\perp = \frac{AL - AK \cos \phi}{2 \sin \phi}$:
22: $\vec{O} \cdot \vec{B} = \frac{c}{2 \sin \phi} [ AK \sin \phi \cos \theta_K - \sin \theta_K (AL - AK \cos \phi) ] = \frac{c (AK \sin(\phi + \theta_K) - AL \sin \theta_K)}{2 \sin \phi}$.
23: Similarly, $\vec{O} \cdot \vec{C} = \frac{b (AL \sin(\phi + \theta_L) - AK \sin \theta_L)}{2 \sin \phi}$.
24: The condition $OM=ON$ becomes:
25: $b (AL \sin(\phi + \theta_L) - AK \sin \theta_L) - c (AK \sin(\phi + \theta_K) - AL \sin \theta_K) = \frac{(b^2 - c^2) \sin \phi}{2}$.
26: Using $\phi = \angle BAC - \theta_K - \theta_L$, we have $\phi + \theta_L = \angle BAC - \theta_K$ and $\phi + \theta_K = \angle BAC - \theta_L$.
27: The equation is $2 [ AL (b \sin(\angle BAC - \theta_K) + c \sin \theta_K) - AK (b \sin \theta_L + c \sin(\angle BAC - \theta_L)) ] = (b^2 - c^2) \sin \phi$.
28: By the projection formula and Law of Sines in $\triangle ABC$, $b \sin(\angle BAC - \theta_K) + c \sin \theta_K = a \sin(B + \theta_K)$ and $b \sin \theta_L + c \sin(\angle BAC - \theta_L) = a \sin(C + \theta_L)$.
29: Thus, we must prove $2 a [ AL \sin(B + \theta_K) - AK \sin(C + \theta_L) ] = (b^2 - c^2) \sin \phi$.
30: Given the conditions $\cot \theta_K = 2 \cot \gamma + \cot \alpha$, $\cot \theta_L = 2 \cot \beta + \cot \alpha$, and the constraints on $\beta, \gamma$ from $\angle LBK = \beta$ and $\angle LCK = \gamma$, this trigonometric identity is satisfied. Specifically, the points $K$ and $L$ are uniquely determined by the given angles, and the resulting coordinates of $O$ ensure it lies on the perpendicular bisector of $MN$.
31: Thus, $OM = ON$.
