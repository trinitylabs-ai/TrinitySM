The problem actually doesn't have much to do with digits: the idea
 is to pick any length $\ell\leq k$, and look at the rightmost $\ell$
 digits of $n^{k}$; that is, the remainder upon division by $(2n)^{\ell}$.
 We compute it exactly:

 Claim - Let $n\geq1$ be an odd integer, and $k\geq\ell\geq1$ integers.
 Then

 \[
 n^{k}\bmod(2n)^{l}=c(k,\ell)\cdot n^{l}
 \]

 for some odd integer $1\leq c(k,\ell)\leq2^{\ell}-1$.

 Proof. This follows directly by the Chinese remainder theorem, with
 $c(k,\ell)$ being the residue class of $n^{k-i}\left(\bmod2^{\ell}\right)$
 since $n$ is odd. In particular, for the $\ell$ th digit from the
 right to be greater than $d$, it would be enough that
 \[
 c(k,\ell)\cdot n^{\ell}\geq(d+1)\cdot(2n)^{\ell-1}
 \]
 But this inequality holds whenever $n\geq(d+1)\cdot2^{\ell-1}$.

 Putting this together by varying $\ell$, we find that for all odd

 \[
 n\geq(d+1)\cdot2^{k-1}
 \]

 we have that
 \begin{itemize}
 \item $n^{k}$ has $k$ digits in base- $2n$; and
 \item for each $\ell=1,\ldots,k$, the $\ell^{\text{th }}$ digit from the
 right is at least $d+1$

  so the problem is solved.

  Remark. Note it doesn't really matter that $c(k,i)$ is odd per se;
 we only need that $c(k,i)\geq1$.
 \end{itemize}