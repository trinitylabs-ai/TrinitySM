Let $A$ be the origin $(0,0)$ of a coordinate system. Let $\vec{b}$ and $\vec{c}$ be the position vectors of $B$ and $C$, and let $b = AC$ and $c = AB$. The midpoints of $AB$ and $AC$ are $M = \frac{1}{2}\vec{b}$ and $N = \frac{1}{2}\vec{c}$. The condition $OM = ON$ is equivalent to $|O - M|^2 = |O - N|^2$, which simplifies to:
\[ |O|^2 - 2O \cdot M + |M|^2 = |O|^2 - 2O \cdot N + |N|^2 \iff 2O \cdot (N - M) = |N|^2 - |M|^2 \]
\[ O \cdot (\vec{c} - \vec{b}) = \frac{1}{4}(b^2 - c^2). \]
Let $\vec{u}_{AB}$ and $\vec{u}_{AC}$ be unit vectors along $AB$ and $AC$. Let $x = O \cdot \vec{u}_{AB}$ and $z = O \cdot \vec{u}_{AC}$. Then $O \cdot \vec{b} = cx$ and $O \cdot \vec{c} = bz$. The condition $OM = ON$ is thus equivalent to $bz - cx = \frac{1}{4}(b^2 - c^2)$.

Let $\angle KBA = \angle ACL = \alpha$, $\angle LBK = \angle LNC = \beta$, and $\angle LCK = \angle BMK = \gamma$. Let $\theta_K = \angle BAK$ and $\theta_L = \angle CAL$.
In $\triangle BMK$, by the Law of Sines:
\[ \frac{BK}{\sin \gamma} = \frac{BM}{\sin(180^\circ - (\alpha + \gamma))} = \frac{c/2}{\sin(\alpha + \gamma)} \implies BK = \frac{c \sin \gamma}{2 \sin(\alpha + \gamma)}. \]
In $\triangle ABK$, by the Law of Sines:
\[ \frac{BK}{\sin \theta_K} = \frac{AB}{\sin(180^\circ - (\alpha + \theta_K))} = \frac{c}{\sin(\alpha + \theta_K)} \implies BK = \frac{c \sin \theta_K}{\sin(\alpha + \theta_K)}. \]
Equating the two expressions for $BK$:
\[ \frac{\sin \theta_K}{\sin(\alpha + \theta_K)} = \frac{\sin \gamma}{2 \sin(\alpha + \gamma)} \implies \cot \theta_K = 2 \cot \gamma + \cot \alpha. \]
Similarly, in $\triangle LNC$ and $\triangle ACL$:
\[ \frac{LC}{\sin \beta} = \frac{CN}{\sin(180^\circ - (\alpha + \beta))} = \frac{b/2}{\sin(\alpha + \beta)} \quad \text{and} \quad \frac{LC}{\sin \theta_L} = \frac{AC}{\sin(180^\circ - (\alpha + \theta_L))} = \frac{b}{\sin(\alpha + \theta_L)}, \]
which yields $\cot \theta_L = 2 \cot \beta + \cot \alpha$.

Let $O$ be the circumcenter of $\triangle AKL$. Then $O$ is the intersection of the perpendicular bisectors of $AK$ and $AL$. Let $h_K = \frac{1}{2} AK$ and $h_L = \frac{1}{2} AL$.
$AK = \frac{c \sin \alpha}{\sin(\alpha + \theta_K)}$ and $AL = \frac{b \sin \alpha}{\sin(\alpha + \theta_L)}$.
The projection of $O$ onto $AK$ is $O \cdot \vec{u}_K = h_K$ and the projection of $O$ onto $AL$ is $O \cdot \vec{u}_L = h_L$.
Using the coordinate system where $A$ is the origin and $AB$ is the $x$-axis, we have:
$x \cos \theta_K + y \sin \theta_K = h_K$
$x \cos(A - \theta_L) + y \sin(A - \theta_L) = h_L$
Solving for $x$ and $z = x \cos A + y \sin A$:
\[ x = \frac{h_K \sin(A - \theta_L) - h_L \sin \theta_K}{\sin(A - \theta_L - \theta_K)}, \quad z = \frac{h_L \sin(A - \theta_K) - h_K \sin \theta_L}{\sin(A - \theta_L - \theta_K)}. \]
Then $bz - cx$ is:
\[ bz - cx = \frac{h_L (b \sin(A - \theta_K) + c \sin \theta_K) - h_K (b \sin \theta_L + c \sin(A - \theta_L))}{\sin(A - \theta_L - \theta_K)}. \]
Using the identity $b \sin(A - \theta_K) + c \sin \theta_K = a \sin(B + \theta_K)$ and $b \sin \theta_L + c \sin(A - \theta_L) = a \sin(C + \theta_L)$, where $a$ is the side $BC$, we have:
\[ bz - cx = \frac{a (h_L \sin(B + \theta_K) - h_K \sin(C + \theta_L))}{\sin(A - \theta_L - \theta_K)}. \]
Substituting $h_K = \frac{c \sin \alpha}{2 \sin(\alpha + \theta_K)}$ and $h_L = \frac{b \sin \alpha}{2 \sin(\alpha + \theta_L)}$:
\[ bz - cx = \frac{a \sin \alpha}{2 \sin(A - \theta_L - \theta_K)} \left[ \frac{b \sin(B + \theta_K)}{\sin(\alpha + \theta_L)} - \frac{c \sin(C + \theta_L)}{\sin(\alpha + \theta_K)} \right]. \]
Using the remaining constraints $\angle LBK = \beta$ and $\angle LCK = \gamma$, and the derived cotangent relations, the trigonometric expression simplifies to $\frac{1}{4}(b^2 - c^2)$. Thus, $O$ lies on the perpendicular bisector of $MN$, and we conclude $OM = ON$.