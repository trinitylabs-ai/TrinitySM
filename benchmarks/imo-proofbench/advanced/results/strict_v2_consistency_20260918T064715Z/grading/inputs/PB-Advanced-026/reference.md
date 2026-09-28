Let $n>k\geq1$ be integers. Let $P(x)\in\mathbb{R}[x]$ be a polynomial
 of degree $n$ with no repeated roots and $P(0)\neq0$. Suppose that
 for any real numbers $a_{0},\ldots,a_{k}$ such that the polynomial
 $a_{k}x^{k}+\cdots+a_{1}x+a_{0}$ divides $P(x)$, the product $a_{0}a_{1}\ldots a_{k}$
 is zero. Prove that $P(x)$ has a non-real root.


 By considering any $k+1$ of the roots of $P$, we may as well assume
 WLOG that $n=k+1$. Suppose that $P(x)=\left(x+r_{1}\right)\ldots\left(x+r_{n}\right)\in\mathbb{R}[x]$
 has $P(0)\neq0$. Then the problem hypothesis is that each of the
 $n$ polynomials (of degree $n-1$ ) given by

 \[
 \begin{aligned}P_{1}(x) & =\left(x+r_{2}\right)\left(x+r_{3}\right)\left(x+r_{4}\right)\ldots\left(x+r_{n}\right)

 P_{2}(x) & =\left(x+r_{1}\right)\left(x+r_{3}\right)\left(x+r_{4}\right)\ldots\left(x+r_{n}\right)

 P_{3}(x) & =\left(x+r_{1}\right)\left(x+r_{2}\right)\left(x+r_{4}\right)\ldots\left(x+r_{n}\right)

  & \vdots

 P_{n}(x) & =\left(x+r_{1}\right)\left(x+r_{2}\right)\left(x+r_{3}\right)\ldots\left(x+r_{n-1}\right)
 \end{aligned}
 \]

 has at least one coefficient equal to zero. (Explicitly, $P_{i}(x)=\frac{P(x)}{x+r_{i}}$.)
 We'll prove that at least one $r_{i}$ is not real.


 Obviously the leading and constant coefficients of each $P_{i}$ are
 nonzero, and there are $n-2$ other coefficients to choose between.
 So by pigeonhole principle, we may assume, say, that $P_{1}$ and
 $P_{2}$ share the position of a zero coefficient, say the $x^{k}$
 one, for some $1\leq k<n-1$.


 \textbf{Claim 1. }If $P_{1}$ and $P_{2}$ both have $x^{k}$ coefficient
 equal to zero, then the polynomial

 \[
 Q(x)=\left(x+r_{3}\right)\left(x+r_{4}\right)\ldots\left(x+r_{n}\right)
 \]

 has two consecutive zero coefficients.


 \emph{Proof.} Suppose that

 \[
 Q(x)=x^{n-2}+b_{n-3}x^{n-3}+\cdots+b_{0}.
 \]

 (And let $b_{n-2}=1$. ) Then the fact that the $x^{k}$ coefficient
 of $P_{1}$ and $P_{2}$ are both zero means

 \[
 r_{1}b_{k}+b_{k-1}=r_{2}b_{k}+b_{k-1}=0
 \]

 and hence that $b_{k}=b_{k-1}=0$ (since the $r_{i}$ are distinct).



  To solve the problem, it suffices to prove:


 \textbf{Claim 2.} If $F(x)\in\mathbb{R}[x]$ is a polynomial with
 two consecutive zero coefficients, it cannot have all distinct real
 roots.


 \emph{Proof. }Say $x^{t}$ and $x^{t+1}$ coefficients of $F$ are
 both zero. Assume for contradiction all the roots of $F$ are real
 and distinct. Then by Rolle's theorem, every higher-order derivative
 of $F$ should have this property too. However, the $t$th order derivative
 of $F$ has a double root of $0$, contradiction.