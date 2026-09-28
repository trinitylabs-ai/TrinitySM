Let $P(x,y)$ be the assertion $f(x-f(xy))=f(x)f(1-y)$.

 If $f$ is constant, $f\equiv0$ or $f\equiv1$. From now on we will
 only consider non-constant functions.

 Claim 1 $f(f(x))=f(x)$ for all $x\in\mathbb{Z}$

 Proof. $P(0,y):f(-f(0))=f(0)f(1-y)\Longrightarrow f(0)=0$

 $P(x,0):f(x)=f(x)f(1)\Longrightarrow f(1)=1$

 $P(1,y):f(1-f(y))=f(1-y)$

 $P(1,1-y):f(1-f(1-y))=f(y)$

 $P(1,1-f(y)):f(y)=f(1-f(1-y))=f(1-f(1-f(y)))=f(f(y))\Longrightarrow f(f(x))=f(x)\forall x\in\mathbb{Z}\blacksquare$

 $\Longrightarrow P(x,1):f(x-f(x))=0$

 Now consider $f(\mathbb{Z})$.

 Case 1 $f(\mathbb{Z})\subset\{-1,0,1\}$

 Case 1.1. $f(\mathbb{Z})=\{0,1\}$

 We have $f(x)=1\textbackslash \Longrightarrow f(x-1)=0\textbackslash \Longrightarrow
 f(2-x)=1 \textbackslash \Longrightarrow f(1-x)=0$ and $f(1-x)=0
 \textbackslash \Longrightarrow f(x)=1$

 \[
 \therefore f(x)=1\Longleftrightarrow f(x-1)=0\Longleftrightarrow f(2-x)=1\Longleftrightarrow f(1-x)=0
 \]
 We can inductively prove that $f(x)=\begin{cases}
 0 & 2|x

 1 & 2\nmid x
 \end{cases}$

 Case 1.2. $f(\mathbb{Z})=\{-1,0,1\}\Longrightarrow f(-1)=-1$

 $P(1,x)$ and $P(-1,x)$ gives

 \begin{align*}
 f(x)=1 & \Longrightarrow f(1-x)=0,f(x+1)=-f(-2)

 f(x)=0 & \Longrightarrow f(1-x)=1,f(x+1)=1

 f(x)=-1 & \Longrightarrow f(1-x)=f(2),f(x+1)=0
 \end{align*}
 It's easy to see that $f(-2)=1,f(2)=-1$, and using this, we can inductively
 prove that $f(x)=\begin{cases}
 0 & 3|x

 1 & 3|x-1

 -1 & 3|x+1
 \end{cases}$

 Case 2. $f(\mathbb{Z})$ is not a subset of $\{-1,0,1\}$

 Case 2.1 $f(t)=1$ for some $2\mid t$

 \[
 P(2,\frac{t}{2}):1=f(1)=f(2)f(1-\frac{t}{2})
 \]

 Case 2.1.1 : $f(2)=1\Longrightarrow P(2,1):1=f(2)f(0)=0$. Contradiction!

 Case 2.1.2 : $f(2)=-1\Longrightarrow f(-1)=-1,f(1-\frac{t}{2})=-1$

 $P(-1,-x):f(-1-f(x))=-f(1+x)$

 $P(-1,-f(x)):f(-1-f(x))=f(-1-f(f(x)))=-f(1+f(x))\Longrightarrow f(1+x)=f(1+f(x))...(*)$

 Since $f(2)=-1$, so plugging this in $(*)$, we have

 \[
 f(2)=-1\Longrightarrow f(3)=0\Longrightarrow f(4)=1\Longrightarrow f(5)=-1\cdots
 \]
 We can prove inductively that$f(x)=\begin{cases}
 0 & 3|x

 1 & 3|x-1

 -1 & 3|x+1
 \end{cases}$ for all $x\in\mathbb{N}$.

 Plugging in $x=-1,y=-n(n\in\mathbb{N})$ gives $f(-1-n)=f(-1-f(n))=-f(1+n)$,
 so we have $f(x)=\begin{cases}
 0 & 3|x

 1 & 3|x-1

 -1 & 3|x+1
 \end{cases}$for all $x$, so contradiction since $f(\mathbb{Z})\in\{-1,0,1\}$.

 Case 2.2 $f(t)=1\Longrightarrow2\nmid t$

 Claim 2 $f(-1)=-1$ or $f(2)=0$

 Proof. Assume that $f(2)\neq0$

 We will prove that $f(t)=1\Longrightarrow f(1-t)=0$. $P(2,\frac{1-t}{2})$
 gives

 \[
 f(2)=f(2)f(\frac{t-3}{2})\Longrightarrow f(\frac{t-3}{2})=1
 \]
 We repeat this, then we get $t\equiv1(mod2^{n})$ for all $n\Longrightarrow t=1$.
 Note that

 \[
 f(-1)=c\Longrightarrow f(-1-c)=0\Longrightarrow f(c+2)=1
 \]
 Hence we conclude that $c=-1$.

 Case 2.2.1. $f(2)=0\Longrightarrow f(-1)=1$

 Define $n$ as the element of $f(\mathbb{Z})-\{-1,0,1\}$ which has
 the smallest absolute value. Then we have

 \[
 f(x-f(xy))=n\Longrightarrow\{f(x),f(1-y)\}=\{1,n\}\text{ or }\{f(x),f(1-y)\}=\{-1,-n\}...(\star)
 \]
 . Also note that $P(-n,- 1):f(-n-f(n))=0$, where $f(n)=n$ by Claim 1. Thus by $x=n,y=-2$ $(\star)\Longrightarrow f(3)=1$.
 Case 2.2.1. now becomes a repetition of Case 1.1, so contradiction!

 Case 2.2.2. $f(2)\neq0,f(-1)=-1,f(-2)=-f(2)$

 Claim 3 $f(n)=t\Longrightarrow n=t\forall t\leq1$

 Proof. We use induction on $t$. $t=1$ is already proven above. Assume
 that $t$ works.

 If $f(n)=t-1\Longrightarrow f(1+n)=f(1+f(n))=f(t)\Longrightarrow n=t-1$,
 so we're done.

 Use the same method to prove that $f(n)=n\forall n\leq1$, and $P(-1,n)(n>0)$
 gives $f(n+1)=-f(-n-1)=n+1$, so $f(n)=n$ for all $n\in\mathbb{Z}$.