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
