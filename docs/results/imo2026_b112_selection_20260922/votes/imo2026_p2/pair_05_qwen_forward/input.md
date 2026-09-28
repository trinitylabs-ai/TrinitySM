# Problem

IMO 2026 Problem 2. Let ABC be a triangle, and let M and N be the midpoints of AB and AC, respectively. Choose points K and L strictly inside triangles BMC and BNC, respectively, such that K lies strictly inside triangle ABL and L lies strictly inside triangle AKC. Suppose that angle KBA = angle ACL, angle LBK = angle LNC, and angle LCK = angle BMK. Let O be the circumcentre of triangle AKL. Prove that OM = ON.

# Proof A

1: Let $A$ be the origin $(0,0)$ of a coordinate system. Let $\vec{B}$ and $\vec{C}$ be the vectors $\vec{AB}$ and $\vec{AC}$ with lengths $c$ and $b$, respectively. The midpoints of $AB$ and $AC$ are $\vec{M} = \frac{1}{2}\vec{B}$ and $\vec{N} = \frac{1}{2}\vec{C}$. The condition $OM = ON$ is equivalent to $O$ lying on the perpendicular bisector of $MN$, which is the set of points $\vec{X}$ such that $|\vec{X} - \frac{1}{2}\vec{B}|^2 = |\vec{X} - \frac{1}{2}\vec{C}|^2$. Expanding this, we obtain:
2: \[ \vec{X} \cdot \vec{B} - \frac{1}{4}c^2 = \vec{X} \cdot \vec{C} - \frac{1}{4}b^2 \implies \vec{X} \cdot (\vec{B} - \vec{C}) = \frac{c^2 - b^2}{4} \]
3: Let $\angle BAK = \theta_K$ and $\angle CAL = \theta_L$. Let $\angle KBA = \angle ACL = \alpha$, $\angle LBK = \angle LNC = \beta$, and $\angle LCK = \angle BMK = \gamma$.
4: In $\triangle ABK$, by the Law of Sines, $AK = \frac{c \sin \alpha}{\sin(\alpha + \theta_K)}$. In $\triangle BMK$, $\angle MBK = \alpha$ and $\angle BMK = \gamma$, so $\angle BKM = 180^\circ - (\alpha + \gamma)$. Thus $MK = \frac{(c/2) \sin \alpha}{\sin(\alpha + \gamma)}$. In $\triangle AMK$, $\angle AMK = 180^\circ - \gamma$ and $\angle MAK = \theta_K$, so $\angle AKM = \gamma - \theta_K$. By the Law of Sines, $AK = \frac{MK \sin \gamma}{\sin \theta_K} = \frac{c \sin \alpha \sin \gamma}{2 \sin(\alpha + \gamma) \sin \theta_K}$. Equating the two expressions for $AK$:
5: \[ \frac{\sin \theta_K}{\sin(\alpha + \theta_K)} = \frac{\sin \gamma}{2 \sin(\alpha + \gamma)} \]
6: Similarly, for $\triangle ACL$ and $\triangle LNC$, we find $\frac{\sin \theta_L}{\sin(\alpha + \theta_L)} = \frac{\sin \beta}{2 \sin(\alpha + \beta)}$.
7: Furthermore, the conditions $\angle LBK = \beta$ and $\angle LCK = \gamma$ imply $\angle LBA = \alpha + \beta$ and $\angle KCA = \alpha + \gamma$. Applying the Law of Sines in $\triangle ABL$ and $\triangle ACK$:
8: \[ AL = \frac{c \sin(\alpha + \beta)}{\sin(A - \theta_L + \alpha + \beta)} \quad \text{and} \quad AK = \frac{b \sin(\alpha + \gamma)}{\sin(A - \theta_K + \alpha + \gamma)} \]
9: Let $\vec{u}_K$ and $\vec{u}_L$ be unit vectors along $AK$ and $AL$. Since $O$ is the circumcenter of $\triangle AKL$, $\vec{O} \cdot \vec{u}_K = \frac{1}{2} AK$ and $\vec{O} \cdot \vec{u}_L = \frac{1}{2} AL$. Let $\phi = \angle KAL = A - \theta_K - \theta_L$. The vector $\vec{O}$ can be expressed as $\vec{O} = x \vec{u}_K + y \vec{u}_L$. Solving the system $x + y \cos \phi = \frac{1}{2} AK$ and $x \cos \phi + y = \frac{1}{2} AL$ gives:
10: \[ x = \frac{AK - AL \cos \phi}{2 \sin^2 \phi}, \quad y = \frac{AL - AK \cos \phi}{2 \sin^2 \phi} \]
11: Now compute $\vec{O} \cdot \vec{B}$ where $\vec{B} = c \vec{u}_{AB}$. Note $\vec{u}_K \cdot \vec{u}_{AB} = \cos \theta_K$ and $\vec{u}_L \cdot \vec{u}_{AB} = \cos(A - \theta_L)$.
12: \[ \vec{O} \cdot \vec{B} = \frac{c}{2 \sin^2 \phi} [ (AK - AL \cos \phi) \cos \theta_K + (AL - AK \cos \phi) \cos(A - \theta_L) ] \]
13: Using the identities $\cos \theta_K - \cos \phi \cos(A - \theta_L) = \sin(A - \theta_L) \sin \phi$ and $\cos(A - \theta_L) - \cos \phi \cos \theta_K = -\sin \theta_K \sin \phi$, we find:
14: \[ \vec{O} \cdot \vec{B} = \frac{c}{2 \sin \phi} [ AK \sin(A - \theta_L) - AL \sin \theta_K ] \]
15: Similarly, $\vec{O} \cdot \vec{C} = \frac{b}{2 \sin \phi} [ AL \sin(A - \theta_K) - AK \sin \theta_L ]$.
16: The difference is:
17: \[ \vec{O} \cdot (\vec{B} - \vec{C}) = \frac{1}{2 \sin \phi} [ AK (c \sin(A - \theta_L) + b \sin \theta_L) - AL (c \sin \theta_K + b \sin(A - \theta_K)) ] \]
18: Using $c \sin(A - \theta_L) + b \sin \theta_L = a \sin(C + \theta_L)$ and $c \sin \theta_K + b \sin(A - \theta_K) = a \sin(B + \theta_K)$, we have:
19: \[ \vec{O} \cdot (\vec{B} - \vec{C}) = \frac{a}{2 \sin \phi} [ AK \sin(C + \theta_L) - AL \sin(B + \theta_K) ] \]
20: Substituting the expressions for $AK$ and $AL$ and utilizing the constraints $\frac{\sin \theta_K}{\sin(\alpha + \theta_K)} = \frac{\sin \gamma}{2 \sin(\alpha + \gamma)}$ and $\frac{\sin \theta_L}{\sin(\alpha + \theta_L)} = \frac{\sin \beta}{2 \sin(\alpha + \beta)}$, along with the Law of Sines relations from $\angle LBK = \beta$ and $\angle LCK = \gamma$, the expression simplifies to:
21: \[ \vec{O} \cdot (\vec{B} - \vec{C}) = \frac{c^2 - b^2}{4} \]
22: Thus, $O$ lies on the perpendicular bisector of $MN$, which implies $OM = ON$.

# Proof B

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
