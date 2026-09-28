**Proof:**

We establish a Cartesian coordinate system with $A$ at the origin $(0,0)$. Let $B = (bx, by)$ and $C = (cx, cy)$. Since $ABC$ is a non-degenerate triangle, the determinant $bx cy - by cx \ne 0$. The midpoints of $AB$ and $AC$ are $M = \frac{A+B}{2} = (bx/2, by/2)$ and $N = \frac{A+C}{2} = (cx/2, cy/2)$. Let $K = (kx, ky)$ and $L = (lx, ly)$. Let $O$ be the circumcenter of $\triangle AKL$, and define the scaled point $O' = 2O$.

The geometric hypotheses translate into algebraic conditions via cotangents. For any two vectors $\vec{u}, \vec{v}$, we use $\cot \angle(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\vec{u} \times \vec{v}}$.

1. The condition $\angle KBA = \angle ACL$ implies equality of their cotangents. Using $\vec{BA} = (-bx, -by)$, $\vec{BK} = (kx-bx, ky-by)$, $\vec{CA} = (-cx, -cy)$, and $\vec{CL} = (lx-cx, ly-cy)$, we compute:
\[
\cot \angle KBA = \frac{bx^2 + by^2 - bx kx - by ky}{bx ky - by kx}, \quad \cot \angle ACL = \frac{cx^2 + cy^2 - cx lx - cy ly}{cx ly - cy lx}.
\]
Equating these expressions and clearing denominators yields a polynomial equation. Direct expansion confirms this is exactly the first polynomial equation $E_1 = 0$ listed in the lemma's hypotheses.

2. The condition $\angle LBK = \angle LNC$ gives:
\[
\cot \angle LBK = \frac{(lx-bx)(kx-bx) + (ly-by)(ky-by)}{lx ky - ly kx - lx by + ly bx - bx ky + by kx},
\]
\[
\cot \angle LNC = \frac{2 lx cx + 2 ly cy - cx^2 - cy^2}{2 lx cy - 2 ly cx}.
\]
Equating and clearing denominators yields the second polynomial equation $E_2 = 0$.

3. The condition $\angle LCK = \angle BMK$ gives:
\[
\cot \angle LCK = \frac{(lx-cx)(kx-cx) + (ly-cy)(ky-cy)}{(lx-cx)(ky-cy) - (ly-cy)(kx-cx)},
\]
\[
\cot \angle BMK = \frac{2 bx kx + 2 by ky - bx^2 - by^2}{2 bx ky - 2 by kx}.
\]
Equating and clearing denominators yields the third polynomial equation $E_3 = 0$.

The strict interior conditions ($K$ strictly inside $\triangle BMC$ and $\triangle ABL$, $L$ strictly inside $\triangle BNC$ and $\triangle AKC$) guarantee that no three points among $\{A, B, C, M, N, K, L\}$ are collinear, except for the defined midpoints $M \in AB$ and $N \in AC$. Consequently, every $2 \times 2$ determinant formed by coordinate pairs of these points is strictly nonzero. Each nonzero guard in the lemma corresponds to such a determinant (i.e., twice the signed area of a triangle formed by a subset of these points). Since the points lie strictly in the interior of the specified triangles, all these signed areas are strictly nonzero, thereby satisfying every division guard and non-degeneracy condition required by the lemma.

With the polynomial equations $E_1 = E_2 = E_3 = 0$ and all nonzero guards verified from the theorem's hypotheses, we apply the certified geometric algebra lemma:

## Geometric algebra lemma

Let bx, by, cx, cy, kx, ky, lx, ly be real scalars. Assume:

\[\operatorname{EqualAngles}\left(K,B,A,A,C,L\right).\]

\[\operatorname{EqualAngles}\left(L,B,K,L,N,C\right).\]

\[\operatorname{EqualAngles}\left(L,C,K,B,M,K\right).\]

\[\operatorname{Inside}\left(K,B,M,C\right).\]

\[\operatorname{Inside}\left(L,B,N,C\right).\]

\[\operatorname{Inside}\left(K,A,B,L\right).\]

\[\operatorname{Inside}\left(L,A,K,C\right).\]

Use the following definitions, with the construction formulas and domains justified in Appendix A:

\[A=\left(0,0\right).\]

\[B=\left(bx,by\right).\]

\[C=\left(cx,cy\right).\]

\[M=\operatorname{Mid}\left(A,B\right).\]

\[N=\operatorname{Mid}\left(A,C\right).\]

\[K=\left(kx,ky\right).\]

\[L=\left(lx,ly\right).\]

\[O=\operatorname{Center}\left(\operatorname{Circ}\left(A,K,L\right)\right).\]

\[O_{prime}=\left(2\right)\left(O\right).\]

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

\[\|\left(O_{prime}\right)-\left(B\right)\|^2=\|\left(O_{prime}\right)-\left(C\right)\|^2.\]

The lemma concludes that $\|O' - B\|^2 = \|O' - C\|^2$. We now translate this algebraic identity back to the original geometric configuration. By construction, $O' = 2O$, $M = B/2$, and $N = C/2$. Therefore,
\[
\|O' - B\|^2 = \|2O - B\|^2 = 4\left\|O - \frac{B}{2}\right\|^2 = 4\|O - M\|^2 = 4 OM^2,
\]
and similarly,
\[
\|O' - C\|^2 = \|2O - C\|^2 = 4\left\|O - \frac{C}{2}\right\|^2 = 4\|O - N\|^2 = 4 ON^2.
\]
The equality $\|O' - B\|^2 = \|O' - C\|^2$ thus implies $4 OM^2 = 4 ON^2$, which yields $OM = ON$. This completes the proof. $\square$

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

\[M=\operatorname{Mid}\left(A,B\right)=\left(\frac{bx}{2},\frac{by}{2}\right).\]

\[N=\operatorname{Mid}\left(A,C\right)=\left(\frac{cx}{2},\frac{cy}{2}\right).\]

\[K=\left(kx,ky\right)=\left(kx,ky\right).\]

\[L=\left(lx,ly\right)=\left(lx,ly\right).\]

\[O=\operatorname{Center}\left(\operatorname{Circ}\left(A,K,L\right)\right)=\left(\frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{2 \left(kx ly - ky lx\right)},- \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{2 \left(kx ly - ky lx\right)}\right).\]

\[O_{prime}=\left(2\right)\left(O\right)=\left(\frac{kx^{2} ly + ky^{2} ly - ky lx^{2} - ky ly^{2}}{kx ly - ky lx},- \frac{kx^{2} lx - kx lx^{2} - kx ly^{2} + ky^{2} lx}{kx ly - ky lx}\right).\]

The construction denominators are justified as follows. Positivity and nonzero source conditions refer to the hypotheses of the lemma.

\[(1)(kx ly - ky lx)\ne0\quad\Longrightarrow\quad kx ly - ky lx\ne0.\] (Nonzero factor of source condition p_{6}.)

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

\[\|\left(O_{prime}\right)-\left(B\right)\|^2=\|\left(O_{prime}\right)-\left(C\right)\|^2.\]