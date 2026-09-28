# Problem

Find all non-negative integers $a,b,c$ such that $20^{a}+b^{4}=2024^{c}$

# Proof A

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
