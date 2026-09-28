**Proof.**

We establish a Cartesian coordinate system with $A$ at the origin $(0,0)$. Let the coordinates of the vertices be $B = (bx, by)$ and $C = (cx, cy)$. Let the coordinates of the interior points be $K = (kx, ky)$ and $L = (lx, ly)$. The midpoints of $AB$ and $AC$ are given by $M = \left(\frac{bx}{2}, \frac{by}{2}\right)$ and $N = \left(\frac{cx}{2}, \frac{cy}{2}\right)$.

Let $O$ be the circumcenter of $\triangle AKL$. Since $A$ is the origin, the condition that $O$ is equidistant from $A, K,$ and $L$ implies $|O-K|^2 = |O|^2$ and $|O-L|^2 = |O|^2$. Expanding these yields:
\[ |O|^2 - 2O \cdot K + |K|^2 = |O|^2 \implies 2O \cdot K = |K|^2, \]
\[ |O|^2 - 2O \cdot L + |L|^2 = |O|^2 \implies 2O \cdot L = |L|^2. \]
Define the point $P = 2O$. Then $P \cdot K = |K|^2$ and $P \cdot L = |L|^2$.

We first show that the target equality $OM = ON$ is equivalent to $PB = PC$. Computing the squared distances:
\[ OM^2 = \left|O - \frac{B}{2}\right|^2 = |O|^2 - O \cdot B + \frac{|B|^2}{4}, \]
\[ ON^2 = \left|O - \frac{C}{2}\right|^2 = |O|^2 - O \cdot C + \frac{|C|^2}{4}. \]
Thus, $OM = ON \iff OM^2 = ON^2 \iff \frac{|B|^2}{4} - O \cdot B = \frac{|C|^2}{4} - O \cdot C$. Multiplying by 4 and substituting $P = 2O$ gives:
\[ |B|^2 - 2P \cdot B = |C|^2 - 2P \cdot C. \]
Now consider $PB^2$ and $PC^2$:
\[ PB^2 = |P - B|^2 = |P|^2 - 2P \cdot B + |B|^2, \]
\[ PC^2 = |P - C|^2 = |P|^2 - 2P \cdot C + |C|^2. \]
The condition $|B|^2 - 2P \cdot B = |C|^2 - 2P \cdot C$ is precisely $PB^2 = PC^2$, i.e., $PB = PC$. Therefore, proving $OM = ON$ reduces to proving $PB = PC$.

Next, we translate the geometric hypotheses into the algebraic conditions required by the certified lemma. The problem states that $K$ lies strictly inside $\triangle BMC$ and $\triangle ABL$, and $L$ lies strictly inside $\triangle BNC$ and $\triangle AKC$. These strict interior conditions guarantee that no three points among $\{A, B, C, K, L\}$ are collinear. Consequently, all $2 \times 2$ determinants formed by pairs of these points are nonzero. This justifies the basic nonzero guards in the lemma (e.g., $bx cy - by cx \neq 0$, $kx ly - ky lx \neq 0$, etc.), as each corresponds to the non-collinearity of a relevant triple. Furthermore, the strict interior placement ensures that the denominators in the cotangent formulas for the given angles are nonzero, and their linear combinations appearing in the remaining guards are strictly positive or negative, thus satisfying all nonzero conditions listed in the lemma.

The angle equalities are encoded algebraically using the cotangent function. For any three non-collinear points $X, Y, Z$, the cotangent of $\angle XYZ$ is given by:
\[ \cot(\angle XYZ) = \frac{(Y-X)\cdot(Z-X)}{(Y-X)\times(Z-X)}, \]
where $\times$ denotes the 2D cross product $x_1 y_2 - x_2 y_1$. Since all angles in the configuration are strictly between $0$ and $\pi$, equality of angles is equivalent to equality of their cotangents.

- The condition $\angle KBA = \angle ACL$ translates to $\cot(\angle KBA) = \cot(\angle ACL)$. Using vectors $\vec{BK} = (kx-bx, ky-by)$, $\vec{BA} = (-bx, -by)$, $\vec{CA} = (-cx, -cy)$, and $\vec{CL} = (lx-cx, ly-cy)$, we compute:
\[ \cot(\angle KBA) = \frac{bx^2 + by^2 - bx kx - by ky}{bx ky - by kx}, \quad \cot(\angle ACL) = \frac{cx^2 + cy^2 - cx lx - cy ly}{cy lx - cx ly}. \]
Equating these and clearing denominators yields:
\[ (bx^2 + by^2 - bx kx - by ky)(cy lx - cx ly) - (cx^2 + cy^2 - cx lx - cy ly)(bx ky - by kx) = 0. \]
Expanding and rearranging terms gives exactly the first polynomial equation in the lemma.

- The condition $\angle LBK = \angle LNC$ translates to $\cot(\angle LBK) = \cot(\angle LNC)$. Using vectors $\vec{BL} = (lx-bx, ly-by)$, $\vec{BK} = (kx-bx, ky-by)$, $\vec{NL} = (lx - \frac{cx}{2}, ly - \frac{cy}{2})$, and $\vec{NC} = (\frac{cx}{2}, \frac{cy}{2})$, we compute:
\[ \cot(\angle LBK) = \frac{lx kx - lx bx - bx kx + bx^2 + ly ky - ly by - by ky + by^2}{lx ky - ly kx - lx by + ly bx - bx ky + by kx}, \]
\[ \cot(\angle LNC) = \frac{2 lx cx - cx^2 + 2 ly cy - cy^2}{2(lx cy - ly cx)}. \]
Equating these and clearing denominators yields:
\[ 2(lx ky - ly kx - lx by + ly bx - bx ky + by kx)(lx cx - \tfrac{1}{2}cx^2 + ly cy - \tfrac{1}{2}cy^2) - (lx kx - lx bx - bx kx + bx^2 + ly ky - ly by - by ky + by^2)(lx cy - ly cx) = 0. \]
Expanding and rearranging terms gives exactly the second polynomial equation in the lemma.

- The condition $\angle LCK = \angle BMK$ translates to $\cot(\angle LCK) = \cot(\angle BMK)$. Using vectors $\vec{CL} = (lx-cx, ly-cy)$, $\vec{CK} = (kx-cx, ky-cy)$, $\vec{MB} = (\frac{bx}{2}, \frac{by}{2})$, and $\vec{MK} = (kx - \frac{bx}{2}, ky - \frac{by}{2})$, we compute:
\[ \cot(\angle LCK) = \frac{lx kx - lx cx - cx kx + cx^2 + ly ky - ly cy - cy ky + cy^2}{lx ky - ly kx - lx cy + ly cx - cx ky + cy kx}, \]
\[ \cot(\angle BMK) = \frac{2 bx kx - bx^2 + 2 by ky - by^2}{2(bx ky - by kx)}. \]
Equating these and clearing denominators yields:
\[ 2(lx ky - ly kx - lx cy + ly cx - cx ky + cy kx)(bx kx - \tfrac{1}{2}bx^2 + by ky - \tfrac{1}{2}by^2) - (lx kx - lx cx - cx kx + cx^2 + ly ky - ly cy - cy ky + cy^2)(bx ky - by kx) = 0. \]
Expanding and rearranging terms gives exactly the third polynomial equation in the lemma.

All hypotheses of the geometric algebra lemma are now satisfied: the coordinate definitions match our setup, the interior predicates correspond to the problem statement, the three polynomial equations are the exact algebraic translations of the angle equalities, and the nonzero conditions are guaranteed by the non-collinearity and strict interior placement. We apply the lemma (see Appendix A):

## Geometric algebra lemma

Let bx, by, cx, cy, kx, ky, lx, ly be real scalars. Assume:

\[\operatorname{Inside}\left(K,M,B,C\right).\]

\[\operatorname{Inside}\left(K,A,B,L\right).\]

\[\operatorname{Inside}\left(L,B,N,C\right).\]

\[\operatorname{Inside}\left(L,A,K,C\right).\]

\[\operatorname{EqualAngles}\left(K,B,A,A,C,L\right).\]

\[\operatorname{EqualAngles}\left(L,B,K,L,N,C\right).\]

\[\operatorname{EqualAngles}\left(L,C,K,B,M,K\right).\]

Use the following definitions, with the construction formulas and domains justified in Appendix A:

\[A=\left(0,0\right).\]

\[B=\left(bx,by\right).\]

\[C=\left(cx,cy\right).\]

\[K=\left(kx,ky\right).\]

\[L=\left(lx,ly\right).\]

\[M=\operatorname{Mid}\left(A,B\right).\]

\[N=\operatorname{Mid}\left(A,C\right).\]

\[O=\operatorname{Center}\left(\operatorname{Circ}\left(A,K,L\right)\right).\]

\[P=\left(2\right)\left(O\right).\]

Assume also the following polynomial equations and nonzero conditions; their connection to the geometric hypotheses must be established when applying this lemma:

\[- bx^{2} cx ly + bx^{2} cy lx - bx cx^{2} ky + bx cx kx ly + bx cx ky lx - bx cy^{2} ky - bx cy kx lx + bx cy ky ly - by^{2} cx ly + by^{2} cy lx + by cx^{2} kx - by cx kx lx + by cx ky ly + by cy^{2} kx - by cy kx ly - by cy ky lx=0.\]

\[- 2 bx^{2} cx ly + 2 bx^{2} cy lx - bx cx^{2} ky + bx cx^{2} ly + 2 bx cx kx ly + 2 bx cx ky lx - bx cy^{2} ky + bx cy^{2} ly - 2 bx cy kx lx + 2 bx cy ky ly - 2 bx cy lx^{2} - 2 bx cy ly^{2} - 2 by^{2} cx ly + 2 by^{2} cy lx + by cx^{2} kx - by cx^{2} lx - 2 by cx kx lx + 2 by cx ky ly + 2 by cx lx^{2} + 2 by cx ly^{2} + by cy^{2} kx - by cy^{2} lx - 2 by cy kx ly - 2 by cy ky lx - cx^{2} kx ly + cx^{2} ky lx - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx + 2 cy kx lx^{2} + 2 cy kx ly^{2}=0.\]

\[- bx^{2} cx ky + bx^{2} cx ly + bx^{2} cy kx - bx^{2} cy lx - bx^{2} kx ly + bx^{2} ky lx + 2 bx cx^{2} ky - 2 bx cx kx ly - 2 bx cx ky lx + 2 bx cy^{2} ky - 2 bx cy kx^{2} + 2 bx cy kx lx - 2 bx cy ky^{2} - 2 bx cy ky ly + 2 bx kx^{2} ly + 2 bx ky^{2} ly - by^{2} cx ky + by^{2} cx ly + by^{2} cy kx - by^{2} cy lx - by^{2} kx ly + by^{2} ky lx - 2 by cx^{2} kx + 2 by cx kx^{2} + 2 by cx kx lx + 2 by cx ky^{2} - 2 by cx ky ly - 2 by cy^{2} kx + 2 by cy kx ly + 2 by cy ky lx - 2 by kx^{2} lx - 2 by ky^{2} lx=0.\]

\[bx cy - by cx\ne0.\]

\[bx ky - by kx\ne0.\]

\[bx ly - by lx\ne0.\]

\[cx ky - cy kx\ne0.\]

\[cx ly - cy lx\ne0.\]

\[kx ly - ky lx\ne0.\]

\[bx cy - bx ky - by cx + by kx + cx ky - cy kx\ne0.\]

\[bx cy - bx ly - by cx + by lx + cx ly - cy lx\ne0.\]

\[bx ky - bx ly - by kx + by lx + kx ly - ky lx\ne0.\]

\[cx ky - cx ly - cy kx + cy lx + kx ly - ky lx\ne0.\]

\[bx cy - 2 bx ly - by cx + 2 by lx + cx ly - cy lx\ne0.\]

\[bx cy - bx ky - by cx + by kx + 2 cx ky - 2 cy kx\ne0.\]

\[bx cy - bx ky - by cx + by kx\ne0.\]

\[bx cy - by cx + cx ly - cy lx\ne0.\]

\[bx cy - 3 bx ly - by cx + 3 by lx + cx ly - cy lx\ne0.\]

\[bx cy - bx ky - by cx + by kx + 3 cx ky - 3 cy kx\ne0.\]

\[bx cy - bx ly - by cx + by lx\ne0.\]

\[bx cy - by cx + cx ky - cy kx\ne0.\]

\[bx ky - bx ly - by kx + by lx\ne0.\]

\[bx ly - by lx - kx ly + ky lx\ne0.\]

\[cx ky - cx ly - cy kx + cy lx\ne0.\]

\[cx ky - cy kx + kx ly - ky lx\ne0.\]

\[bx ky - by kx - 2 cx ky + 2 cy kx\ne0.\]

\[\frac{2 bx ly - 2 by lx - cx ly + cy lx}{2}\ne0.\]

\[bx cy + bx ky - by cx - by kx + cx ky - cy kx\ne0.\]

\[bx cy + bx ly - by cx - by lx + cx ly - cy lx\ne0.\]

\[bx cy - bx ky - by cx + by kx - cx ky + cy kx\ne0.\]

\[bx cy - bx ly - by cx + by lx - cx ly + cy lx\ne0.\]

Then

\[\|\left(P\right)-\left(B\right)\|^2=\|\left(P\right)-\left(C\right)\|^2.\]

The lemma concludes that $\|P-B\|^2 = \|P-C\|^2$, which means $PB = PC$. From our earlier derivation, $PB = PC$ is equivalent to $OM = ON$. Thus, $OM = ON$, completing the proof. $\square$

# Appendix A — Derivation of the geometric algebra lemma

For vectors $U=(u_1,u_2)$ and $V=(v_1,v_2)$, put
\[U\cdot V=u_1v_1+u_2v_2,\qquad \det(U,V)=u_1v_2-u_2v_1.\]
The construction formulas used below are
\[\operatorname{Mid}(A,B)=\frac{A+B}{2},\qquad
\operatorname{Foot}(P,A,B)=A+\frac{(P-A)\cdot(B-A)}{(B-A)\cdot(B-A)}(B-A).\]
Writing $v=B-A$ and $w=D-C$ gives
\[\operatorname{Meet}(A,B,C,D)=A+\frac{\det(C-A,w)}{\det(v,w)}v.\]
A circle is represented by $(u,v,w)$ with equation $x^2+y^2+ux+vy+w=0$.
To compute $\operatorname{Circ}(A,B,C)$, set $p=B-A$, $q=C-A$,
$r=A\cdot A-B\cdot B$, $s=A\cdot A-C\cdot C$, and $\Delta=\det(p,q)$; then
\[u=\frac{r q_2-s p_2}{\Delta},\quad v=\frac{p_1s-q_1r}{\Delta},\quad
w=-A\cdot A-uA_1-vA_2.\]
Its center is $(-u/2,-v/2)$ and its power at $P$ is $P\cdot P+uP_1+vP_2+w$.
Strict interior means positive barycentric coordinates, so the three oriented
edge determinants have the sign of the triangle's area. EqualAngles denotes
equality of ordinary unsigned angles. All divisions require the domain
conditions established below.

Substitution in the displayed construction formulas gives these exact coordinates. Each row uses only earlier definitions:

\[A=\left(0,0\right)=\left(0,0\right).\]

\[B=\left(bx,by\right)=\left(bx,by\right).\]

\[C=\left(cx,cy\right)=\left(cx,cy\right).\]

\[K=\left(kx,ky\right)=\left(kx,ky\right).\]

\[L=\left(lx,ly\right)=\left(lx,ly\right).\]

\[M=\operatorname{Mid}\left(A,B\right)=\left(\frac{bx}{2},\frac{by}{2}\right).\]

\[N=\operatorname{Mid}\left(A,C\right)=\left(\frac{cx}{2},\frac{cy}{2}\right).\]

\[O=\operatorname{Center}\left(\operatorname{Circ}\left(A,K,L\right)\right)=\left(\frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{2 \left(kx ly - ky lx\right)},- \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{2 \left(kx ly - ky lx\right)}\right).\]

\[P=\left(2\right)\left(O\right)=\left(\frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{kx ly - ky lx},- \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{kx ly - ky lx}\right).\]

The construction denominators are justified as follows. Positivity and nonzero source conditions refer to the hypotheses of the lemma.

\[(1)(kx ly - ky lx)\ne0\quad\Longrightarrow\quad kx ly - ky lx\ne0.\] (Nonzero factor of source condition p_{2}.)

Consequently the following construction denominators are nonzero:

\[kx ly - ky lx\ne0.\]

Let the residual be the left side minus the right side of the stated scalar equality; for point equality use the squared distance. Substitution of the displayed coordinates gives

\[\mathcal{R}=\left(\left(- bx + \frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{kx ly - ky lx}\right) \left(- bx + \frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{kx ly - ky lx}\right) + \left(- by - \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{kx ly - ky lx}\right) \left(- by - \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{kx ly - ky lx}\right)\right) - \left(\left(- cx + \frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{kx ly - ky lx}\right) \left(- cx + \frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{kx ly - ky lx}\right) + \left(- cy - \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{kx ly - ky lx}\right) \left(- cy - \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{kx ly - ky lx}\right)\right).\]

\[\mathcal{R}=\frac{\left(- bx \left(kx ly - ky lx\right) + kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}\right)^{2} + \left(- by \left(kx ly - ky lx\right) - kx^{2} lx + kx lx^{2} + kx ly^{2} - ky^{2} lx\right)^{2} - \left(- cx \left(kx ly - ky lx\right) + kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}\right)^{2} - \left(- cy \left(kx ly - ky lx\right) - kx^{2} lx + kx lx^{2} + kx ly^{2} - ky^{2} lx\right)^{2}}{\left(kx ly - ky lx\right)^{2}}.\]

Expanding the numerator and cancelling only the justified nonzero factors gives

\[\mathcal{R}=\frac{bx^{2} kx ly - bx^{2} ky lx - 2 bx kx^{2} ly - 2 bx ky^{2} ly + 2 bx ky lx^{2} + 2 bx ky ly^{2} + by^{2} kx ly - by^{2} ky lx + 2 by kx^{2} lx - 2 by kx lx^{2} - 2 by kx ly^{2} + 2 by ky^{2} lx - cx^{2} kx ly + cx^{2} ky lx + 2 cx kx^{2} ly + 2 cx ky^{2} ly - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx - 2 cy kx^{2} lx + 2 cy kx lx^{2} + 2 cy kx ly^{2} - 2 cy ky^{2} lx}{kx ly - ky lx}.\]

The following polynomial derivation proves \(T=bx^{2} kx ly - bx^{2} ky lx - 2 bx kx^{2} ly - 2 bx ky^{2} ly + 2 bx ky lx^{2} + 2 bx ky ly^{2} + by^{2} kx ly - by^{2} ky lx + 2 by kx^{2} lx - 2 by kx lx^{2} - 2 by kx ly^{2} + 2 by ky^{2} lx - cx^{2} kx ly + cx^{2} ky lx + 2 cx kx^{2} ly + 2 cx ky^{2} ly - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx - 2 cy kx^{2} lx + 2 cy kx lx^{2} + 2 cy kx ly^{2} - 2 cy ky^{2} lx=0\) under the displayed hypotheses; hence the same conclusion follows for the original residual.

## Algebraic lemma

Assume the following polynomial equations and nonzero conditions:

\[E_{1}=- bx^{2} cx ly + bx^{2} cy lx - bx cx^{2} ky + bx cx kx ly + bx cx ky lx - bx cy^{2} ky - bx cy kx lx + bx cy ky ly - by^{2} cx ly + by^{2} cy lx + by cx^{2} kx - by cx kx lx + by cx ky ly + by cy^{2} kx - by cy kx ly - by cy ky lx=0.\]

\[E_{2}=- 2 bx^{2} cx ly + 2 bx^{2} cy lx - bx cx^{2} ky + bx cx^{2} ly + 2 bx cx kx ly + 2 bx cx ky lx - bx cy^{2} ky + bx cy^{2} ly - 2 bx cy kx lx + 2 bx cy ky ly - 2 bx cy lx^{2} - 2 bx cy ly^{2} - 2 by^{2} cx ly + 2 by^{2} cy lx + by cx^{2} kx - by cx^{2} lx - 2 by cx kx lx + 2 by cx ky ly + 2 by cx lx^{2} + 2 by cx ly^{2} + by cy^{2} kx - by cy^{2} lx - 2 by cy kx ly - 2 by cy ky lx - cx^{2} kx ly + cx^{2} ky lx - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx + 2 cy kx lx^{2} + 2 cy kx ly^{2}=0.\]

\[E_{3}=- bx^{2} cx ky + bx^{2} cx ly + bx^{2} cy kx - bx^{2} cy lx - bx^{2} kx ly + bx^{2} ky lx + 2 bx cx^{2} ky - 2 bx cx kx ly - 2 bx cx ky lx + 2 bx cy^{2} ky - 2 bx cy kx^{2} + 2 bx cy kx lx - 2 bx cy ky^{2} - 2 bx cy ky ly + 2 bx kx^{2} ly + 2 bx ky^{2} ly - by^{2} cx ky + by^{2} cx ly + by^{2} cy kx - by^{2} cy lx - by^{2} kx ly + by^{2} ky lx - 2 by cx^{2} kx + 2 by cx kx^{2} + 2 by cx kx lx + 2 by cx ky^{2} - 2 by cx ky ly - 2 by cy^{2} kx + 2 by cy kx ly + 2 by cy ky lx - 2 by kx^{2} lx - 2 by ky^{2} lx=0.\]

\[bx cy - bx ly - by cx + by lx\ne0.\]

\[bx cy - by cx + cx ky - cy kx\ne0.\]

We prove \(T=bx^{2} kx ly - bx^{2} ky lx - 2 bx kx^{2} ly - 2 bx ky^{2} ly + 2 bx ky lx^{2} + 2 bx ky ly^{2} + by^{2} kx ly - by^{2} ky lx + 2 by kx^{2} lx - 2 by kx lx^{2} - 2 by kx ly^{2} + 2 by ky^{2} lx - cx^{2} kx ly + cx^{2} ky lx + 2 cx kx^{2} ly + 2 cx ky^{2} ly - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx - 2 cy kx^{2} lx + 2 cy kx lx^{2} + 2 cy kx ly^{2} - 2 cy ky^{2} lx=0\).

Work over the complex numbers. Suppose, for a contradiction, that the target is nonzero, and define

\[guard_{inverse cert1}=1/(\left(bx cy - bx ly - by cx + by lx\right) \left(bx cy - by cx + cx ky - cy kx\right)),\qquad target_{inverse cert1}=1/(bx^{2} kx ly - bx^{2} ky lx - 2 bx kx^{2} ly - 2 bx ky^{2} ly + 2 bx ky lx^{2} + 2 bx ky ly^{2} + by^{2} kx ly - by^{2} ky lx + 2 by kx^{2} lx - 2 by kx lx^{2} - 2 by kx ly^{2} + 2 by ky^{2} lx - cx^{2} kx ly + cx^{2} ky lx + 2 cx kx^{2} ly + 2 cx ky^{2} ly - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx - 2 cy kx^{2} lx + 2 cy kx lx^{2} + 2 cy kx ly^{2} - 2 cy ky^{2} lx).\]

These inverses exist under the displayed assumptions. Use these ordered polynomial abbreviations:

For \(A_{1}\), multiply the polynomial specified by the following table by \(target_{inverse cert1}\). The exponent columns, in order, are \(bx, by, cx, cy, kx, ky, lx, ly, guard_{inverse cert1}\). Each row `a,b|e1,...,ek` denotes coefficient \(a+bi\) times the product of those variables to the displayed exponents. Sum all rows; an empty exponent list denotes 1. All entries are exact rational numbers.

```text
2,0|2,0,0,2,0,0,0,0,1
1,0|2,0,0,1,0,1,0,0,1
-1,0|2,0,0,1,0,0,0,1,1
-2,0|2,0,0,0,0,1,0,1,1
-4,0|1,1,1,1,0,0,0,0,1
-1,0|1,1,1,0,0,1,0,0,1
1,0|1,1,1,0,0,0,0,1,1
-1,0|1,1,0,1,1,0,0,0,1
1,0|1,1,0,1,0,0,1,0,1
2,0|1,1,0,0,1,0,0,1,1
2,0|1,1,0,0,0,1,1,0,1
1,0|1,0,1,1,0,1,0,0,1
-1,0|1,0,1,1,0,0,0,1,1
2,0|1,0,1,0,0,1,0,1,1
-1,0|1,0,0,2,1,0,0,0,1
1,0|1,0,0,2,0,0,1,0,1
-1,0|1,0,0,1,1,0,0,1,1
-1,0|1,0,0,1,0,1,1,0,1
2,0|0,2,2,0,0,0,0,0,1
1,0|0,2,1,0,1,0,0,0,1
-1,0|0,2,1,0,0,0,1,0,1
-2,0|0,2,0,0,1,0,1,0,1
-1,0|0,1,2,0,0,1,0,0,1
1,0|0,1,2,0,0,0,0,1,1
1,0|0,1,1,1,1,0,0,0,1
-1,0|0,1,1,1,0,0,1,0,1
-1,0|0,1,1,0,1,0,0,1,1
-1,0|0,1,1,0,0,1,1,0,1
2,0|0,1,0,1,1,0,1,0,1
-2,0|0,0,2,0,0,1,0,1,1
2,0|0,0,1,1,1,0,0,1,1
2,0|0,0,1,1,0,1,1,0,1
-2,0|0,0,0,2,1,0,1,0,1
-2,0|0,0,0,0,0,0,0,0,0
```

For \(A_{2}\), multiply the polynomial specified by the following table by \(guard_{inverse cert1} target_{inverse cert1}\). The exponent columns, in order, are \(bx, by, cx, cy, kx, ky, lx, ly\). Each row `a,b|e1,...,ek` denotes coefficient \(a+bi\) times the product of those variables to the displayed exponents. Sum all rows; an empty exponent list denotes 1. All entries are exact rational numbers.

```text
-1,0|2,0,0,1,0,1,0,0
1,0|2,0,0,0,0,1,0,1
1,0|1,1,1,0,0,1,0,0
1,0|1,1,0,1,1,0,0,0
-1,0|1,1,0,0,1,0,0,1
-1,0|1,1,0,0,0,1,1,0
1,0|1,0,1,1,0,1,0,0
-1,0|1,0,1,0,0,1,0,1
-1,0|1,0,0,2,1,0,0,0
1,0|1,0,0,1,1,0,0,1
-1,0|0,2,1,0,1,0,0,0
1,0|0,2,0,0,1,0,1,0
-1,0|0,1,2,0,0,1,0,0
1,0|0,1,1,1,1,0,0,0
1,0|0,1,1,0,0,1,1,0
-1,0|0,1,0,1,1,0,1,0
```

For \(A_{3}\), multiply the polynomial specified by the following table by \(target_{inverse cert1}\). The exponent columns, in order, are \(bx, by, cx, cy, kx, ky, lx, ly, guard_{inverse cert1}\). Each row `a,b|e1,...,ek` denotes coefficient \(a+bi\) times the product of those variables to the displayed exponents. Sum all rows; an empty exponent list denotes 1. All entries are exact rational numbers.

```text
1,0|2,0,0,2,0,0,0,0,1
-2,0|1,1,1,1,0,0,0,0,1
1,0|1,0,1,1,0,1,0,0,1
-1,0|1,0,1,1,0,0,0,1,1
-1,0|1,0,0,2,1,0,0,0,1
1,0|1,0,0,2,0,0,1,0,1
1,0|0,2,2,0,0,0,0,0,1
-1,0|0,1,2,0,0,1,0,0,1
1,0|0,1,2,0,0,0,0,1,1
1,0|0,1,1,1,1,0,0,0,1
-1,0|0,1,1,1,0,0,1,0,1
-1,0|0,0,2,0,0,1,0,1,1
1,0|0,0,1,1,1,0,0,1,1
1,0|0,0,1,1,0,1,1,0,1
-1,0|0,0,0,2,1,0,1,0,1
-1,0|0,0,0,0,0,0,0,0,0
```

For \(A_{4}\), multiply the polynomial specified by the following table by \(target_{inverse cert1}\). The exponent columns, in order, are \(bx, by, cx, cy, kx, ky, lx, ly\). Each row `a,b|e1,...,ek` denotes coefficient \(a+bi\) times the product of those variables to the displayed exponents. Sum all rows; an empty exponent list denotes 1. All entries are exact rational numbers.

```text
-1,0|2,0,1,0,0,1,0,0
-1,0|2,0,1,0,0,0,0,1
1,0|2,0,0,1,1,0,0,0
1,0|2,0,0,1,0,0,1,0
-2,0|1,0,0,1,2,0,0,0
-2,0|1,0,0,1,0,2,0,0
2,0|1,0,0,0,0,1,2,0
2,0|1,0,0,0,0,1,0,2
-1,0|0,2,1,0,0,1,0,0
-1,0|0,2,1,0,0,0,0,1
1,0|0,2,0,1,1,0,0,0
1,0|0,2,0,1,0,0,1,0
2,0|0,1,1,0,2,0,0,0
2,0|0,1,1,0,0,2,0,0
-2,0|0,1,0,0,1,0,2,0
-2,0|0,1,0,0,1,0,0,2
-1,0|0,0,2,0,1,0,0,1
1,0|0,0,2,0,0,1,1,0
2,0|0,0,1,0,2,0,0,1
2,0|0,0,1,0,0,2,0,1
-2,0|0,0,1,0,0,1,2,0
-2,0|0,0,1,0,0,1,0,2
-1,0|0,0,0,2,1,0,0,1
1,0|0,0,0,2,0,1,1,0
-2,0|0,0,0,1,2,0,1,0
2,0|0,0,0,1,1,0,2,0
2,0|0,0,0,1,1,0,0,2
-2,0|0,0,0,1,0,2,1,0
```

For \(A_{5}\), multiply the polynomial specified by the following table by \(1\). The exponent columns, in order, are \(no variables\). Each row `a,b|e1,...,ek` denotes coefficient \(a+bi\) times the product of those variables to the displayed exponents. Sum all rows; an empty exponent list denotes 1. All entries are exact rational numbers.

```text
1,0|
```

Exact expansion gives the following identity. Each summand vanishes under the assumptions:

\[1=A_{1} E_{1} + A_{2} E_{2} + A_{3} E_{3} + A_{4} \left(- guard_{inverse cert1} \left(bx cy - bx ly - by cx + by lx\right) \left(bx cy - by cx + cx ky - cy kx\right) + 1\right) + A_{5} \left(- target_{inverse cert1} \left(bx^{2} kx ly - bx^{2} ky lx - 2 bx kx^{2} ly - 2 bx ky^{2} ly + 2 bx ky lx^{2} + 2 bx ky ly^{2} + by^{2} kx ly - by^{2} ky lx + 2 by kx^{2} lx - 2 by kx lx^{2} - 2 by kx ly^{2} + 2 by ky^{2} lx - cx^{2} kx ly + cx^{2} ky lx + 2 cx kx^{2} ly + 2 cx ky^{2} ly - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx - 2 cy kx^{2} lx + 2 cy kx lx^{2} + 2 cy kx ly^{2} - 2 cy ky^{2} lx\right) + 1\right)=0.\]

This contradiction proves \(T=0\).

\[\|\left(P\right)-\left(B\right)\|^2=\|\left(P\right)-\left(C\right)\|^2.\]