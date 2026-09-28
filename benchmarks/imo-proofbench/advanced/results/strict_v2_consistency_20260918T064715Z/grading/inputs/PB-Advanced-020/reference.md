To begin with, we can change the expression in the problem to
 $\gcd \left( x^n +y , \, (y-x)\left(\sum_{i=0}^{n-1} y^i x^{n-i-1} - 1\right) \right) = \gcd \left( x^n +y , \, y^n - x^n -(y-x) \right) = \gcd(x^n +y , y^n +x)$.
 Let the limit of the sequence $(a_n)$ exist and be equal to $g$. Then, for sufficiently large $n$,

 Lemma. If the limit of $a_n$ as $n \to \infty$ exists and is equal to $g$, then $g$ divides $2 \gcd(x, y)$.

 Proof. For sufficiently large $n$, we have $a_n = \gcd \left( x^n +y , \, y^n +x \right) = g$.
 This implies that $g$ divides $x^n + y$ and $g$ divides $y^n +x$ for all $n \ge N$, for some positive integer $N$.

 Consider $n \ge N$. We have $x^n + y \equiv 0 \pmod{g}$ and $x^{n+1} + y \equiv 0 \pmod{g}$.
 Multiplying the first congruence by $x$, we get $x^{n+1} + xy \equiv 0 \pmod{g}$.
 Subtracting the second congruence from this, we have $(x^{n+1} + xy) - (x^{n+1} + y) \equiv 0 - 0 \pmod{g}$, which simplifies to $xy - y = y(x-1) \equiv 0 \pmod{g}$.

 Analogously, $x(y-1)$ is divisible by $g$.
 Their difference $x-y$ is then divisible by $g$, so $g$ also divides
 $x(y-1)+x(x-y)=x^2 -x$. All powers of $x$ are then congruent modulo
 $g$, so $x+y\equiv x^{N}+y\equiv0(\bmod g)$. Then $2x=(x+y)+(x-y)$
 and $2y=(x+y)-(x-y)$ are both divisible by $g$, so $g\mid2\operatorname{gcd}(x,y)$.
 On the other hand, it is clear that $\operatorname{gcd}(x,y)\mid g$,
 thus proving the Lemma.

 Let $d=\operatorname{gcd}(x,y)$, and write $x=da$ and $y=db$ for
 coprime positive integers $a$ and $b$. We have that

 \[
 \operatorname{gcd}\left((da)^{n}+db,(db)^{n}+da\right)=d\operatorname{gcd}\left(d^{n-1}a^{n}+b,d^{n-1}b^{n}+a\right)
 \]

 so the Lemma tells us that

 \[
 \operatorname{gcd}\left(d^{n-1}a^{n}+b,d^{n-1}b^{n}+a\right)\leqslant2
 \]

 for all $n\geqslant N$. Defining $K=d^{2}ab+1$, note that $K$ is
 coprime to each of $d,a$, and $b$. By Euler's theorem, for $n\equiv-1(\bmod\varphi(K))$
 we have that

 \[
 d^{n-1}a^{n}+b\equiv d^{-2}a^{-1}+b\equiv d^{-2}a^{-1}\left(1+d^{2}ab\right)\equiv 0\quad(\bmod K)
 \]

 so $K\mid d^{n-1}a^{n}+b$. Analogously, we have that $K\mid d^{n-1}b^{n}+a$.
 Taking such an $n$ which also satisfies $n\geqslant N$ gives us
 that

 \[
 K\mid\operatorname{gcd}\left(d^{n-1}a^{n}+b,d^{n-1}b^{n}+a\right)\leqslant2
 \]

 This is only possible when $d=a=b=1$, which yields the only solution
 $(x,y)=(1,1)$. Therefore, the only solution is $(x,y)=(1,1)$.