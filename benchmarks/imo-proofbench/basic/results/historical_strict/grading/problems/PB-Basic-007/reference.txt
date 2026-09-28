$n=2$ with $\left(a_{0}, a_{1}, a_{2}\right)=(-1,1,3)$.

 We provide a solution when we relax the condition $a_n=3$. When we add back the condition, the only solution is $n=2$ with $\left(a_{0}, a_{1}, a_{2}\right)=(-1,1,3)$.

 When relaxing the condition $a_n=3$, the short answers are $n=1$ with $\left(a_{0}, a_{1}\right)=(2,-2) ; n=2$ with $\left(a_{0}, a_{1}, a_{2}\right)=(-1,1,3)$; or $n$ even with $a_{0}=\cdots=a_{n}=-1$.

 It is clear that $a_{0} \neq 0$ as otherwise $a_{n}=0$. For any $k=1, \ldots, n+1$, let $I_{k}$ be the convex hull of $0, a_{0}, \ldots, a_{k-1}$. We will define $a_{-1}=0$ for convenience.

 We first show that $a_{k}$ is not in the interior of $I_{k}$. Otherwise, let $i, j \in\{-1,0, \ldots, k-$ $1\}$ be such that $a_{i}, a_{j}$ are the endpoints of $I_{k}$. Then as $a_{i}-a_{j} \mid f\left(a_{i}\right)-f\left(a_{j}\right)=$ $a_{i+1}-a_{j+1}$, we know that $a_{i+1}$ and $a_{j+1}$ are also the endpoints of $I_{k}$, and by continuing this argument we eventually get that $a_{k}$ is an endpoint of $I_{k}$, which is a contradiction. A consequence is that the endpoints of $I_{k}$ are $a_{k-2}$ and $a_{k-1}$ unless $a_{k-2}=a_{k-1}$. Now if $a_{i}=0$ for some $i>0$, then it is clear that the nonzero terms of $a_{0}, \ldots, a_{n}$ all have the same sign. Then $f\left(a_{i-1}\right)=0$ gives a contradiction if we take $i$ to be the smallest index with $a_{i}=0$.

 We first assume that $a_{n} \neq a_{0}$. If $\left|a_{i}\right|<2$ for any $i<n$, then we have several possibilities: either $n \leqslant 2$; or $a_{0}, \ldots, a_{n}=-1,1, \ldots,-1,1$, or $a_{0}, \ldots, a_{n}=1,-1, \ldots, 1,-1$, or $a_{0}, \ldots, a_{n}=-1,1,1, \ldots, 1$, or $a_{0}, \ldots, a_{n}=1,-1, \ldots,-1$, for $n>2$. It is easy to verify that the last four cases cannot occur by evaluating $f(1)$. Therefore we have $n=2, a_{0}=-a_{1} \in\{1,-1\}$, or $n=1, a_{0}= \pm 1$. In the first case, we have $a_{2}-a_{1}=f\left(a_{1}\right)-f\left(a_{0}\right)=2 a_{1}^{2}=2$ and so $a_{2}=a_{1}+2$. Therefore $a_{1}=f\left(a_{0}\right)=$ $\left(a_{0}+a_{1}+2\right)+a_{0} a_{1}=2-1=1$, and we get the solution $a_{0}, a_{1}, a_{2}=-1,1,3$. In the second case, we have $a_{1}=f\left(a_{0}\right)= \pm a_{1} \pm 1$, and we get no solution by parity.

 Now if $a_{n} \neq a_{0}$ and $a_{n}$ has the largest absolute value, pick $i<n$ such that $\left|a_{i}\right| \geqslant 2$. Then

 \[
 \left|f\left(a_{i}\right)\right| \geqslant\left|a_{n}\right|\left(\left|a_{i}\right|^{n}-\left|a_{i}\right|^{n-1}-\cdots-1\right) \geqslant\left|a_{n}\right|,
 \]

 and $\left|f\left(a_{i}\right)\right|=\left|a_{i+1}\right|\left|a_{n}\right|$. Therefore all equalities should hold, and we get $a_{0}=\cdots=$ $a_{n-1}=-a_{n}$ and $\left|a_{i}\right|=2$. Note that if $n \geqslant 2$, then $a_{0}=a_{1}$, which shows that

 $a_{0}=\cdots=a_{n}$, which is a contradiction. Therefore $n=1$ and we get $\left(a_{0}, a_{1}\right)=(2,-2)$ or $(-2,2)$. The latter is not a solution, so we get $a_{0}=2$ and $a_{1}=-2$.

 So now in the case that $a_{n} \neq a_{0}$, we may assume that $a_{n}$ does not have the largest absolute value. Let $a_{k}$ be the least index such that $a_{k}=a_{k+1}=\cdots=a_{n}$. Then we must have $\left|a_{k-1}\right|>\left|a_{k}\right|$ as $a_{k-1}$ and $a_{k}$ are the endpoints of $I_{k-1}$. We know that $a_{0} \mid a_{k-1}$ and $a_{0} \mid a_{k}$, and so $\left|a_{k-1}\right| \geqslant\left|a_{k}\right|+\left|a_{0}\right|$. As $a_{k-1} \mid f\left(a_{k-1}\right)-f(0)=a_{k}-a_{0}$, we have $\left|a_{k-1}\right| \leqslant\left|a_{k}-a_{0}\right|$ since $a_{k} \neq a_{0}$. This shows that $\left|a_{k}-a_{0}\right|=\left|a_{k}\right|+\left|a_{0}\right|=\left|a_{k-1}\right|$. As a consequence, we have $\left|a_{i}\right| \leqslant\left|a_{k}\right|+\left|a_{0}\right|$ for any $i$. Now we have

 \[
 \left|a_{k}\right|=\left|f\left(a_{k-1}\right)\right| \geqslant\left|a_{k}\right|\left(\left|a_{k-1}\right|^{n}-\left|a_{k-1}\right|^{n-1}-\cdots-1\right)-\left|a_{0}\right|\left(\left|a_{k-1}\right|^{n-1}+\cdots+1\right) .
 \]

 Hence

 \[
 \frac{\left|a_{k}\right|}{\left|a_{0}\right|} \leqslant \frac{\left|a_{k-1}\right|^{n-1}+\cdots+1}{\left|a_{k-1}\right|^{n}-\left|a_{k-1}\right|^{n-1}-\cdots-1} .
 \]

 Note that $\left|a_{k}\right| /\left|a_{0}\right|$ is a positive integer. If it is greater than 1 , then as $\left|a_{k-1}\right|=$ $\left|a_{k}\right|+\left|a_{0}\right| \geqslant 3$, we have

 \[
 \frac{\left|a_{k-1}\right|^{n-1}+\cdots+1}{\left|a_{k-1}\right|^{n}-\left|a_{k-1}\right|^{n-1}-\cdots-1} \leqslant \frac{3^{n-1}+\cdots+1}{3^{n}-3^{n-1}-\cdots-1}<1
 \]

 which is a contradiction. Therefore $\left|a_{k}\right|=\left|a_{0}\right|$, and so $a_{k}=-a_{0}$. This also shows that $a_{k-1}=2 a_{0}$, and by the inequality we see that $\left|a_{0}\right|=1$. With these constraints, we know that $a_{0}, \ldots, a_{n} \in\left\{a_{0},-a_{0}, 2 a_{0}\right\}$. By enumerating, we only have the possibilities $a_{0}, \ldots, a_{n}= \pm 1, \pm 2, \mp 1, \pm 2, \mp 1, \ldots, \pm 2, \mp 1$, or $a_{0}, \ldots, a_{n}= \pm 1, \mp 1, \pm 2, \mp 1, \ldots, \pm 2, \mp 1$, or $a_{0}, \ldots, a_{n}= \pm 1, \pm 2, \mp 1, \ldots, \mp 1$. For the first case, we have $n=2 t$ adn $2 a_{0}=a_{1}=$ $f\left(a_{0}\right)=-(t-1) a_{0}+2 t$, showing that $t=1, a_{0}=1$, and by plugging in $a_{1}$ we get a contradiction. For the second case, we have $n=2 t+1$ and $-a_{0}=a_{1}=f\left(a_{0}\right)=$ $(2 t+1) a_{0}-(t+1)$, which has no solutions. For the third case, if $a_{0}=1$ then we get $n=2$ and $a_{0}, a_{1}, a_{2}=1,2,-1$ by the equation $a_{1}=f\left(a_{0}\right)$, which is not a solution. Thus $a_{0}=-1$, and by plugging in $a_{0}$ we also get a contradiction.

 The remaining case is $a_{n}=a_{0}$. If $a_{n}=a_{n-1}$, then we must have $a_{0}=\cdots=a_{n}$. By plugging in $a_{0}$ we have $a_{0}^{n+1}+\cdots+a_{0}^{2}=0$, and so $a_{0}=-1$ and $n$ is even. Now assume that $a_{n} \neq a_{n-1}$. Then $a_{n}, a_{n-1}$ are the endpoints of $I_{n+1}$. Note that if $a_{n-2}=a_{n-1}$

 then $a_{n}=a_{n-1}$, which is a contradiction. Therefore $a_{n-2}, a_{n-1}$ are also endpoints of $I_{n+1}$. By induction we may show that $a_{k}, a_{k-1}$ are the endpoints of $I_{k+1}$. As $a_{0} \neq 0$, we must have $a_{n}=a_{n-2}=\cdots=a_{0}$, and so $n$ is even. This shows that $a_{n-1}=\cdots=a_{1}$. Now we have

 \[
 a_{0}^{n+1}+a_{0}^{n-1} a_{1}+\cdots+a_{0}^{3}+a_{0} a_{1}+a_{0}=a_{1}
 \]

 and

 \[
 a_{0} a_{1}^{n}+a_{1}^{n}+\cdots+a_{0} a_{1}^{2}+a_{1}^{2}+a_{0}=a_{0}
 \]

 The latter can be rewritten as $\left(a_{0}+1\right)\left(a_{1}^{n-2}+a_{1}^{n-4}+\cdots+1\right)=0$. Therefore $a_{0}=-1$ or $a_{1}=-1$. If $a_{0}=-1$, then $-\left(a_{1}+1\right) n / 2-1=a_{1}$, or equivalently, $\left(a_{1}+1\right)(n+2)=0$. This shows that $a_{1}=-1$, which was already obtained above. If $a_{1}=-1$, then the first equation gives $a_{0}^{n+1}=-1$ and so $a_{0}=-1$ too.

 In conclusion, all the solutions are: $n=1$ with $\left(a_{0}, a_{1}\right)=(2,-2) ; n=2$ with $\left(a_{0}, a_{1}, a_{2}\right)=(-1,1,3)$; or $n$ even with $a_{0}=\cdots=a_{n}=-1$.
