# Problem

Find all non-negative integers $a,b,c$ such that $20^{a}+b^{4}=2024^{c}$

# Proof A

1: To find all non-negative integers $a, b, c$ such that $20^a + b^4 = 2024^c$, we analyze the equation by considering different cases for the variables.
2: 
3: **Case 1: $a=0$**
4: The equation becomes $1 + b^4 = 2024^c$.
5: - If $c=0$, we have $1 + b^4 = 1$, which implies $b=0$. This gives the solution $(a, b, c) = (0, 0, 0)$.
6: - If $c=1$, we have $b^4 = 2023$. Since $6^4 = 1296$ and $7^4 = 2401$, there is no integer solution for $b$.
7: - If $c \ge 2$, we consider the equation modulo 16. Note that $2024 = 16 \times 126 + 8$, so $2024 \equiv 8 \pmod{16}$. Thus $2024^c \equiv 8^c \pmod{16}$. For $c \ge 2$, $8^c$ is a multiple of $8^2 = 64$, so $2024^c \equiv 0 \pmod{16}$. This implies $b^4 = 2024^c - 1 \equiv -1 \equiv 15 \pmod{16}$. However, fourth powers modulo 16 are only $0$ (for even $b$) or $1$ (for odd $b$). Thus, $b^4 \equiv 15 \pmod{16}$ has no solutions.
8: 
9: **Case 2: $b=0$**
10: The equation becomes $20^a = 2024^c$.
11: - If $c=0$, then $20^a = 1$, so $a=0$, giving $(0, 0, 0)$.
12: - If $c > 0$, the prime factorization of the left side is $20^a = (2^2 \cdot 5)^a = 2^{2a} \cdot 5^a$, and the right side is $2024^c = (2^3 \cdot 11 \cdot 23)^c = 2^{3c} \cdot 11^c \cdot 23^c$. For these to be equal, the prime factors must be the same, but the right side contains 11 and 23, while the left side does not. Thus, no solutions exist for $c > 0$.
13: 
14: **Case 3: $c=0$**
15: The equation becomes $20^a + b^4 = 1$. Since $a, b \ge 0$, the only way this can hold is if $20^a = 1$ and $b^4 = 0$, which implies $a=0$ and $b=0$. This again gives $(0, 0, 0)$.
16: 
17: **Case 4: $a, b, c \ge 1$**
18: We first examine the equation modulo 5:
19: $0 + b^4 \equiv 2024^c \equiv (-1)^c \pmod 5$.
20: By Fermat's Little Theorem, $b^4 \equiv 0 \pmod 5$ if $5|b$ and $b^4 \equiv 1 \pmod 5$ if $5 \nmid b$. Since $(-1)^c$ can only be $1$ or $-1$, we must have $(-1)^c = 1$, which implies that $c$ is even. Let $c = 2m$ for some integer $m \ge 1$.
21: The equation becomes:
22: $20^a = 2024^{2m} - b^4 = (2024^m - b^2)(2024^m + b^2)$.
23: Since the product is $20^a = 2^{2a} \cdot 5^a$, each factor must be of the form $2^x 5^y$. Let:
24: $2024^m - b^2 = 2^x 5^y$ and $2024^m + b^2 = 2^w 5^z$, where $x+w=2a$ and $y+z=a$.
25: Summing these equations gives:
26: $2 \cdot 2024^m = 2^x 5^y + 2^w 5^z$.
27: Substituting $2024 = 2^3 \cdot 253$, we have:
28: $2^{3m+1} \cdot 253^m = 2^x 5^y + 2^w 5^z$.
29: If $x \neq w$, the 2-adic valuation of the right side is $\min(x, w)$, so $\min(x, w) = 3m+1$. If $x=w$, then $x=w=a$.
30: Because the equations for $x > w$ are symmetric to those for $x < w$ by swapping the pairs $(x, y)$ and $(w, z)$, we can assume without loss of generality that $x \le w$. Then $2^{3m+1} \cdot 253^m = 2^x (5^y + 2^{w-x} 5^z)$.
31: Since the left side is not divisible by 5, we must have $y=0$ or $z=0$.
32: 
33: - If $y=0$, then $z=a$ and $2^{3m+1} \cdot 253^m = 2^x (1 + 2^{w-x} 5^a)$.
34:   If $w-x > 0$, then $1 + 2^{w-x} 5^a$ is odd, so $x = 3m+1$ and $253^m - 1 = 2^{w-x} 5^a$. However, $253^m - 1$ is always divisible by $253-1 = 252 = 2^2 \cdot 3^2 \cdot 7$, meaning it is divisible by 3 and 7, but $2^{w-x} 5^a$ is not.
35:   If $w-x = 0$, then $x=w=a$ and $2^{3m+1-a} \cdot 253^m = 1 + 5^a$. This implies $11 | (1+5^a)$, but the residues of $5^a \pmod{11}$ are $\{5, 3, 4, 9, 1\}$, so $5^a+1 \pmod{11} \in \{6, 4, 5, 10, 2\}$, never 0.
36: 
37: - If $z=0$, then $y=a$ and $2^{3m+1} \cdot 253^m = 2^x (5^a + 2^{w-x})$.
38:   If $w-x > 0$, then $5^a + 2^{w-x}$ is odd, so $x = 3m+1$ and $253^m - 5^a = 2^{w-x}$. Modulo 3, $253 \equiv 1$ and $5 \equiv -1$, so $1^m - (-1)^a \equiv 2^{w-x} \pmod 3$. If $a$ is even, $0 \equiv 2^{w-x} \pmod 3$ (impossible). If $a$ is odd, $2 \equiv 2^{w-x} \pmod 3$, which requires $w-x$ to be odd. But $w-x = 2a - 2x$ is always even.
39:   If $w-x = 0$, then $x=w=a$ and $2^{3m+1-a} \cdot 253^m = 5^a + 1$. Again, $11 | 253^m$ but $11 \nmid (5^a+1)$.
40: 
41: Thus, there are no solutions for $a, b, c \ge 1$. The only solution is $(0, 0, 0)$.
42: 
43: The only non-negative integers $a, b, c$ that satisfy the equation are $(0, 0, 0)$.

# Proof B

1: To find all non-negative integers $a, b, c$ such that $20^a + b^4 = 2024^c$, we analyze the equation by considering different cases for the variables.
2: 
3: **Case 1: $c = 0$**
4: The equation becomes $20^a + b^4 = 2024^0 = 1$. Since $a$ and $b$ are non-negative integers, $20^a$ can be $1$ (if $a=0$) or at least $20$ (if $a \ge 1$). If $a=0$, then $1 + b^4 = 1 \implies b=0$. This gives the solution $(a, b, c) = (0, 0, 0)$. If $a \ge 1$, $20^a + b^4 \ge 20$, so no solution exists.
5: 
6: **Case 2: $a = 0$**
7: The equation becomes $1 + b^4 = 2024^c$. If $c=0$, we recover the solution $(0, 0, 0)$. If $c > 0$, then $b^4 = 2024^c - 1$. For $c=1$, $b^4 = 2023$, which is not a fourth power ($6^4 = 1296, 7^4 = 2401$). For $c > 1$, the equation $2024^c - b^4 = 1$ is a specific case of Catalan's Conjecture, which states that the only solution to $x^n - y^m = 1$ for $x, y, n, m > 1$ is $3^2 - 2^3 = 1$. Here $x=2024$ and $y=b$, which does not match. If $b=1$, $2024^c = 2$, impossible. If $b=0$, $2024^c = 1 \implies c=0$.
8: 
9: **Case 3: $b = 0$**
10: The equation becomes $20^a = 2024^c$. Factoring into primes: $(2^2 \cdot 5)^a = (2^3 \cdot 11 \cdot 23)^c$, which simplifies to $2^{2a} \cdot 5^a = 2^{3c} \cdot 11^c \cdot 23^c$. By the Fundamental Theorem of Arithmetic, the prime factors must be identical. The left side contains the prime 5, while the right side does not. This requires $a=0$, which then implies $c=0$, returning us to $(0, 0, 0)$.
11: 
12: **Case 4: $a, b, c > 0$**
13: We examine the equation modulo 5: $20^a \equiv 0 \pmod 5$ for $a \ge 1$. By Fermat's Little Theorem, $b^4 \equiv 0$ or $1 \pmod 5$. Also, $2024^c \equiv (-1)^c \pmod 5$. The equation becomes $0 + b^4 \equiv (-1)^c \pmod 5$. If $b^4 \equiv 0 \pmod 5$, then $0 \equiv (-1)^c \pmod 5$, which is impossible. Thus, $b^4 \equiv 1 \pmod 5$, which implies $(-1)^c \equiv 1 \pmod 5$, so $c$ must be even. Let $c = 2k$ for some $k \ge 1$.
14: The equation is $20^a = 2024^{2k} - b^4 = (2024^k - b^2)(2024^k + b^2)$.
15: Since $20^a = 2^{2a} 5^a$, both factors must be of the form $2^x 5^y$. Let $2024^k - b^2 = 2^z 5^w$ and $2024^k + b^2 = 2^x 5^y$ with $x+z=2a$ and $y+w=a$.
16: Summing these gives $2 \cdot 2024^k = 2^x 5^y + 2^z 5^w$. Substituting $2024 = 2^3 \cdot 253$, we have $2^{3k+1} \cdot 253^k = 2^x 5^y + 2^z 5^w$.
17: If $y > 0$ and $w > 0$, then 5 divides the right side, so 5 must divide $2^{3k+1} \cdot 253^k$, which is impossible. Thus, one of $y$ or $w$ must be 0. By symmetry, assume $y=0$. Then $2^{3k+1} \cdot 253^k = 2^x + 2^z 5^w$.
18: Let $m = \min(x, z)$. Dividing by $2^m$, we get $2^{3k+1-m} \cdot 253^k = 2^{x-m} + 2^{z-m} 5^w$.
19: 
20: Subcase 4.1: $m=x$. Then $2^{3k+1-x} \cdot 253^k = 1 + 2^{z-x} 5^w$.
21: If $z-x > 0$, then $2^{3k+1-x} \cdot 253^k - 2^{z-x} 5^w = 1$. Modulo 2, this requires $3k+1-x=0$, so $253^k - 2^{z-x} 5^w = 1$. For $k=1$, $252 = 2^{z-x} 5^w$, but $252 = 2^2 \cdot 3^2 \cdot 7$ is not of the form $2^\delta 5^w$. For $k \ge 2$, $253-1=252$ divides $253^k-1$, so $252$ must divide $2^{z-x} 5^w$, which is impossible.
22: If $z-x = 0$, then $2^{3k+1-x} \cdot 253^k = 1 + 5^w$. Modulo 11, $253 \equiv 0 \pmod{11}$, so $0 \equiv 1 + 5^w \pmod{11} \implies 5^w \equiv 10 \pmod{11}$. The powers of 5 modulo 11 are $\{5, 3, 4, 9, 1\}$, so no solution exists.
23: 
24: Subcase 4.2: $m=z$. Then $2^{3k+1-z} \cdot 253^k = 2^{x-z} + 5^w$.
25: If $3k+1-z > 0$ and $x-z > 0$, then $5^w$ must be even, which is impossible.
26: If $x-z = 0$, we return to the equation $2^{3k+1-x} \cdot 253^k = 1 + 5^w$, which has no solutions.
27: If $3k+1-z = 0$, then $z = 3k+1$ and $253^k = 2^{x-z} + 5^w$. Let $\delta = x-z$. Then $253^k = 2^\delta + 5^w$.
28: We also have $2b^2 = |(2024^k + b^2) - (2024^k - b^2)| = |2^x 5^y - 2^z 5^w|$. With $y=0$ and $z=3k+1$, $2b^2 = |2^x - 2^{3k+1} 5^w| = 2^{3k+1}|2^\delta - 5^w|$.
29: Thus $b^2 = 2^{3k}|2^\delta - 5^w|$.
30: If $3k$ is even, we require $|2^\delta - 5^w| = v^2$. If $2^\delta > 5^w$, then $2^\delta - 5^w = v^2$; for $\delta \ge 2$, $2^\delta - 5^w \equiv 3 \pmod 4$, impossible. If $5^w > 2^\delta$, then $5^w - 2^\delta = v^2$. However, $3k$ even implies $k$ is even. For $k$ even, $253^k = 2^\delta + 5^w$ has no solutions: modulo 5, $2^\delta \equiv 3^k \equiv \pm 1 \pmod 5$, so $\delta$ is even. Let $\delta=2m$. Then $(253^{k/2}-2^m)(253^{k/2}+2^m) = 5^w$, which implies $253^{k/2}-2^m = 5^p$ and $253^{k/2}+2^m = 5^q$. Then $2 \cdot 2^m = 5^q - 5^p$. For $p=0$, $2^{m+1} = 5^q - 1$, which only has the solution $q=1, m=1$, but $253^{k/2} = 1+2=3$ is impossible.
31: If $3k$ is odd, we require $2|2^\delta - 5^w| = v^2$. If $2^\delta > 5^w$, then $2(2^\delta - 5^w) = v^2$; for $\delta \ge 2$, $2(2^\delta - 5^w) \equiv 2 \pmod 4$, impossible. If $5^w > 2^\delta$, then $2(5^w - 2^\delta) = v^2$; for $\delta \ge 2$, $2(5^w - 2^\delta) \equiv 2 \pmod 4$, impossible.
32: If $\delta = 0$, $253^k = 1 + 5^w \implies 253^k - 1 = 5^w$. For $k=1$, $252 = 5^w$ (no). For $k \ge 2$, $252 | 5^w$ (no).
33: If $\delta = 1$, $253^k = 2 + 5^w \implies 253^k - 2 = 5^w$. Modulo 8, $5^k - 2 \equiv 5^w \pmod 8$. If $k$ is even, $1-2 \equiv 7 \pmod 8$, but $5^w \equiv 1, 5 \pmod 8$. If $k$ is odd, $5-2 \equiv 3 \pmod 8$, but $5^w \equiv 1, 5 \pmod 8$. No solution.
34: If $w=0$, $253^k = 2^\delta + 1 \implies 2^\delta = 253^k - 1$. For $k=1$, $2^\delta = 252$ (no). For $k \ge 2$, $252 | 2^\delta$ (no).
35: 
36: Thus, no solutions exist for $a, b, c > 0$. The only non-negative integer solution is $(a, b, c) = (0, 0, 0)$.
