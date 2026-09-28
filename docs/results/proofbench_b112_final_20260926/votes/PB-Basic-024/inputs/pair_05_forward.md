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

1: To find all non-negative integers $a, b, c$ such that $20^a + b^4 = 2024^c$, we analyze the equation by considering the prime factorizations: $20 = 2^2 \cdot 5$ and $2024 = 2^3 \cdot 11 \cdot 23 = 2^3 \cdot 253$.
2: 
3: **1. Boundary Cases**
4: *   If $c = 0$, the equation is $20^a + b^4 = 1$. For $a=0$, $1 + b^4 = 1 \implies b=0$. For $a \ge 1$, $20^a \ge 20$, so there are no further solutions. This yields $(0, 0, 0)$.
5: *   If $b = 0$, the equation is $20^a = 2024^c$, which means $2^{2a} \cdot 5^a = 2^{3c} \cdot 253^c$. Due to the unique factorization of integers, the exponents of the primes 5, 11, and 23 must be zero, so $a = 0$ and $c = 0$. This yields $(0, 0, 0)$.
6: *   If $a = 0$, the equation is $1 + b^4 = 2024^c$. For $c=0$, $b=0$. For $c=1$, $b^4 = 2023$, which is not a fourth power ($6^4=1296, 7^4=2401$). For $c \ge 2$, $b^4 = 2024^c - 1$. Modulo 5, $b^4 \equiv (-1)^c - 1 \pmod 5$. Since $b^4 \equiv 0, 1 \pmod 5$, $c$ must be even. Let $c=2k$. Then $b^4 = (2024^k - 1)(2024^k + 1)$. Since $2024$ is even, $2024^k \pm 1$ are odd, so $\gcd(2024^k-1, 2024^k+1) = 1$. Thus, each factor must be a fourth power: $2024^k - 1 = u^4$ and $2024^k + 1 = v^4$. This implies $v^4 - u^4 = 2$, which has no integer solutions.
7: 
8: **2. General Case ($a, b, c > 0$)**
9: We use the 2-adic valuation $v_2(n)$. We have $v_2(20^a) = 2a$, $v_2(b^4) = 4v_2(b)$, and $v_2(2024^c) = 3c$.
10: 
11: *   **Case A: $2a < 4v_2(b)$**. Then $v_2(20^a + b^4) = 2a$, so $2a = 3c$.
12:     Then $b^4 = 2^{3c} 253^c - 2^{2a} 5^a = 2^{2a}(253^c - 5^a)$. Thus $2a$ must be a multiple of 4 ($a$ even), and $253^c - 5^a = X^4$.
13:     Modulo 5, $3^c \equiv X^4 \equiv 0, 1 \pmod 5$, so $c$ is even. Let $c=2k$.
14:     Then $253^{2k} - X^4 = 5^a \implies (253^k - X^2)(253^k + X^2) = 5^a$.
15:     The factors are powers of 5. Let $253^k - X^2 = 5^u$ and $253^k + X^2 = 5^v$ with $v > u$.
16:     Adding them gives $2 \cdot 253^k = 5^u(1 + 5^{v-u})$. Since $\gcd(253, 5) = 1$, we must have $u=0$, so $2 \cdot 253^k = 5^v + 1$.
17:     Modulo 11, $2 \cdot 0 \equiv 5^v + 1 \pmod{11} \implies 5^v \equiv 10 \pmod{11}$. However, the powers of 5 modulo 11 are $\{5, 3, 4, 9, 1\}$. Thus, Case A has no solutions.
18: 
19: *   **Case B: $4v_2(b) < 2a$**. Then $v_2(20^a + b^4) = 4v_2(b)$, so $4v_2(b) = 3c$.
20:     Let $b = 2^{3c/4}m$ with $m$ odd. Then $c=4n$ for some $n$.
21:     $20^a = 2^{3c}(253^c - m^4) \implies 2^{2a} 5^a = 2^{12n}(253^{4n} - m^4) \implies 253^{4n} - m^4 = 2^{2a-12n} 5^a$.
22:     $(253^n - m)(253^n + m)(253^{2n} + m^2) = 2^{2a-12n} 5^a$.
23:     Let $253^n - m = 2^{x_1} 5^{y_1}$ and $253^n + m = 2^{x_2} 5^{y_2}$. Then $2 \cdot 253^n = 2^{x_1} 5^{y_1} + 2^{x_2} 5^{y_2}$.
24:     Since $253^n$ is odd, $\min(x_1, x_2) = 1$. Let $x_1 = 1$. Then $m = |253^n - 2 \cdot 5^{y_1}|$.
25:     The third factor is $253^{2n} + m^2 = 2^{x_3} 5^{y_3}$.
26:     Substituting $m$: $253^{2n} + (253^n - 2 \cdot 5^{y_1})^2 = 2^{x_3} 5^{y_3} \implies 2(253^{2n} - 2 \cdot 253^n 5^{y_1} + 2 \cdot 5^{2y_1}) = 2^{x_3} 5^{y_3}$.
27:     Dividing by 2: $253^{2n} - 2 \cdot 253^n 5^{y_1} + 2 \cdot 5^{2y_1} = 2^{x_3-1} 5^{y_3}$.
28:     If $y_1 > 0$, then $253^{2n} - 2 \cdot 253^n 5^{y_1} + 2 \cdot 5^{2y_1} = (253^n - 5^{y_1})^2 + 5^{2y_1}$.
29:     Let $Z = 253^n - 5^{y_1}$. Since $y_1 > 0$, $Z$ is even. Thus $Z^2 + 5^{2y_1}$ is odd, so $2^{x_3-1} 5^{y_3}$ must be odd, implying $x_3-1 = 0$.
30:     Then $Z^2 + 5^{2y_1} = 5^{y_3}$. If $y_3=0$, $Z^2+5^{2y_1}=1 \implies Z=0, y_1=0$ (Contradiction). If $y_3>0$, then $5 | Z^2 \implies 5 | 253^n$, which is impossible.
31:     Thus $y_1 = 0$. The equation becomes $(253^n - 1)^2 + 1 = 2^{x_3-1} 5^{y_3}$.
32:     Since $253 \equiv 1 \pmod 4$, $Y = 253^n - 1 \equiv 0 \pmod 4$, so $Y^2 + 1 \equiv 1 \pmod{16}$.
33:     This implies $x_3-1 = 0$, so $Y^2 + 1 = 5^{y_3}$.
34:     We solve $Y^2 + 1 = 5^k$ for non-negative integers $Y, k$.
35:     If $k=0$, $Y=0$. If $k=1$, $Y=2$.
36:     If $k \ge 2$, then for $Y=0, 1$ there are no solutions. For $Y \ge 2$, the equation $5^k - Y^2 = 1$ is an instance of Catalan's equation $x^a - y^b = 1$ with $x=5, a=k, y=Y, b=2$. Catalan's Theorem states the only solution for $x, a, y, b > 1$ is $3^2 - 2^3 = 1$. Since $x=5 \neq 3$, there are no solutions for $k \ge 2$.
37:     Thus, $Y=0$ or $Y=2$.
38:     $Y=0 \implies 253^n = 1 \implies n=0$ (Contradiction, $c>0$).
39:     $Y=2 \implies 253^n = 3$ (No).
40:     Thus, Case B has no solutions.
41: 
42: *   **Case C: $2a = 4v_2(b)$**. Let $b = 2^{a/2} m$ with $m$ odd.
43:     $20^a + b^4 = 2^{2a}(5^a + m^4)$. Since $5^a \equiv 1 \pmod 4$ and $m^4 \equiv 1 \pmod 4$, $5^a + m^4 \equiv 2 \pmod 4$, so $v_2(5^a + m^4) = 1$.
44:     Thus $3c = 2a + 1$. Then $b^4 = 2^{3c} 253^c - 2^{2a} 5^a = 2^{2a}(2 \cdot 253^c - 5^a)$, so $2 \cdot 253^c - 5^a = X^4$.
45:     Modulo 5, $X^4 \equiv 2 \cdot 3^c \pmod 5$. For $X^4 \in \{0, 1\}$, we must have $2 \cdot 3^c \equiv 1 \pmod 5 \implies 3^c \equiv 3 \pmod 5 \implies c \equiv 1 \pmod 4$.
46:     However, $b = 2^{a/2} m$ requires $a$ to be even. Then $3c = 2a + 1 \implies 3c \equiv 1 \pmod 4 \implies -c \equiv 1 \pmod 4 \implies c \equiv 3 \pmod 4$.
47:     This is a contradiction.
48: 
49: The only non-negative integer solution is $(0, 0, 0)$.
