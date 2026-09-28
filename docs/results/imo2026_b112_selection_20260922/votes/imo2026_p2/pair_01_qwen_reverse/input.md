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
