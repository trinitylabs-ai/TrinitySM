# Problem

Find all non-negative integers $a,b,c$ such that $20^{a}+b^{4}=2024^{c}$

# Proof A

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

# Proof B

1: To find all non-negative integers $a, b, c$ such that $20^a + b^4 = 2024^c$, we analyze the equation by considering different values for the variables and using modular arithmetic.
2: 
3: **1. Case $c = 0$**
4: If $c = 0$, the equation becomes:
5: $$20^a + b^4 = 2024^0 = 1$$
6: Since $a$ and $b$ are non-negative integers, $20^a \ge 1$ and $b^4 \ge 0$.
7: - If $a \ge 1$, then $20^a \ge 20$, which makes $20^a + b^4 > 1$. Thus, we must have $a = 0$.
8: - Substituting $a = 0$ gives $20^0 + b^4 = 1 \implies 1 + b^4 = 1 \implies b^4 = 0 \implies b = 0$.
9: This yields the solution $(a, b, c) = (0, 0, 0)$.
10: 
11: **2. Case $c \ge 1$**
12: If $c \ge 1$, we examine the equation modulo 11. Note that $2024 = 11 \times 184$, so $2024 \equiv 0 \pmod{11}$. The equation becomes:
13: $$20^a + b^4 \equiv 0 \pmod{11}$$
14: Since $20 \equiv 9 \pmod{11}$, we have:
15: $$9^a + b^4 \equiv 0 \pmod{11} \implies b^4 \equiv -9^a \pmod{11}$$
16: We first determine the possible values of $9^a \pmod{11}$ for $a \in \mathbb{N}_0$:
17: - $9^0 \equiv 1 \pmod{11}$
18: - $9^1 \equiv 9 \pmod{11}$
19: - $9^2 \equiv 81 \equiv 4 \pmod{11}$
20: - $9^3 \equiv 9 \times 4 = 36 \equiv 3 \pmod{11}$
21: - $9^4 \equiv 9 \times 3 = 27 \equiv 5 \pmod{11}$
22: - $9^5 \equiv 9 \times 5 = 45 \equiv 1 \pmod{11}$
23: The sequence of powers $9^a \pmod{11}$ is periodic with period 5, taking values in the set $\{1, 3, 4, 5, 9\}$.
24: Consequently, the possible values for $-9^a \pmod{11}$ are:
25: - $-1 \equiv 10 \pmod{11}$
26: - $-3 \equiv 8 \pmod{11}$
27: - $-4 \equiv 7 \pmod{11}$
28: - $-5 \equiv 6 \pmod{11}$
29: - $-9 \equiv 2 \pmod{11}$
30: Thus, $b^4 \pmod{11} \in \{2, 6, 7, 8, 10\}$.
31: 
32: Next, we determine the possible 4th powers modulo 11:
33: - $0^4 \equiv 0 \pmod{11}$
34: - $1^4 \equiv 1 \pmod{11}$
35: - $2^4 = 16 \equiv 5 \pmod{11}$
36: - $3^4 = 81 \equiv 4 \pmod{11}$
37: - $4^4 = 256 = 23 \times 11 + 3 \equiv 3 \pmod{11}$
38: - $5^4 = 625 = 56 \times 11 + 9 \equiv 9 \pmod{11}$
39: - $6^4 \equiv (-5)^4 \equiv 9 \pmod{11}$
40: - $7^4 \equiv (-4)^4 \equiv 3 \pmod{11}$
41: - $8^4 \equiv (-3)^4 \equiv 4 \pmod{11}$
42: - $9^4 \equiv (-2)^4 \equiv 5 \pmod{11}$
43: - $10^4 \equiv (-1)^4 \equiv 1 \pmod{11}$
44: The set of 4th powers modulo 11 is $\{0, 1, 3, 4, 5, 9\}$.
45: 
46: Comparing the two sets:
47: $$\{2, 6, 7, 8, 10\} \cap \{0, 1, 3, 4, 5, 9\} = \emptyset$$
48: Since there is no overlap, there are no non-negative integers $a, b$ that satisfy $b^4 \equiv -9^a \pmod{11}$. Therefore, no solutions exist for $c \ge 1$.
49: 
50: **Final Result**
51: The only non-negative integer solution is $(a, b, c) = (0, 0, 0)$.
52: 
53: \(\square\)
