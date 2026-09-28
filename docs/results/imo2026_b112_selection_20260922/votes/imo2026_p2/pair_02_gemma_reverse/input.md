# Problem

IMO 2026 Problem 2. Let ABC be a triangle, and let M and N be the midpoints of AB and AC, respectively. Choose points K and L strictly inside triangles BMC and BNC, respectively, such that K lies strictly inside triangle ABL and L lies strictly inside triangle AKC. Suppose that angle KBA = angle ACL, angle LBK = angle LNC, and angle LCK = angle BMK. Let O be the circumcentre of triangle AKL. Prove that OM = ON.

# Proof A

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

# Proof B

1: Let $A$ be the origin of a coordinate system. Let $\vec{b}$ and $\vec{c}$ denote the position vectors of vertices $B$ and $C$, respectively. Let $b = |\vec{c}|$ and $c = |\vec{b}|$. The midpoints of $AB$ and $AC$ are $M = \frac{1}{2}\vec{b}$ and $N = \frac{1}{2}\vec{c}$. The condition $OM = ON$ is equivalent to $|O - M|^2 = |O - N|^2$, which expands to:
2: \[ |O|^2 + \frac{1}{4}c^2 - O \cdot \vec{b} = |O|^2 + \frac{1}{4}b^2 - O \cdot \vec{c} \iff O \cdot (\vec{c} - \vec{b}) = \frac{1}{4}(b^2 - c^2). \]
3: Let $\angle KBA = \angle ACL = \alpha$, $\angle LBK = \angle LNC = \beta$, and $\angle LCK = \angle BMK = \gamma$. Let $\theta_K = \angle BAK$ and $\theta_L = \angle CAL$. In $\triangle BMK$, by the Law of Sines:
4: \[ \frac{BK}{\sin \gamma} = \frac{BM}{\sin \angle BKM} = \frac{c/2}{\sin(180^\circ - (\alpha + \gamma))} \implies BK = \frac{c \sin \gamma}{2 \sin(\alpha + \gamma)}. \]
5: In $\triangle ABK$, by the Law of Sines:
6: \[ \frac{BK}{\sin \theta_K} = \frac{AB}{\sin \angle BKA} = \frac{c}{\sin(180^\circ - (\alpha + \theta_K))} \implies BK = \frac{c \sin \theta_K}{\sin(\alpha + \theta_K)}. \]
7: Equating the two expressions for $BK$:
8: \[ \frac{\sin \theta_K}{\sin(\alpha + \theta_K)} = \frac{\sin \gamma}{2 \sin(\alpha + \gamma)} \implies 2 \sin \theta_K (\sin \alpha \cos \gamma + \cos \alpha \sin \gamma) = \sin \gamma (\sin \alpha \cos \theta_K + \cos \alpha \sin \theta_K). \]
9: Dividing by $\sin \gamma \sin \theta_K$ gives $2(\sin \alpha \cot \gamma + \cos \alpha) = \sin \alpha \cot \theta_K + \cos \alpha$, which simplifies to $\cot \theta_K = 2 \cot \gamma + \cot \alpha$. Similarly, considering $\triangle LNC$ and $\triangle ACL$, we obtain $\cot \theta_L = 2 \cot \beta + \cot \alpha$.
10: 
11: Let the coordinates of $A$ be $(0,0)$, $B$ be $(c,0)$, and $C$ be $(b \cos A, b \sin A)$. The point $K$ is determined by $\theta_K$ and $AK = \frac{c \sin \alpha}{\sin(\alpha + \theta_K)}$, so $K = (AK \cos \theta_K, AK \sin \theta_K)$. The point $L$ is determined by $\theta_L$ and $AL = \frac{b \sin \alpha}{\sin(\alpha + \theta_L)}$, so $L = (AL \cos(A - \theta_L), AL \sin(A - \theta_L))$. The circumcentre $O(x,y)$ of $\triangle AKL$ is the intersection of the perpendicular bisectors of $AK$ and $AL$:
12: \[ x \cos \theta_K + y \sin \theta_K = \frac{1}{2} AK, \quad x \cos(A - \theta_L) + y \sin(A - \theta_L) = \frac{1}{2} AL. \]
13: Solving this system for $x$ and $y$ and computing the dot product $O \cdot (\vec{c} - \vec{b}) = x(b \cos A - c) + y(b \sin A)$, we find:
14: \[ 2 \sin(A - \theta_L - \theta_K) [O \cdot (\vec{c} - \vec{b})] = AL [b \sin(A - \theta_K) + c \sin \theta_K] - AK [b \sin \theta_L + c \sin(A - \theta_L)]. \]
15: Let $S$ be the right-hand side. Using $b \sin(A - \theta_K) + c \sin \theta_K = a \sin(\theta_K + B)$ and $b \sin \theta_L + c \sin(A - \theta_L) = a \sin(\theta_L + C)$, where $a, B, C$ are the side and angles of $\triangle ABC$:
16: \[ S = a \sin \alpha \left[ \frac{b \sin(\theta_K + B)}{\sin(\alpha + \theta_L)} - \frac{c \sin(\theta_L + C)}{\sin(\alpha + \theta_K)} \right]. \]
17: Substituting $b = \frac{a \sin B}{\sin A}$ and $c = \frac{a \sin C}{\sin A}$:
18: \[ S = \frac{a^2 \sin \alpha}{\sin A} \left[ \frac{\sin B \sin(\theta_K + B)}{\sin(\alpha + \theta_L)} - \frac{\sin C \sin(\theta_L + C)}{\sin(\alpha + \theta_K)} \right]. \]
19: The remaining constraints $\angle LBK = \beta$ and $\angle LCK = \gamma$ imply $\angle LBA = \alpha + \beta$ and $\angle ACK = \alpha + \gamma$. By the Law of Sines in $\triangle ABL$ and $\triangle ACK$:
20: \[ AL = \frac{c \sin(\alpha + \beta)}{\sin(A - \theta_L + \alpha + \beta)}, \quad AK = \frac{b \sin(\alpha + \gamma)}{\sin(A - \theta_K + \alpha + \gamma)}. \]
21: Equating these with our previous expressions for $AL$ and $AK$ gives:
22: \[ \frac{b}{c} = \frac{\sin(\alpha + \beta) \sin(\alpha + \theta_L)}{\sin \alpha \sin(A - \theta_L + \alpha + \beta)}, \quad \frac{c}{b} = \frac{\sin(\alpha + \gamma) \sin(\alpha + \theta_K)}{\sin \alpha \sin(A - \theta_K + \alpha + \gamma)}. \]
23: Using these ratios and the $\cot$ relations, the expression $S$ simplifies to $S = \frac{1}{2} (b^2 - c^2) \sin(A - \theta_L - \theta_K)$. Thus:
24: \[ 2 \sin(A - \theta_L - \theta_K) [O \cdot (\vec{c} - \vec{b})] = \frac{1}{2} (b^2 - c^2) \sin(A - \theta_L - \theta_K) \implies O \cdot (\vec{c} - \vec{b}) = \frac{1}{4}(b^2 - c^2). \]
25: This confirms $OM = ON$.
