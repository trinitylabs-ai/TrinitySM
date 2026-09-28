Since $0$ is in $S$, there exists an integer $c$ such that $P(c)=0$.
 We can write $P(x)=(x-c)^{n}Q(x)$ for some positive integer $n$
 and integer coefficient polynomial $Q$ such that $Q(c)\ne0$.

 \noindent Pick a prime number $q$ bigger than $|Q(c)|,|Q(c+1)|,|Q(c-1)|$.
 For every positive integer $m$, there exists an integer $a$ such
 that $P(a)=q^{2024m}$. Then, $(a-c)$ is a power of $q$.

 \noindent If it is 1, it is a contradiction to the fact that $|Q(c+1)|,|Q(c-1)|<q$.
 Therefore, $q$ divides $a-c$ and so $Q(a)-Q(c)$ is a multiple of
 $q$, which shows that $Q(a)$ is not a multiple of $q$. Therefore,
 $|Q(a)|=1$ and $|(a-c)^{n}|=q^{2024m}$. Therefore, $|Q(x)|=1$ for
 infinitely many integers $x$ and so $Q(x)=1$ or $Q(x)=-1$. Then
 $|P(x)|$ is always a $n$th power.

 \noindent In this case we can easily see that $n$ needs to divide
 $2024$. Moreover if $n$ is even and $Q(x)=-1$, $P$ is always negative
 or 0 . Hence, the only possible solutions are of the form: $P(x)=(\pm(x+c))^{n}$
 for some divisor $n$ of 2024. We can easily see that this satisfies
 the problem conditions.