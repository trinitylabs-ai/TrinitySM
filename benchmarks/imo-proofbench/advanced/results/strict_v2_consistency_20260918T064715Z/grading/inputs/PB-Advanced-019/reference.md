Let $r$ be a positive real number. Let $A(r)$ denote the fractional part of $2r$, so $A(r) = 2r - \lfloor 2r \rfloor$. We are given that $B(n,r) = \sum_{k=1}^n A(kr)$. We want to find all positive real numbers $r$ such that $n(n+1)r - B(n,r)$ is a multiple of $n$ for all positive integers $n$.

 We can rewrite the condition as
 $$
 n(n+1)r - \sum_{k=1}^n (2kr - \lfloor 2kr \rfloor) = \sum_{k=1}^n \lfloor 2kr \rfloor \quad \text{is a multiple of } n.
 $$
 Let $\alpha = 2r$. Then the condition becomes: $\sum_{k=1}^n \lfloor k\alpha \rfloor$ is a multiple of $n$ for all positive integers $n$.

 We prove that all even integers $\alpha$ satisfy the condition, and no other real number $\alpha$ does so. First we will show that
 even integers satisfy the condition. If $\alpha=2m$ where $m$ is
 an integer then

 \[
 \lfloor\alpha\rfloor+\lfloor2\alpha\rfloor+\cdots+\lfloor n\alpha\rfloor=2m+4m+\cdots+2mn=mn(n+1)
 \]

 which is a multiple of $n$. Since $r > 0$, we must have $\alpha = 2r > 0$. So $\alpha$ must be a positive even integer. If $\alpha = 2m$ for some positive integer $m$, then $r = m$, which is a positive integer.

 Now we will show that they are the only real numbers satisfying the
 conditions of the problem. Let $\alpha=k+\epsilon$ where $k$ is
 an integer and $0\leqslant\epsilon<1$. Then the number
 \[
 \begin{aligned}\lfloor\alpha\rfloor+\lfloor2\alpha\rfloor+\cdots+\lfloor n\alpha\rfloor & = \lfloor k+\epsilon \rfloor+\lfloor2(k+\epsilon)\rfloor+\cdots+\lfloor n(k+\epsilon)\rfloor

 & = k+\lfloor\epsilon\rfloor+2k+\lfloor2\epsilon\rfloor+\cdots+nk+\lfloor n\epsilon\rfloor

 & =\frac{kn(n+1)}{2}+\lfloor\epsilon\rfloor+\lfloor2\epsilon\rfloor+\cdots+\lfloor n\epsilon\rfloor
 \end{aligned}
 \]
 has to be a multiple of $n$. We consider two cases based on the parity
 of $k$.


 \begin{itemize}
 \item Case 1: \textbf{$k$ is even.} Then $\frac{kn(n+1)}{2}$ is always
 a multiple of $n$. Thus
 \[
 \lfloor\epsilon\rfloor+\lfloor2\epsilon\rfloor+\cdots+\lfloor n\epsilon\rfloor
 \]
 also has to be a multiple of $n$. We will prove that $\lfloor n\epsilon\rfloor=0$
 for every positive integer $n$ by strong induction. The base case
 $n=1$ follows from the fact that $0\leqslant\epsilon<1$. Let us
 suppose that $\lfloor m\epsilon\rfloor=0$ for every $1\leqslant m<n$.
 Then the number
 \[
 \lfloor\epsilon\rfloor+\lfloor2\epsilon\rfloor+\cdots+\lfloor n\epsilon\rfloor=\lfloor n\epsilon\rfloor
 \]
 has to be a multiple of $n$. As $0\leqslant\epsilon<1$ then $0\leqslant n\epsilon<n$,
 which means that the number $\lfloor n\epsilon\rfloor$ has to be
 equal to 0. The equality $\lfloor n\epsilon\rfloor=0$ implies $0\leqslant\epsilon<1/n$.
 Since this has to happen for all $n$, we conclude that $\epsilon=0$.
 Thus $\alpha$ is an even integer. Since $r > 0$, $\alpha = 2r > 0$. So $\alpha$ must be a positive even integer. This means $2r = 2m$ for some positive integer $m$. Therefore, $r=m$ must be a positive integer.
 \item Case 2: \textbf{$k$ is odd.} We will prove that $\lfloor n\epsilon\rfloor=n-1$
 for every natural number $n$ by strong induction. The base case $n=1$
 again follows from the fact that $0\leqslant\epsilon<1$. Let us suppose
 that $\lfloor m\epsilon\rfloor=m-1$ for every $1\leqslant m<n$.
 We need the number
 \[
 \begin{aligned}\frac{kn(n+1)}{2}+\lfloor\epsilon\rfloor+\lfloor2\epsilon\rfloor+\cdots+\lfloor n\epsilon\rfloor & =\frac{kn(n+1)}{2}+0+1+\cdots+(n-2)+\lfloor n\epsilon\rfloor

 & =\frac{kn(n+1)}{2}+\frac{(n-2)(n-1)}{2}+\lfloor n\epsilon\rfloor

 & =\frac{k+1}{2}n^{2}+\frac{k-3}{2}n+1+\lfloor n\epsilon\rfloor
 \end{aligned}
 \]
 to be a multiple of $n$. As $k$ is odd, we need $1+\lfloor n\epsilon\rfloor$
 to be a multiple of $n$. Again, as $0\leqslant\epsilon<1$ then $0\leqslant n\epsilon<n$,
 so $\lfloor n\epsilon\rfloor=n-1$ as we wanted. This implies that
 $1-\frac{1}{n}\leqslant\epsilon<1$ for all $n$. Taking the limit as $n \to \infty$, we get $\epsilon=1$, which contradicts $0 \le \epsilon < 1$.
 So there are no other solutions in this case.

 \end{itemize}
 Therefore, $\alpha = 2r$ must be a positive even integer. This implies $r$ must be a positive integer.