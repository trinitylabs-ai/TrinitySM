We will prove this using induction. Note that $x_{2}=2^{6}+2=66$
 which is divisible by $x_{1}$ and $x_{3}=2^{66}+2=2(2^{65}+1)$,
 which is divisible by $2(2^{5}+1)=2^{6}+2=x_{2}$.


 For $a,b\in\mathbb{N}$, it is well known that $2^{a}+1|2^{ab}+1$
 and $2^{a}-1|2^{ab}-1$ if $2\not|b$.


 We will prove the result by induction. Note that $\nu_{2}(x_{i})=1$,
 so $\frac{x_{n-1}}{x_{n-2}}$ is odd. Also, note that $x_{1}|x_{2}$,
 as $2|6$, and $x_{2}|x_{3}$, as $6|66$.

 $x_{n}|x_{n+1}\Longleftrightarrow2^{x_{n-1}-1}+1|2^{x_{n}-1}+1\Longleftarrow x_{n-1}-1|x_{n}-1\Longleftrightarrow2^{x_{n-2}}+1|2^{x_{n-1}}+1\Longleftarrow x_{n-2}|x_{n-1}\text{ and that \ensuremath{\frac{x_{n-1}}{x_{n-2}}} is odd.}$
 Thus $x_{n-2}|x_{n-1}\implies x_{n}|x_{n+1}$, we can prove by induction
 that $x_{i}|x_{i+1}$ for all $i\in\mathbb{N}$.
