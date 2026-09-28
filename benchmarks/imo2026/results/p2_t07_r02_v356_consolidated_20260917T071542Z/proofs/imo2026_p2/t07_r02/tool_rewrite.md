**Proof:**

We establish a Cartesian coordinate system with $A$ at the origin $(0,0)$. Let the coordinates of the vertices and interior points be $B = (bx, by)$, $C = (cx, cy)$, $K = (kx, ky)$, and $L = (lx, ly)$. The midpoints of $AB$ and $AC$ are $M = (bx/2, by/2)$ and $N = (cx/2, cy/2)$, respectively.

Since $K$ lies strictly inside $\triangle ABL$ and $L$ lies strictly inside $\triangle AKC$, the points $A, K, L$ are not collinear. Consequently, the circumcenter $O = (x_O, y_O)$ of $\triangle AKL$ is well-defined. Using the standard formula for the circumcenter of points $(0,0)$, $(kx, ky)$, and $(lx, ly)$, we have:
\[
x_O = \frac{kx^2 ly + ky^2 ly - ky lx^2 - ky ly^2}{2(kx ly - ky lx)}, \quad y_O = \frac{-kx^2 lx + kx lx^2 + kx ly^2 - ky^2 lx}{2(kx ly - ky lx)}.
\]
The condition $OM = ON$ is equivalent to $OM^2 = ON^2$. Expanding the squared distances yields:
\[
\left(x_O - \frac{bx}{2}\right)^2 + \left(y_O - \frac{by}{2}\right)^2 = \left(x_O - \frac{cx}{2}\right)^2 + \left(y_O - \frac{cy}{2}\right)^2.
\]
Simplifying the quadratic terms cancels $x_O^2$ and $y_O^2$, leaving a linear expression in $x_O$ and $y_O$:
\[
x_O(cx - bx) + y_O(cy - by) + \frac{1}{4}(bx^2 + by^2 - cx^2 - cy^2) = 0.
\]
Substituting the rational expressions for $x_O$ and $y_O$ into this equation and multiplying by the non-zero denominator $4(kx ly - ky lx)$ clears the fractions. Expanding the resulting product explicitly yields the polynomial $T$:
\[
\begin{aligned}
T = \;& bx^2 kx ly - bx^2 ky lx - 2bx kx^2 ly - 2bx ky^2 ly + 2bx ky lx^2 + 2bx ky ly^2 \\
&+ by^2 kx ly - by^2 ky lx + 2by kx^2 lx - 2by kx lx^2 - 2by kx ly^2 + 2by ky^2 lx \\
&- cx^2 kx ly + cx^2 ky lx + 2cx kx^2 ly + 2cx ky^2 ly - 2cx ky lx^2 - 2cx ky ly^2 \\
&- cy^2 kx ly + cy^2 ky lx - 2cy kx^2 lx + 2cy kx lx^2 + 2cy kx ly^2 - 2cy ky^2 lx.
\end{aligned}
\]
Since $kx ly - ky lx \ne 0$ (guaranteed by the non-collinearity of $A, K, L$), the condition $OM = ON$ holds if and only if $T = 0$.

Next, we translate the geometric angle conditions into polynomial equations. The equality of two angles $\angle PQR = \angle STU$ is algebraically equivalent to the equality of their cotangents. Using the vector identity $\cot \angle PQR = \frac{\vec{QP} \cdot \vec{QR}}{\vec{QP} \times \vec{QR}}$ and clearing denominators, we derive the polynomial premises.

For $\angle KBA = \angle ACL$, the vectors are $\vec{BK} = (kx-bx, ky-by)$, $\vec{BA} = (-bx, -by)$, $\vec{CA} = (-cx, -cy)$, and $\vec{CL} = (lx-cx, ly-cy)$. Computing dot and cross products:
\[
\vec{BK} \cdot \vec{BA} = bx^2 + by^2 - bx kx - by ky, \quad \vec{BK} \times \vec{BA} = bx ky - by kx,
\]
\[
\vec{CA} \cdot \vec{CL} = cx^2 + cy^2 - cx lx - cy ly, \quad \vec{CA} \times \vec{CL} = cy lx - cx ly.
\]
Equating the cotangents $\frac{\vec{BK} \cdot \vec{BA}}{\vec{BK} \times \vec{BA}} = \frac{\vec{CA} \cdot \vec{CL}}{\vec{CA} \times \vec{CL}}$ and cross-multiplying gives:
\[
(bx^2 + by^2 - bx kx - by ky)(cy lx - cx ly) - (cx^2 + cy^2 - cx lx - cy ly)(bx ky - by kx) = 0.
\]
Expanding this product yields exactly the first polynomial equation in the lemma. Applying the identical algebraic procedure to $\angle LBK = \angle LNC$ and $\angle LCK = \angle BMK$ yields the second and third polynomial equations, respectively.

The strict interiority conditions for $K$ and $L$ guarantee that all relevant triangles are non-degenerate and that the points lie on the correct sides of the boundary lines. These geometric constraints imply the non-zero guards (e.g., $bx cy - by cx \ne 0$ for non-collinear $A,B,C$; $kx ly - ky lx \ne 0$ for non-collinear $A,K,L$; and various other determinants corresponding to the boundaries of $\triangle BMC, \triangle ABL, \triangle BNC, \triangle AKC$) and the strict polynomial inequalities listed in the lemma. Specifically, the oriented areas of the relevant triangles are positive, which corresponds exactly to the inequality premises.

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

By the certified algebraic lemma (Appendix A), under the three polynomial equations derived from the angle equalities, along with the non-zero guards and strict inequalities derived from the interiority conditions, the polynomial $T$ necessarily vanishes.

Therefore, $T = 0$. Since the denominator $4(kx ly - ky lx)$ is non-zero, this implies $OM^2 - ON^2 = 0$, and hence $OM = ON$. This completes the proof.

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
