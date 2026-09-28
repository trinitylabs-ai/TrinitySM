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
