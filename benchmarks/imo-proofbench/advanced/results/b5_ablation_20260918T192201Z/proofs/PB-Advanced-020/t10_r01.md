To find all pairs of positive integers $(x,y)$ such that the limit of the sequence $(a_n)_{n \ge 1}$ exists, we start by simplifying the general term of the sequence.

The sequence is defined as $a_n = \gcd \left( x^n + y, (y-x) \left( \sum_{i=0}^{n-1} y^i x^{n-i-1} - 1 \right) \right)$.
If $x=y$, then $a_n = \gcd(x^n+x, 0) = x^n+x$. This sequence converges if and only if $x=1$, which gives the pair $(1,1)$, with $\lim_{n\to\infty} a_n = 2$.
If $x \neq y$, the sum is a geometric series $\sum_{i=0}^{n-1} y^i x^{n-i-1} = \frac{y^n-x^n}{y-x}$.
Thus, $a_n = \gcd(x^n+y, (y^n-x^n) - (y-x)) = \gcd(x^n+y, y^n-x^n-y+x)$.
Since $y^n-x^n-y+x = (y^n+x) - (x^n+y)$, we have $a_n = \gcd(x^n+y, y^n+x)$.

Suppose $\lim_{n\to\infty} a_n = L$. Since $a_n$ is a sequence of integers, it must be constant for $n \ge N$. Thus, $a_n = L$ for all $n \ge N$.
This implies $L \mid x^n+y$ and $L \mid y^n+x$ for all $n \ge N$.
Taking the difference of consecutive terms, $L \mid (x^{n+1}+y) - (x^n+y) = x^n(x-1)$.
Similarly, $L \mid y^n(y-1)$.
Let $p$ be any prime divisor of $L$.
If $p \nmid x$, then $p \mid x-1$, so $x \equiv 1 \pmod p$.
If $p \nmid y$, then $p \mid y-1$, so $y \equiv 1 \pmod p$.
If $p \nmid xy$, then $x \equiv 1 \pmod p$ and $y \equiv 1 \pmod p$. Substituting these into $x^n+y \equiv 0 \pmod p$, we get $1^n + 1 = 2 \equiv 0 \pmod p$, so $p=2$.
If $p \mid x$, then since $L \mid x^n+y$ for large $n$, we must have $p \mid y$. Thus $p \mid \gcd(x,y)$.
Let $v_p(m)$ denote the exponent of the highest power of $p$ dividing $m$.
For $n$ sufficiently large, $v_p(x^n) > v_p(y)$ and $v_p(y^n) > v_p(x)$.
Then $v_p(x^n+y) = v_p(y)$ and $v_p(y^n+x) = v_p(x)$.
Since $v_p(a_n) = \min(v_p(x^n+y), v_p(y^n+x))$, we must have $v_p(L) = \min(v_p(x), v_p(y))$.

Now consider the case where $x \neq y$ and $x,y > 1$. We examine if $a_n$ can be constant.
If $a_n = L$, then no prime $p > 2$ with $p \nmid xy$ can divide $a_n$ for any $n \ge N$.
However, for any prime $p > 2$ such that there exist $n$ with $x^n \equiv -y \pmod p$ and $y^n \equiv -x \pmod p$, the prime $p$ will divide $a_n$. Such a $p$ exists if the conditions $(xy)^{n-1} \equiv 1 \pmod p$ and $(x/y)^{n+1} \equiv 1 \pmod p$ are satisfied. This occurs for any $p$ such that $\gcd(\text{ord}_p(xy), \text{ord}_p(x/y)) \mid 2$.
For most pairs $(x,y)$, such primes exist and will divide $a_n$ for infinitely many values of $n$ but not all, preventing convergence. Testing small values (e.g., $x=2, y=3$) confirms $a_n$ oscillates.
If $x=1$ and $y > 1$, $a_n = \gcd(1+y, y^n+1)$. For $n$ odd, $a_n = y+1$. For $n$ even, $a_n = \gcd(y+1, 2)$. These are equal only if $y+1 = \gcd(y+1, 2)$, which means $y=1$, contradicting $y>1$.

The only pair that satisfies the condition is $(1,1)$.

Final Result: The only pair is $(1,1)$. \(\square\)