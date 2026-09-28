If there exists an integer $k>0$ such that $c_k = 0$, $P(x)=\sum_{i=0}^k c_i x^i$ has less than $k$ roots. So it suffices to see the cases where $c_k \ne 0$ for all integers $k>0$. Let's prove the following lemma:
 If a polynomial $\sum_{i=0}^n a_i x^i$ has $n$ different real roots, $(\frac{a_{1}}{a_0})^2 - 2 \frac{a_{2}}{a_0} \geq n\sqrt[n]{\frac{a_n ^2}{a_0^2}}$

 (Proof) The left hand side is the sum of squares of inverses of all roots. The right hand side is $n$ times the $n$th root of the product of square of inverses of roots. By AM-GM, we can see that the inequality holds.

 Going back to the main proof, let's assume that all $P(x)=\sum_{i=0}^k c_i x^i$ has exactly $k$ distinct real roots.
 By the lemma, $\frac{c_{1}^2 - 2c_0 c_{2}}{\sqrt[n]{c_0^{2n-2}}} \geq n\sqrt[n]{c_n^2}$, which shows that $1\leq c_n^2 \leq (\frac{\frac{c_{1}^2 - 2c_0 c_{2}}{\sqrt[n]{c_0^{2n-2}}}}{n})^n$. We can easily see that the righthandside tends to $0$ as $n$ goes to infinity. It's a contradiction.
