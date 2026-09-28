Note that the function is bijective, so setting $x=0$ gives $g(0)=0$ and since it is strictly increasing, we further derive $g(x)>0$ for $x>0$ and $g(x)<0$ for $x<0$.

 Consider the sequence $u_0 = x, u_{n+1} = g(u_n)$, we have that $u_{n+1} = u_n + 20u_{n-1}$, which gives $u_n = a (-4)^n + b 5^n$ for some real number $a, b$. Moreover, since $g$ is a bijective, there exists a real number $r$ such that $u_{-1} = r$, and so the sequence is well-defined for negative integer $n$ by defining the sequence backward. And since the sequence is increasing, $u_0 > 0$ implies $u_n > 0$ for all integer $n$.

 We will show that $a = 0$, which implies $g(x) = u_1 = 5u_0 = 5x$.

 Indeed, assume that $a > 0$, if $u_0 = x > 0$ then we choose a sufficiently small odd negative integer $n$ such that $(-4/5)^n < -b/a$, this gives $u_n < 0$. However, since $g$ is increasing and $u_0 > 0$, we must have that $u_n > 0$, which is a contradiction. Similarly, if $u_0 = a+b < 0$ then we must have $b < 0$ given $a > 0$, and so for a sufficiently small negative even integer $n$, we have $(-4/5)^n > -b/a$, which gives $u_n > 0$, which is a contradiction. Thus, we must have $a \leq 0$.

 Similarly, we can show that $a < 0$ will lead to a contradiction, and so, we must have $a \geq 0$.

 Together, this implies that $a = 0$. Hence proved.