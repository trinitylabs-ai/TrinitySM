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