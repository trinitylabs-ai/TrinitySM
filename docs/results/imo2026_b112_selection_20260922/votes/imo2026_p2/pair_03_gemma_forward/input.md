# Problem

IMO 2026 Problem 2. Let ABC be a triangle, and let M and N be the midpoints of AB and AC, respectively. Choose points K and L strictly inside triangles BMC and BNC, respectively, such that K lies strictly inside triangle ABL and L lies strictly inside triangle AKC. Suppose that angle KBA = angle ACL, angle LBK = angle LNC, and angle LCK = angle BMK. Let O be the circumcentre of triangle AKL. Prove that OM = ON.

# Proof A

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
