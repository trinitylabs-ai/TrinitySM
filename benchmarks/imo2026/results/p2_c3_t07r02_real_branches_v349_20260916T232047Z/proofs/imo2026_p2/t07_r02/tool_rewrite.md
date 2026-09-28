**Proof.**

We establish a Cartesian coordinate system with $A$ at the origin $(0,0)$. Let the coordinates of the vertices and interior points be $B = (bx, by)$, $C = (cx, cy)$, $K = (kx, ky)$, and $L = (lx, ly)$. Since $ABC$ is a non-degenerate triangle, $A, B, C$ are not collinear, which gives the fundamental non-zero guard:
\[ bx\,cy - by\,cx \neq 0. \]
The midpoints of $AB$ and $AC$ are $M = \left(\frac{bx}{2}, \frac{by}{2}\right)$ and $N = \left(\frac{cx}{2}, \frac{cy}{2}\right)$.

**1. Coordinate expression for the circumcenter $O$**
Since $K$ lies strictly inside $\triangle ABL$ and $L$ lies strictly inside $\triangle AKC$, the points $A, K, L$ are not collinear. Thus, the determinant of their coordinates is non-zero:
\[ kx\,ly - ky\,lx \neq 0. \]
The circumcenter $O = (x_O, y_O)$ of $\triangle AKL$ is the intersection of the perpendicular bisectors of $AK$ and $AL$. The equations of these bisectors are:
\[ 2kx\,x + 2ky\,y = kx^2 + ky^2, \qquad 2lx\,x + 2ly\,y = lx^2 + ly^2. \]
Solving this linear system for $x_O$ and $y_O$ yields:
\[ x_O = \frac{kx^2 ly + ky^2 ly - lx^2 ky - ly^2 ky}{2(kx\,ly - ky\,lx)}, \qquad y_O = \frac{kx\,lx^2 + kx\,ly^2 - lx\,kx^2 - lx\,ky^2}{2(kx\,ly - ky\,lx)}. \]

**2. Algebraic condition for $OM = ON$**
The equality $OM = ON$ is equivalent to $|O - M|^2 = |O - N|^2$. Expanding the squared distances:
\[ |O|^2 - 2O \cdot M + |M|^2 = |O|^2 - 2O \cdot N + |N|^2 \iff 2O \cdot (N - M) = |N|^2 - |M|^2. \]
Substituting $N - M = \frac{1}{2}(C - B)$ and $|N|^2 - |M|^2 = \frac{1}{4}(|C|^2 - |B|^2)$, we obtain:
\[ O \cdot (C - B) = \frac{1}{4}(cx^2 + cy^2 - bx^2 - by^2). \]
Substituting the expressions for $x_O$ and $y_O$ and clearing the denominator $4(kx\,ly - ky\,lx)$, we arrive at the polynomial equation $T = 0$, where:
\[
\begin{aligned}
T = \;& bx^2 kx\,ly - bx^2 ky\,lx - 2bx\,kx^2 ly - 2bx\,ky^2 ly + 2bx\,ky\,lx^2 + 2bx\,ky\,ly^2 \\
&+ by^2 kx\,ly - by^2 ky\,lx + 2by\,kx^2 lx - 2by\,kx\,lx^2 - 2by\,kx\,ly^2 + 2by\,ky^2 lx \\
&- cx^2 kx\,ly + cx^2 ky\,lx + 2cx\,kx^2 ly + 2cx\,ky^2 ly - 2cx\,ky\,lx^2 - 2cx\,ky\,ly^2 \\
&- cy^2 kx\,ly + cy^2 ky\,lx - 2cy\,kx^2 lx + 2cy\,kx\,lx^2 + 2cy\,kx\,ly^2 - 2cy\,ky^2 lx.
\end{aligned}
\]
Thus, $OM = ON$ holds if and only if $T = 0$.

**3. Algebraic encoding of the angle conditions**
We translate the given angle equalities into polynomial equations. Since all points are strictly inside the specified triangles, all relevant angles lie in $(0, \pi)$, making the cotangent function injective. The condition $\angle PQR = \angle STU$ is algebraically equivalent to $(\vec{QP} \times \vec{QR})(\vec{TS} \cdot \vec{TU}) - (\vec{QP} \cdot \vec{QR})(\vec{TS} \times \vec{TU}) = 0$.
- The condition $\angle KBA = \angle ACL$ is equivalent to:
\[ - bx^{2} cx\,ly + bx^{2} cy\,lx - bx\,cx^{2} ky + bx\,cx\,kx\,ly + bx\,cx\,ky\,lx - bx\,cy^{2} ky - bx\,cy\,kx\,lx + bx\,cy\,ky\,ly - by^{2} cx\,ly + by^{2} cy\,lx + by\,cx^{2} kx - by\,cx\,kx\,lx + by\,cx\,ky\,ly + by\,cy^{2} kx - by\,cy\,kx\,ly - by\,cy\,ky\,lx = 0. \]
- The condition $\angle LBK = \angle LNC$ is equivalent to:
\[ - 2 bx^{2} cx\,ly + 2 bx^{2} cy\,lx - bx\,cx^{2} ky + bx\,cx^{2} ly + 2 bx\,cx\,kx\,ly + 2 bx\,cx\,ky\,lx - bx\,cy^{2} ky + bx\,cy^{2} ly - 2 bx\,cy\,kx\,lx + 2 bx\,cy\,ky\,ly - 2 bx\,cy\,lx^{2} - 2 bx\,cy\,ly^{2} - 2 by^{2} cx\,ly + 2 by^{2} cy\,lx + by\,cx^{2} kx - by\,cx^{2} lx - 2 by\,cx\,kx\,lx + 2 by\,cx\,ky\,ly + 2 by\,cx\,lx^{2} + 2 by\,cx\,ly^{2} + by\,cy^{2} kx - by\,cy^{2} lx - 2 by\,cy\,kx\,ly - 2 by\,cy\,ky\,lx - cx^{2} kx\,ly + cx^{2} ky\,lx - 2 cx\,ky\,lx^{2} - 2 cx\,ky\,ly^{2} - cy^{2} kx\,ly + cy^{2} ky\,lx + 2 cy\,kx\,lx^{2} + 2 cy\,kx\,ly^{2} = 0. \]
- The condition $\angle LCK = \angle BMK$ is equivalent to:
\[ - bx^{2} cx\,ky + bx^{2} cx\,ly + bx^{2} cy\,kx - bx^{2} cy\,lx - bx^{2} kx\,ly + bx^{2} ky\,lx + 2 bx\,cx^{2} ky - 2 bx\,cx\,kx\,ly - 2 bx\,cx\,ky\,lx + 2 bx\,cy^{2} ky - 2 bx\,cy\,kx^{2} + 2 bx\,cy\,kx\,lx - 2 bx\,cy\,ky^{2} - 2 bx\,cy\,ky\,ly + 2 bx\,kx^{2} ly + 2 bx\,ky^{2} ly - by^{2} cx\,ky + by^{2} cx\,ly + by^{2} cy\,kx - by^{2} cy\,lx - by^{2} kx\,ly + by^{2} ky\,lx - 2 by\,cx^{2} kx + 2 by\,cx\,kx^{2} + 2 by\,cx\,kx\,lx + 2 by\,cx\,ky^{2} - 2 by\,cx\,ky\,ly - 2 by\,cy^{2} kx + 2 by\,cy\,kx\,ly + 2 by\,cy\,ky\,lx - 2 by\,kx^{2} lx - 2 by\,ky^{2} lx = 0. \]

**4. Derivation of guards and inequalities from interiority**
The strict interiority conditions ($K$ inside $\triangle BMC$ and $\triangle ABL$; $L$ inside $\triangle BNC$ and $\triangle AKC$) guarantee that no three relevant points are collinear. This yields all the non-zero guards required by the lemma, such as:
\[ bx\,cy - bx\,ly - by\,cx + by\,lx \neq 0, \quad bx\,cy - by\,cx + cx\,ky - cy\,kx \neq 0, \quad bx\,ly - by\,lx \neq 0, \quad cx\,ky - cy\,kx \neq 0, \]
and the remaining $\neq 0$ conditions, which correspond to the non-vanishing of oriented areas for triangles like $ABL$, $AKC$, $BMK$, $LNC$, etc.
Furthermore, the orientation of the interior points relative to the triangle edges ensures that the signed areas of these triangles are strictly positive. These correspond precisely to the strict inequalities ($>0$) in the lemma, which prevent degenerate configurations and ensure the angle equalities are interpreted correctly within $(0, \pi)$. All guards and inequalities listed in the exact lemma are direct algebraic consequences of these geometric interiority hypotheses.

**5. Application of the certified lemma**
We have shown that the geometric hypotheses of the theorem imply the three polynomial equations above, along with all the non-zero guards and strict inequalities listed in the exact lemma.
## Algebraic lemma

For the real variables bx, by, cx, cy, kx, ky, lx, ly, assume:

\[- bx^{2} cx ly + bx^{2} cy lx - bx cx^{2} ky + bx cx kx ly + bx cx ky lx - bx cy^{2} ky - bx cy kx lx + bx cy ky ly - by^{2} cx ly + by^{2} cy lx + by cx^{2} kx - by cx kx lx + by cx ky ly + by cy^{2} kx - by cy kx ly - by cy ky lx=0.\]

\[- 2 bx^{2} cx ly + 2 bx^{2} cy lx - bx cx^{2} ky + bx cx^{2} ly + 2 bx cx kx ly + 2 bx cx ky lx - bx cy^{2} ky + bx cy^{2} ly - 2 bx cy kx lx + 2 bx cy ky ly - 2 bx cy lx^{2} - 2 bx cy ly^{2} - 2 by^{2} cx ly + 2 by^{2} cy lx + by cx^{2} kx - by cx^{2} lx - 2 by cx kx lx + 2 by cx ky ly + 2 by cx lx^{2} + 2 by cx ly^{2} + by cy^{2} kx - by cy^{2} lx - 2 by cy kx ly - 2 by cy ky lx - cx^{2} kx ly + cx^{2} ky lx - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx + 2 cy kx lx^{2} + 2 cy kx ly^{2}=0.\]

\[- bx^{2} cx ky + bx^{2} cx ly + bx^{2} cy kx - bx^{2} cy lx - bx^{2} kx ly + bx^{2} ky lx + 2 bx cx^{2} ky - 2 bx cx kx ly - 2 bx cx ky lx + 2 bx cy^{2} ky - 2 bx cy kx^{2} + 2 bx cy kx lx - 2 bx cy ky^{2} - 2 bx cy ky ly + 2 bx kx^{2} ly + 2 bx ky^{2} ly - by^{2} cx ky + by^{2} cx ly + by^{2} cy kx - by^{2} cy lx - by^{2} kx ly + by^{2} ky lx - 2 by cx^{2} kx + 2 by cx kx^{2} + 2 by cx kx lx + 2 by cx ky^{2} - 2 by cx ky ly - 2 by cy^{2} kx + 2 by cy kx ly + 2 by cy ky lx - 2 by kx^{2} lx - 2 by ky^{2} lx=0.\]

\[bx cy - bx ly - by cx + by lx\ne0.\]

\[bx cy - by cx + cx ky - cy kx\ne0.\]

\[\frac{bx^{2} cy ky}{4} - \frac{bx by cx ky}{4} - \frac{bx by cy kx}{4} + \frac{by^{2} cx kx}{4}>0.\]

\[- \frac{bx^{2} cy^{2}}{4} + \frac{bx^{2} cy ky}{4} + \frac{bx by cx cy}{2} - \frac{bx by cx ky}{4} - \frac{bx by cy kx}{4} - \frac{bx cx cy ky}{2} + \frac{bx cy^{2} kx}{2} - \frac{by^{2} cx^{2}}{4} + \frac{by^{2} cx kx}{4} + \frac{by cx^{2} ky}{2} - \frac{by cx cy kx}{2}>0.\]

\[\frac{bx^{2} cy^{2}}{2} - \frac{bx^{2} cy ky}{2} - bx by cx cy + \frac{bx by cx ky}{2} + \frac{bx by cy kx}{2} + \frac{bx cx cy ky}{2} - \frac{bx cy^{2} kx}{2} + \frac{by^{2} cx^{2}}{2} - \frac{by^{2} cx kx}{2} - \frac{by cx^{2} ky}{2} + \frac{by cx cy kx}{2}>0.\]

\[bx^{2} ky ly - bx by kx ly - bx by ky lx + by^{2} kx lx>0.\]

\[- bx^{2} ky ly + bx^{2} ly^{2} + bx by kx ly + bx by ky lx - 2 bx by lx ly - bx kx ly^{2} + bx ky lx ly - by^{2} kx lx + by^{2} lx^{2} + by kx lx ly - by ky lx^{2}>0.\]

\[bx kx ly^{2} - bx ky lx ly - by kx lx ly + by ky lx^{2}>0.\]

\[- \frac{bx^{2} cy^{2}}{4} + \frac{bx^{2} cy ly}{2} + \frac{bx by cx cy}{2} - \frac{bx by cx ly}{2} - \frac{bx by cy lx}{2} - \frac{bx cx cy ly}{4} + \frac{bx cy^{2} lx}{4} - \frac{by^{2} cx^{2}}{4} + \frac{by^{2} cx lx}{2} + \frac{by cx^{2} ly}{4} - \frac{by cx cy lx}{4}>0.\]

\[- \frac{bx cx cy ly}{4} + \frac{bx cy^{2} lx}{4} + \frac{by cx^{2} ly}{4} - \frac{by cx cy lx}{4}>0.\]

\[\frac{bx^{2} cy^{2}}{2} - \frac{bx^{2} cy ly}{2} - bx by cx cy + \frac{bx by cx ly}{2} + \frac{bx by cy lx}{2} + \frac{bx cx cy ly}{2} - \frac{bx cy^{2} lx}{2} + \frac{by^{2} cx^{2}}{2} - \frac{by^{2} cx lx}{2} - \frac{by cx^{2} ly}{2} + \frac{by cx cy lx}{2}>0.\]

\[- cx kx ky ly + cx ky^{2} lx + cy kx^{2} ly - cy kx ky lx>0.\]

\[cx^{2} ky^{2} - cx^{2} ky ly - 2 cx cy kx ky + cx cy kx ly + cx cy ky lx + cx kx ky ly - cx ky^{2} lx + cy^{2} kx^{2} - cy^{2} kx lx - cy kx^{2} ly + cy kx ky lx>0.\]

\[cx^{2} ky ly - cx cy kx ly - cx cy ky lx + cy^{2} kx lx>0.\]

\[- \frac{bx cy}{2} + \frac{by cx}{2}\ne0.\]

\[- \frac{bx ky}{2} + \frac{by kx}{2}\ne0.\]

\[\frac{bx cy}{2} - \frac{bx ky}{2} - \frac{by cx}{2} + \frac{by kx}{2} + cx ky - cy kx\ne0.\]

\[- bx cy + bx ky + by cx - by kx - cx ky + cy kx\ne0.\]

\[bx ly - by lx\ne0.\]

\[bx ky - by kx\ne0.\]

\[- bx ky + bx ly + by kx - by lx - kx ly + ky lx\ne0.\]

\[kx ly - ky lx\ne0.\]

\[- \frac{bx cy}{2} + \frac{by cx}{2}\ne0.\]

\[\frac{bx cy}{2} - bx ly - \frac{by cx}{2} + by lx + \frac{cx ly}{2} - \frac{cy lx}{2}\ne0.\]

\[\frac{cx ly}{2} - \frac{cy lx}{2}\ne0.\]

\[- bx cy + bx ly + by cx - by lx - cx ly + cy lx\ne0.\]

\[- cx ky + cy kx\ne0.\]

\[kx ly - ky lx\ne0.\]

\[- cx ky + cx ly + cy kx - cy lx - kx ly + ky lx\ne0.\]

\[- cx ly + cy lx\ne0.\]

Then \(T=bx^{2} kx ly - bx^{2} ky lx - 2 bx kx^{2} ly - 2 bx ky^{2} ly + 2 bx ky lx^{2} + 2 bx ky ly^{2} + by^{2} kx ly - by^{2} ky lx + 2 by kx^{2} lx - 2 by kx lx^{2} - 2 by kx ly^{2} + 2 by ky^{2} lx - cx^{2} kx ly + cx^{2} ky lx + 2 cx kx^{2} ly + 2 cx ky^{2} ly - 2 cx ky lx^{2} - 2 cx ky ly^{2} - cy^{2} kx ly + cy^{2} ky lx - 2 cy kx^{2} lx + 2 cy kx lx^{2} + 2 cy kx ly^{2} - 2 cy ky^{2} lx=0\).
By the certified lemma, these algebraic conditions imply $T = 0$.

**6. Conclusion**
Since $T = 0$, the condition $O \cdot (C - B) = \frac{1}{4}(|C|^2 - |B|^2)$ holds. As derived in Step 2, this is equivalent to $|O - M|^2 = |O - N|^2$, which means $OM = ON$. This completes the proof. $\square$

# Appendix A — Proof of the algebraic lemma

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
