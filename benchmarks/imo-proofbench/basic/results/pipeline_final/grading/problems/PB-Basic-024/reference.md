We state the following well-known lemma: If $p=4k+3$ is a prime
 number for some positive integer $k$, and there exists integers $x,y$
 such that $x^{2}+y^{2}$ is divisible by $p$, then we have $x,y$
 are both divisible by $p$.

 We omit the proof of this lemma since it is a well-known result.

 Now, return to the main problem. It is obvious that $(a,b,c)=(0,0,0)$
 is a solution. Now, consider $c>0$, we have the following cases:


 \textbf{Case 1: $a$ is even.}

 In this case, we have $a=2k$ for some non-negative integer $k$.
 This gives $(20^{k})^{2}+(b^{2})^{2}$ is divisible by $2024$, which
 is divisible by $11$. Since $11$ is a prime in the form of $4n+3$
 for some positive integer $n$, we must have that $20^{k},b^{2}$
 are all divisible by $11$, which is a contradiction since $\gcd(20,11)=1$.
 Hence, $a$ cannot be even.


 \textbf{Case 2: $a$ is odd.}

 In this case, we have $a,c\geq1$, and so $b$ must be even. Let $b=2^{t}q$
 for some non-negative integer $t,q$ where $q$ is odd, we have the
 equation becomes $2^{2a}5^{a}+2^{4t}q^{4}=2^{3c}253^{c}$. Consider
 quadratic residue modulo $11$, we have the LHS gives us $-5$ is
 a quadratic residue modulo $11$. However, since $11$ has the form
 $4n+3$ we have $-1$ is a quadratic nonresdue, while $5$ is a quadratic
 residue modulo $11$ from the Law of Quadratic Reciprocity. Hence,
 we have that $-5$ is a quadratic nonresidue modulo $11$, which a
 contradiction.

 Hence, $(a,b,c)=(0,0,0)$ is the only solution.
