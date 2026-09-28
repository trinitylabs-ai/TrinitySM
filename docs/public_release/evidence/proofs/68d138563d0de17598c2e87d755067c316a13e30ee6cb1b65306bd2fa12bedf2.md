To prove that for a prime number $p$ and positive integers $a, b, n$ such that $p^n = a^4 + b^4$ with $n \geq 2$, it must be that $n \geq 5$, we analyze the possibilities for $n=2, 3, 4$.

**1. The Case $n=2$**
If $n=2$, the equation becomes $a^4 + b^4 = p^2$. This is a specific instance of the equation $x^4 + y^4 = z^2$. It is a well-known result, proven by Pierre de Fermat using the method of infinite descent, that the equation $x^4 + y^4 = z^2$ has no solutions in positive integers. Consequently, $n=2$ is impossible.

**2. The Case $n=4$**
If $n=4$, the equation becomes $a^4 + b^4 = p^4$. This is a specific case of Fermat's Last Theorem for $k=4$, which states that $x^4 + y^4 = z^4$ has no solutions in positive integers. Thus, $n=4$ is impossible.

**3. The Case $n=3$**
If $n=3$, the equation becomes $a^4 + b^4 = p^3$. 
First, let $d = \gcd(a, b)$. Then $d^4((a/d)^4 + (b/d)^4) = p^3$. Since $p$ is prime, $d^4$ must be a power of $p$. However, $d^4 \leq p^3$ implies $d=1$. Thus, $a$ and $b$ are coprime.

If $p=2$, then $a^4 + b^4 = 8$. Since $a, b \geq 1$, the only possibility is $a=1, b=1$, but $1+1=2 \neq 8$.
If $p > 2$, then $p^3 = (a^2)^2 + (b^2)^2$ implies $p \equiv 1 \pmod 4$. In the ring of Gaussian integers $\mathbb{Z}[i]$, the equation factors as $(a^2 + ib^2)(a^2 - ib^2) = p^3$. 

Let $\delta = \gcd(a^2 + ib^2, a^2 - ib^2)$. Then $\delta$ divides their sum $2a^2$ and their difference $2ib^2$. Since $\gcd(a, b) = 1$, $\delta$ must divide $2$. The prime factorization of $2$ in $\mathbb{Z}[i]$ is $2 = -i(1+i)^2$. If $1+i$ divides $a^2 + ib^2$, then $a^2 + ib^2 \equiv 0 \pmod{1+i}$. Since $i \equiv -1 \pmod{1+i}$, this implies $a^2 - b^2 \equiv 0 \pmod{1+i}$, meaning $a^2 - b^2$ is even, so $a$ and $b$ must have the same parity. Since $\gcd(a, b) = 1$, they must both be odd. However, for any odd integer $x$, $x^4 \equiv 1 \pmod{16}$. Thus, if $a$ and $b$ are odd, $a^4 + b^4 \equiv 2 \pmod{16}$. This would mean $p^3 \equiv 2 \pmod{16}$, which implies $p$ is even, contradicting $p > 2$. Thus, $\delta$ is a unit, and the factors are coprime.

Because $\mathbb{Z}[i]$ is a unique factorization domain, $a^2 + ib^2 = u(x+iy)^3$ for some unit $u \in \{1, -1, i, -i\}$ and some $x+iy \in \mathbb{Z}[i]$ such that $x^2+y^2=p$.
- If $u=1$, $a^2 = x(x^2 - 3y^2)$ and $b^2 = y(3x^2 - y^2)$.
- If $u=-1$, replacing $x \to -x$ and $y \to -y$ reduces this to the $u=1$ case.
- If $u=i$, $a^2 = y(y^2 - 3x^2)$ and $b^2 = x(x^2 - 3y^2)$. Replacing $y \to -y$ and swapping $a \leftrightarrow b$ reduces this to the $u=1$ case.
- If $u=-i$, replacing $x \to -x$ and $y \to -y$ reduces this to the $u=i$ case.
Thus, $u=1$ is sufficient. We have $a^2 = x(x^2 - 3y^2)$ and $b^2 = y(3x^2 - y^2)$. Since $a, b > 0$, we must have $x(x^2 - 3y^2) > 0$ and $y(3x^2 - y^2) > 0$. Since $x^2+y^2=p$ and $\gcd(x, y)=1$, we have $\gcd(x, x^2-3y^2) = \gcd(x, 3)$ and $\gcd(y, 3x^2-y^2) = \gcd(y, 3)$.

- **Case A: $\gcd(x, 3) = 1$ and $\gcd(y, 3) = 1$.**
Then $x = u^2, x^2 - 3y^2 = v^2, y = m^2, 3x^2 - y^2 = k^2$ for some integers $u, v, m, k$. This gives $u^4 - 3m^4 = v^2$ and $3u^4 - m^4 = k^2$. Modulo 4, since $\gcd(u, m)=1$, one is even and the other odd. If $u$ is even and $m$ is odd, $3u^4 - m^4 \equiv -1 \equiv 3 \pmod 4$. If $u$ is odd and $m$ is even, $3u^4 - m^4 \equiv 3 \pmod 4$. Neither can be a square $k^2$.

- **Case B: $\gcd(x, 3) = 1$ and $\gcd(y, 3) = 3$.**
Let $v_3(y) = k \geq 1$. Then $3x^2 - y^2 = 3(x^2 - 3^{k-1}(y/3^k)^2)$. Since $\gcd(x, 3)=1$, $x^2 - 3^{k-1}(y/3^k)^2 \equiv 1 \pmod 3$ if $k \geq 2$. If $k=1$, $y=3s$ with $3 \nmid s$, then $x^2-3s^2 \equiv 1 \pmod 3$. In all cases, $v_3(3x^2-y^2) = 1$.
Since $b^2 = y(3x^2-y^2)$, we have $v_3(b^2) = v_3(y) + 1$. Thus $v_3(y)$ must be odd. Let $v_3(y) = 2j+1$. Then $y = 3^{2j+1}m^2$ for some $m$ with $3 \nmid m$.
Then $b^2 = 3^{2j+1}m^2 \cdot 3(x^2 - 3^{4j+1}m^4) = 3^{2j+2}m^2(x^2 - 3(3^j m)^4)$. Thus $x^2 - 3(3^j m)^4 = k^2$.
Since $\gcd(x, 3)=1$, we have $\gcd(x, x^2-3y^2)=1$. From $a^2 = x(x^2-3y^2)$, it follows that $x$ is a square, $x=u^2$.
Thus $u^4 - 3(3^j m)^4 = k^2$. We prove that $X^4 - 3Y^4 = Z^2$ has no solutions in positive integers by infinite descent.
Assume a solution exists with minimal $X > 0$. Then $(X^2 - Z)(X^2 + Z) = 3Y^4$. Let $g = \gcd(X^2 - Z, X^2 + Z)$. Then $g$ divides $2X^2$ and $2Z$. Since $\gcd(X, Z)=1$, $g \in \{1, 2\}$.
If $g=1$, the coprime factors of $3Y^4$ must be $\{s^4, 3t^4\}$ for some $s, t$ such that $st=Y$. Thus $2X^2 = s^4 + 3t^4$. Modulo 3, $2X^2 \equiv s^4 \pmod 3$. If $3 \nmid s$, then $s^4 \equiv 1 \pmod 3$, so $2X^2 \equiv 1 \pmod 3 \implies X^2 \equiv 2 \pmod 3$, impossible. If $3 \mid s$, then $3 \mid X$, and $2(3X')^2 = (3s')^4 + 3t^4 \implies 6X'^2 = 27s'^4 + t^4$, which implies $3 \mid t$, contradicting $\gcd(s, t)=1$.
If $g=2$, then $X, Z$ are odd and $Y$ is even. Let $Y=2j$. Then $\frac{X^2-Z}{2} \cdot \frac{X^2+Z}{2} = 12j^4$. Since $\gcd=1$, the factors are $\{s^4, 12t^4\}$ or $\{3s^4, 4t^4\}$.
If $X^2 = 3s^4 + 4t^4$, then modulo 4 we have $X^2 \equiv 3s^4 \pmod 4$. If $s$ is odd, $X^2 \equiv 3 \pmod 4$, impossible. If $s$ is even, $s=2S$, then $X^2 = 48S^4 + 4t^4 \implies (X/2)^2 = 12S^4 + t^4$, which is the other case.
If $X^2 = s^4 + 12t^4$, then $(X-s^2)(X+s^2) = 12t^4$, so $\frac{X-s^2}{2} \cdot \frac{X+s^2}{2} = 3t^4$. Since $\gcd(X, s)=1$ and $X, s$ are odd, $\gcd(\frac{X-s^2}{2}, \frac{X+s^2}{2}) = 1$. The coprime factors are $\{u^4, 3v^4\}$.
1) If $\frac{X+s^2}{2} = u^4$ and $\frac{X-s^2}{2} = 3v^4$, then $s^2 = u^4 - 3v^4$. This is the original equation with $u < X$, a contradiction.
2) If $\frac{X+s^2}{2} = 3v^4$ and $\frac{X-s^2}{2} = u^4$, then $s^2 = 3v^4 - u^4$. Modulo 3, $s^2 + u^4 = 3v^4 \implies s, u \equiv 0 \pmod 3$. Let $s=3S, u=3U$. Then $9S^2 + 81U^4 = 3v^4 \implies 3S^2 + 27U^4 = v^4 \implies v=3V$. Then $3S^2 + 27U^4 = 81V^4 \implies S^2 = 27V^4 - 9U^4 = 9(3V^4 - U^4)$. Thus $S=3S'$ and $S'^2 = 3V^4 - U^4$. This is the same form as $s^2 = 3v^4 - u^4$ with $U < s < X$, a contradiction.
Thus, Case B is impossible.

- **Case C: $\gcd(x, 3) = 3$ and $\gcd(y, 3) = 1$.**
Then $x = 3u^2$ and $x^2 - 3y^2 = 3v^2 \implies 3u^4 - y^2 = v^2$. Since $\gcd(y, 3) = 1$, $y = m^2$, so $3u^4 - m^4 = v^2$. Modulo 3, this gives $-m^4 \equiv v^2 \pmod 3$. Since $m^4 \equiv 1 \pmod 3$, we have $v^2 \equiv -1 \equiv 2 \pmod 3$, which is impossible.

Since all cases for $n=2, 3, 4$ lead to contradictions, we conclude $n \geq 5$.

\(\square\)