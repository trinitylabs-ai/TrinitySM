Let the given condition be
 \[
 (P(b-P(a))+a-P(b))(P(a+P(b-P(a)))-b)=0\quad(*)
 \]
 for all $a,b\in\mathbb{Q}$. Let $y=b-P(a)$. Then $b=y+P(a)$. Substituting
 this into $(*)$, we get
 \[
 (P(y)+a-P(y+P(a)))(P(a+P(y))-(y+P(a)))=0.
 \]
 This must hold for all $a\in\mathbb{Q}$ and all $y$ in the image
 of $b\mapsto b-P(a)$. Since $b$ can be any rational number, $y$
 can be any rational number (assuming $P(a)\in\mathbb{Q}$). Thus,
 for all $a,y\in\mathbb{Q}$, we have
 \[
 P(y+P(a))=P(y)+a\quad\text{or}\quad P(a+P(y))=y+P(a).
 \]
 Let's rewrite this by swapping variable names $a\to y$ and $y\to x$:
 For all $x,y\in\mathbb{Q}$,
 \[
 P(x+P(y))=P(x)+y\quad\text{or}\quad P(P(x)+y)=x+P(y).\quad(**)
 \]
 We want to find the maximum possible number of elements in the set
 $S=\{P(a)+P(-a):a\in\mathbb{Q}\}$. Let $g(a)=P(a)+P(-a)$. We want
 to find the maximum possible size of the image of $g$.


 We begin by providing an example of a function $P$ for which there
 are two values of $g(a)$. We take the function $P(x)=2\lfloor x\rfloor-x=\lfloor x\rfloor-\{x\}$.
 First, we show that $P$ satisfies $(**)$. Given $x,y\in\mathbb{Q}$,
 writing $f$ instead of $P$: If $\{x\}<\{y\}$, then $f(f(x)+y)=x+f(y)$.
 This is the second case of $(**)$. If $\{x\}>\{y\}$, then $f(x+f(y))=f(x)+y$.
 This is the first case of $(**)$. If $\{x\}=\{y\}$, then $f(x)+y=x+f(y)=N$
 (an integer). $f(N)=N$. So $f(x+f(y))=f(N)=N=f(x)+y$ and $f(f(x)+y)=f(N)=N=x+f(y)$.
 Both cases of $(**)$ hold. In all cases, the relation $(**)$ is
 satisfied, which is equivalent to the original condition $(*)$.


 Finally, we compute $g(a)=P(a)+P(-a)$ for this function. $g(a)=(2\lfloor a\rfloor-a)+(2\lfloor-a\rfloor-(-a))=2(\lfloor a\rfloor+\lfloor-a\rfloor)$.
 If $a$ is an integer, $\lfloor a\rfloor=a$ and $\lfloor-a\rfloor=-a$,
 so $g(a)=2(a-a)=0$. If $a$ is not an integer, $\lfloor-a\rfloor=-\lfloor a\rfloor-1$,
 so $g(a)=2(\lfloor a\rfloor-\lfloor a\rfloor-1)=-2$. The set of values
 for $g(a)$ is $\{0,-2\}$. There are two values for $g(a)$.

 Now, we prove that there cannot be more than two values of $g(a).$
 Applying $(**)$ with $y=x$ tells us that $P(x+P(x))=P(x)+x$ or
 $P(P(x)+x)=x+P(x)$. In either case, if we let $z=x+P(x)$, then $P(z)=z$.
 So
 \[
 P(x+P(x))=x+P(x)\qquad\tag{(1)}
 \]
 for all $x\in\mathbb{Q}$.


 We begin with the following lemma.


 \textbf{Lemma 1.} $P$ is a bijection, and satisfies
 \[
 P(-P(-x))=x\qquad\tag{(2)}
 \]

 \emph{Proof.} We first prove that $P$ is injective. Suppose that
 $P(x_{1})=P(x_{2})=Y$. The condition $(**)$ applied to $(x_{1},x_{2})$
 gives $P(x_{1}+P(x_{2}))=P(x_{1})+x_{2}$ or $P(P(x_{1})+x_{2})=x_{1}+P(x_{2})$.
 Substituting $P(x_{1})=P(x_{2})=Y$, this becomes $P(x_{1}+Y)=Y+x_{2}$
 or $P(Y+x_{2})=x_{1}+Y$.

 From (1), we know $P(x_{1}+P(x_{1}))=x_{1}+P(x_{1})$, i.e., $P(x_{1}+Y)=x_{1}+Y$.
 Also from (1), $P(x_{2}+P(x_{2}))=x_{2}+P(x_{2})$, i.e., $P(x_{2}+Y)=x_{2}+Y$.

 Case A: $P(x_{1}+Y)=Y+x_{2}$ holds. Using $P(x_{1}+Y)=x_{1}+Y$,
 we get $x_{1}+Y=Y+x_{2}$, which implies $x_{1}=x_{2}$.

 Case B: $P(Y+x_{2})=x_{1}+Y$ holds. Using $P(x_{2}+Y)=x_{2}+Y$,
 we get $x_{2}+Y=x_{1}+Y$, which implies $x_{1}=x_{2}$.

 In both cases, $x_{1}=x_{2}$. So $P$ is injective.


 Now, (1) with $x=0$ tells us that $P(0+P(0))=0+P(0)$, so $P(P(0))=P(0)$.
 By injectivity, $P(0)=0$.

 Let $C(x,y)$: $P(x+P(y))=P(x)+y$ or $P(P(x)+y)=x+P(y)$.

 $C(x,-P(x))$: $P(x+P(-P(x)))=P(x)-P(x)=0$ or $P(P(x)-P(x))=x+P(-P(x))$.

 Case 1: $P(x+P(-P(x)))=0$. Since $P(0)=0$ and $P$ is injective,
 $x+P(-P(x))=0$, so $P(-P(x))=-x$.

 Case 2: $P(0)=x+P(-P(x))$. Since $P(0)=0$, this gives $0=x+P(-P(x))$,
 so $P(-P(x))=-x$.

 Both options yield $P(-P(x))=-x$. Replace $x$ with $-x$: $P(-P(-x))=-(-x)=x$.
 This proves (2).


 Finally, bijectivity follows immediately from (2). $P$ is injective.
 For any $y\in\mathbb{Q}$, let $x=-P(-y)$. Then $P(x)=P(-P(-y))=y$.
 So $P$ is surjective.


 Since $P$ is bijective, it has an inverse, which we denote $P^{-1}$.
 From (2), $P(-P(-x))=x$. Let $z=-P(-x)$. Then $P(z)=x$, so $z=P^{-1}(x)$.
 Thus, $P^{-1}(x)=-P(-x)$. Rearranging gives $P(-x)=-P^{-1}(x)$.
 We have $g(x)=P(x)+P(-x)=P(x)-P^{-1}(x)$.

 Suppose $g(x)=u$ and $g(y)=v$, where $u\neq v$ are both nonzero.
 Define $x^{\prime}=P^{-1}(x)$ and $y^{\prime}=P^{-1}(y)$. By definition,
 $P(x')=x$ and $P(y')=y$. We have $g(x)=P(x)-P^{-1}(x)=P(x)-x'=u$,
 so $P(x)=x'+u$. Similarly,
 \[
 g(y)=P(y)-P^{-1}(y)=P(y)-y'=v,
 \]
 so $P(y)=y'+v$.


 Apply $(**)$ to $(x',y)$:

 \[
 P(x'+P(y))=P(x')+y\text{ or }P(P(x')+y)=x'+P(y).
 \]
 $P(x'+y'+v)=x+y$ or $P(x+y)=x'+y'+v$. (Let $A=x+y,B=x'+y'+v$. $P(B)=A$
 or $P(A)=B$.)



  Apply $(**)$ to $(x,y')$:
 \[
 P(x+P(y'))=P(x)+y'\text{ or }P(P(x)+y')=x+P(y').
 \]
 $P(x+y)=P(x)+y'=(x'+u)+y'$ or $P(x'+u+y')=x+y$. (Let $C=x'+y'+u$.
 $P(A)=C$ or $P(C)=A$.)


 We have the possibilities:

 (1a) $P(B)=A$ and (2a) $P(A)=C$.

 (1a) $P(B)=A$ and (2b) $P(C)=A$. Since $P$ is injective, $B=C$,
 so $x'+y'+v=x'+y'+u$, which implies $u=v$. Contradiction.

 (1b) $P(A)=B$ and (2a) $P(A)=C$. Since $P(A)$ must be unique, $B=C$,
 which implies $u=v$. Contradiction.

 (1b) $P(A)=B$ and (2b) $P(C)=A$.

 So we must have either ($P(B)=A$ and $P(A)=C$) or ($P(A)=B$ and
 $P(C)=A$).


 Case 1: $P(x'+y'+v)=x+y$ and $P(x+y)=x'+y'+u$.

 Case 2: $P(x+y)=x'+y'+v$ and $P(x'+y'+u)=x+y$.


 Swapping $(x,u)$ with $(y,v)$ transforms Case 1 into Case 2 structure
 and vice versa. So, without loss of generality, assume Case 2 holds:
 $P(x+y)=x'+y'+v$ and $P(x'+y'+u)=x+y$.


 Now consider $(**)$ applied to $(x+y,-x'-u)$. Let $A=x+y$ and $Z=-x'-u$.
 Using $P(-z)=-P^{-1}(z)$, we have $P(-x'-u)=-P^{-1}(x'+u)$. From
 $P(x)=x'+u$ we have $x=P^{-1}(x'+u)$. Therefore, $P(Z)=P(-x'-u)=-x$.

 Now $C(A,Z)$ gives: $P(A+P(Z))=P(A)+Z$ or $P(P(A)+Z)=A+P(Z)$. Substitute
 $A=x+y$, $Z=-x'-u$, $P(Z)=-x$. And $P(A)=P(x+y)=x'+y'+v$ (using
 Case 2).


 Option 1: $P((x+y)+(-x))=P(x+y)+(-x'-u)$. $P(y)=(x'+y'+v)-x'-u=y'+v-u$.

 Option 2: $P(P(x+y)+Z)=A+P(Z)$. $P((x'+y'+v)+(-x'-u))=(x+y)+(-x)$.
 $P(y'+v-u)=y$.


 So we have $P(y)=y'+v-u$ or $P(y'+v-u)=y$. This means $y'+v-u$
 must be either $P(y)$ or $P^{-1}(y)$. We know $P(y)=y'+v$ and $P^{-1}(y)=y'$.
 If $y'+v-u=P(y)=y'+v$, then $v-u=v$, which means $u=0$. This contradicts
 our assumption $u\neq0$. If $y'+v-u=P^{-1}(y)=y'$, then $v-u=0$,
 which means $u=v$. This contradicts our assumption $u\neq v$.


 Both possibilities lead to a contradiction. Therefore, the initial
 assumption that there exist distinct non-zero values $u,v$ for $g(x)$
 must be false. The set $S=\{g(a):a\in\mathbb{Q}\}$ can contain $g(0)=P(0)+P(0)=0$.
 It can contain at most one non-zero value $u$. Thus, the set $S$
 must be a subset of $\{0,u\}$ for some $u\in\mathbb{Q}$. The maximum
 possible number of elements in $S$ is $2$.


 Since we found an example where the set of values is $\{0,-2\}$,
 which has 2 elements, the maximum possible number of elements is exactly
 2.