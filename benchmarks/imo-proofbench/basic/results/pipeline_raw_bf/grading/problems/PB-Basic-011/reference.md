Partition the set $\{ 1,2,3,\cdots ,2000\}$ into 1000 parts $P_{1}\cup P_{2}\cup P_{3}\cup \cdots \cup P_{1000}$ such that $P_{a}$ contains all numbers of the form $2^{b}(2a-1)$ where $b$ is a nonnegative integer.

 $A$ cannot have two elements from the same part (otherwise one would divide the other by a power of 2). So $A$ must have exactly one element from each part.

 Let $t_{a}$ be the element of $A$ contained in $P_{a}$. Then consider $t_{1},t_{2},t_{5},\cdots $, each being a product of a power of 3 and a power of 2. The highest power of 2 dividing $t_{1}$ must be strictly greater than the highest power of 2 dividing $t_{2}$ (otherwise $t_{1}$ divides $t_{2}$). Similarly, the highest powers of 2 dividing $t_{1},t_{2},t_{5},\cdots $ must be a strictly decreasing sequence. In particular, there are 7 numbers in the sequence, so $t_{1}$ must be at least $2^6=64$. In a similar manner, if $666<3^{b}(2a-1)<2000$, then $t_{a}\geq 2^{b}(2a-1)$. (Here we look at the numbers where the odd factors are $(2a-1)$ times a power of 3.)

 Suppose one of the $t_{a}$ is less than 64. Then we have
 \[666<3^{b}(2a-1)\leq (3/2)^{b}t_{a}<64(3/2)^{b}\]
 so that $b\geq 6$. However, this means either $a=1$ (we know $t_{1}\geq 64$) or $t_{a}\geq 3\cdot 2^{6}$, which is a contradiction. Therefore, every element must be at least 64.


 We could attain a minimum by setting $t_{a}=2^{f(a)}(2a-1)$ where $f(a)$ satisfies $666<3^{f(a)}(2a-1)<2000$ if we can show it works. To do this, we must show that $t_{x}$ cannot divide $t_{y}$ for any $x\neq y$. Suppose there were such $x$ and $y$. Then
 \[2^{u}(2x-1)|2^{v}(2y-1)\]
 where $u=f(x)$ and $v=f(y)$. In particular, $u\leq v$ and $(2x-1)|(2y-1)$.

 In order to have $(2x-1)|(2y-1)$, we must have $2y-1\geq 3(2x-1)$, but this implies
 \[3^{u+1}(2x-1) \ge 2001 >3^{v}(2y-1)\geq 3^{v+1}(2x-1)\]
 and $u>v$, a contradiction! Therefore $\boxed{64}$ is the minimum.
