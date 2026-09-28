From the given equation, observe that $a>c$. The equation can be
 rewritten as:
 \[
 2^{c}\left(2^{a-c}-1\right)=7^{b}-1.
 \]

 We consider the following cases:


 \textbf{Case 1: $b$ is odd}

 In this case, $7^{b}-1\equiv2\pmod 4$, so $2^{c}=2$, which implies
 $c=1$. Substituting back into the equation, we have:
 \[
 2^{a}=7^{b}+1.
 \]

 On the other hand, note that $7^{b}+1=8(7^{b-1}-7^{b-2}+\cdots+7+1)$.
 If $b\ge3$ the second factor is an odd number greater than 1 which
 cannot divide $2^{a}$, contradiction. Therefore we have $b=1$ and
 $2^{a}=8$, so $a=3$. Hence, this case gives the solution $(a,b,c)=(3,1,1)$.


 \textbf{Case 2: $b$ is even but not divisible by $4$}

 Let $b=4k+2$, where $k\in\mathbb{N}$. Then:
 \[
 7^{b}-1=7^{4k+2}-1=\left(7^{2k+1}-1\right)\left(7^{2k+1}+1\right).
 \]

 Reasoning similarly to the previous case, we find that $7^{2k+1}-1$
 is divisible by $2$ but not by $4$, $7^{2k+1}+1$ is divisible by
 $8$ but not by $16$. Therefore, $7^{b}-1$ is divisible by $16$
 but not by $32$, which implies $c=4$. Substituting back into the
 equation, we have:
 \[
 2^{a}=7^{4k+2}+15.
 \]

 Since $7^{4k+2}+15\equiv1\pmod 3$, it follows that $2^{a}\equiv1\pmod 3$.
 Thus, $a$ is even. Let $a=2\ell$, where $\ell\in\mathbb{Z}^{+}$,
 $\ell\geq2$ (since $x>z=4$). We can write:
 \[
 15=2^{2\ell}-7^{4k+2}=\left(2^{\ell}-7^{2k+1}\right)\left(2^{\ell}+7^{2k+1}\right).
 \]

 From here we easily obtain $\ell=3$ and $k=0$ which gives $a=6$
 and $b=2$. Thus, this case gives the solution $(a,b,c)=(6,2,4)$.


 \textbf{Case 3: $b$ is divisible by $4$}

 In this case, $7^{b}-1$ is divisible by $4^{2}=16$. Since $2^{a-c}-1$
 is divisible by $25$, $a-c$ is divisible by $\text{ord}_{25}(2)=20$.
 Then, $2^{a-c}-1$ is divisible by 31. Additionally:
 \[
 2^{a-c}-1\text{ is divisible by }31\implies7^{b}-1\text{ is divisible by }31.
 \]

 Note that $\text{ord}_{31}(7)=15$, so $b$ is divisible by $15$.
 However, in this case $7^{b}-1$ is also divisible by $9$, implying
 $a-c$ must be divisible by $6$ which implies that $2^{a-c}-1$ is
 divisible by $7$. Then, we find:
 \[
 7^{b}-1\text{ is divisible by }7,\text{ leading to a contradiction.}
 \]

 Hence, there are no solutions in this case.


 \textbf{Conclusion}

 The two valid solutions are:
 \[
 (a,b,c)=(3,1,1)\quad\text{and}\quad(a,b,c)=(6,2,4).
 \]