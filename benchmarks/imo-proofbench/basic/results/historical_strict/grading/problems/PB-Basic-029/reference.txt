Let $\ell$ be the nearest to $O$ line from $L$ and $\ell\cap I=\left\{ X_{1},X_{2},...,X_{n-1}\right\} $
 with $|OX_{i}|\leq|OX_{i+1}|$ for every $i.$

 Claim. Open segment $OX_{i}$ intersects at most $i-1$ line from
 $S$.

 Proof. Suppose the contrary, so $OX_{i}$ intersects $i$ lines and
 in particular it intersects line $\ell'$ such that $Y=\ell\cap\ell'\notin\bigcup_{t=1}^{i-1}\{X_{t}\}.$
 If $Z=OX_{i}\cap\ell'$ we get the contradiction with
 \[
 |OY|\geq|OX_{i}|\implies\angle OYX_{i}<90^{\circ}\implies d(O,\ell')=|OY|\cdot\sin\angle OYZ<|OY|\cdot\sin\angle OYX_{i}=d(O,\ell)\text{ }\Box
 \]
 Now with fixed $n$ we apply induction by $p.$ By the claim $X_{1}$
 is always red, so the base case $p=0$ follows. Now consider problem
 statement for $S\backslash\ell$ and $p=k,$ so there exist at least
 $C_{p+2}^{2}$ red points. After backing $\ell$ to $L$ and increasing
 $p$ to $p+1$ all red points are preserved and by claim all points
 $X_{1},X_{2},...,X_{p+2}$ are red, so totally there are at least
 $C_{p+3}^{2}$ red points.

 For the example construction, we take $X=(-1,-1)$ and $n$ lines
 to be the lines connecting $(0,n-1-i)$ and $(i,0)$ for $0\le i\le n-1$.
