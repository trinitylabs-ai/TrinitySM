By taking $x = 0$, we get $f(0) + 2f(y) = f(f(y))$ for all $y\in \mathbb{Z}$. So, the problem becomes:
 $$ f(2x) + 2f(y) = f(0) + 2f(x + y) $$
 Taking $x = 1$ for this one, we quickly obtain that $2(f(y+1) - f(y)) = f(2) - f(0) \Leftrightarrow f(y+1)-f(y) = (f(2)-f(0))/2$, so $f$ is linear, that is there exists $k,c$ such that $f(x) = kx+c$. Plug this back into the original equation, we see $f(x) = 2x+c$ and $f(x)=0$ are all possible solutions, and these indeed satisfy the given condition
