Step 1. Lemma. If for a prime $p$, $p\equiv 2 \pmod{3}$, then $p$ cannot divide $q^2-q+1$ for any prime $q$.
 Proof. Assume $p \mid q^2-q+1$ (so $p$ is odd); then $p \mid q^3+1$, so $q^3 \equiv -1 \pmod{p}$, thus $q^6 \equiv 1 \pmod{p}$. Let $\nu$ be the multiplicative order of $q$ modulo $p$; then $\nu \mid 6$, and $\nu \mid p-1$ (by Fermat's Little theorem). That forces $\nu = 2$ (since $\nu = 1$ means $q \equiv 1 \pmod{p}$, so $-1 \equiv q^3 \equiv 1 \pmod{p}$, forcing $p=2$, absurd), and so $q \equiv -1 \pmod{p}$. But then $0\equiv q^2-q+1 \equiv 1 + 1 + 1 = 3 \pmod{p}$, forcing $p=3$, absurd.

 Step 2. Easily $a>3$, then $a^2=ab+b^3+1>2b+b^3+1>2b+b^2+1=(b+1)^2$, hence $a>b+1$; but then from $a\mid b^3+1=(b+1)(b^2-b+1)$ follows that $a\mid b^2-b+1$, hence $a\equiv 1 \pmod{3}$.

 Step 3. If $b\equiv 1\pmod{3}$, then $1=a^2-ab-b^3 \equiv 1-1-1 = -1 \pmod{3}$, a contradiction. If $b\equiv 2\pmod{3}$, then $1=a^2 - ab - b^3 \equiv 1 - 2 + 1 = 0 \pmod{3}$, a contradiction again. Hence $b=3$ (the only moment where the primality of $b$ is actually used), and from this we easily get $a=7$. So $(a,b)=(7,3)$ is the only solution.
