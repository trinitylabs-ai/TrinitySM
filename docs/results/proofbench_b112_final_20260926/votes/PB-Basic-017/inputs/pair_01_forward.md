# Problem

Find all non-negative integer $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number.

# Proof A

1: To find all non-negative integers $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number, we analyze the expression for $A_n$.
2: 
3: First, we simplify the terms of $A_n$. Let $m = n^2+n+1$. Since $n$ is a non-negative integer, $m$ is a positive integer with $m \ge 0^2+0+1 = 1$. The expression becomes:
4: \[ A_n = 1 + 3^{20m} + (3^2)^{14m} = 1 + 3^{20m} + 3^{28m} \]
5: We can rewrite this expression as a polynomial by substituting $y = 3^{4m}$. Then:
6: \[ 3^{20m} = (3^{4m})^5 = y^5 \quad \text{and} \quad 3^{28m} = (3^{4m})^7 = y^7 \]
7: Thus, $A_n$ corresponds to the value of the polynomial $P(y) = y^7 + y^5 + 1$ for $y = 3^{4m}$.
8: 
9: We check if $P(y)$ is factorable over the integers. Let $\omega$ be a primitive cube root of unity, such that $\omega^2 + \omega + 1 = 0$ and $\omega^3 = 1$. Evaluating $P(y)$ at $y = \omega$:
10: \[ P(\omega) = \omega^7 + \omega^5 + 1 = (\omega^3)^2 \cdot \omega + \omega^3 \cdot \omega^2 + 1 = \omega + \omega^2 + 1 = 0 \]
11: Since $P(\omega) = 0$, the polynomial $y^2 + y + 1$ is a factor of $y^7 + y^5 + 1$. By performing polynomial long division, we obtain:
12: \[ y^7 + y^5 + 1 = (y^2 + y + 1)(y^5 - y^4 + y^3 - y + 1) \]
13: To verify this, we expand the product:
14: \begin{align*} (y^2 + y + 1)(y^5 - y^4 + y^3 - y + 1) &= y^2(y^5 - y^4 + y^3 - y + 1) + y(y^5 - y^4 + y^3 - y + 1) + 1(y^5 - y^4 + y^3 - y + 1) \\ &= (y^7 - y^6 + y^5 - y^3 + y^2) + (y^6 - y^5 + y^4 - y^2 + y) + (y^5 - y^4 + y^3 - y + 1) \\ &= y^7 + (-y^6 + y^6) + (y^5 - y^5 + y^5) + (y^4 - y^4) + (-y^3 + y^3) + (y^2 - y^2) + (y - y) + 1 \\ &= y^7 + y^5 + 1 \end{align*}
15: 
16: For $A_n$ to be a prime number, one of the factors in the product must be equal to 1. We analyze the two factors for $y = 3^{4m}$ where $m \ge 1$:
17: 1.  The first factor is $F_1 = y^2 + y + 1$. Since $m \ge 1$, we have $y = 3^{4m} \ge 3^4 = 81$. Thus:
18:     \[ F_1 \ge 81^2 + 81 + 1 = 6561 + 81 + 1 = 6643 > 1 \]
19: 2.  The second factor is $F_2 = y^5 - y^4 + y^3 - y + 1$. We can rewrite this as:
20:     \[ F_2 = y^4(y - 1) + y(y^2 - 1) + 1 \]
21:     Since $y \ge 81$, both $(y-1)$ and $(y^2-1)$ are positive. Therefore:
22:     \[ F_2 > 1 \]
23: 
24: Since $A_n$ is the product of two integers $F_1$ and $F_2$, both of which are strictly greater than 1 for all non-negative integers $n$, $A_n$ is always a composite number. Thus, there are no non-negative integers $n$ such that $A_n$ is prime.
25: 
26: There are no such non-negative integers $n$. \(\square\)

# Proof B

1: To find all non-negative integers $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number, we analyze the expression for $A_n$.
2: 
3: Let $k = n^2+n+1$. Since $n$ is a non-negative integer, $k$ is always a positive integer. For $n=0$, $k=1$; for $n \ge 1$, $k \ge 3$.
4: We rewrite the expression $A_n$ using the base 3:
5: \[ A_n = 1 + 3^{20k} + (3^2)^{14k} = 1 + 3^{20k} + 3^{28k} \]
6: To simplify the expression, let $z = 3^{4k}$. Then we can express $A_n$ as a polynomial in $z$:
7: \[ A_n = z^7 + z^5 + 1 \]
8: We test for polynomial factors of $P(z) = z^7 + z^5 + 1$. Consider the roots of $z^2+z+1=0$, which are $\omega$ and $\omega^2$ where $\omega^3=1$ and $\omega^2+\omega+1=0$. Substituting $z = \omega$ into $P(z)$:
9: \[ P(\omega) = \omega^7 + \omega^5 + 1 = (\omega^3)^2 \cdot \omega + (\omega^3) \cdot \omega^2 + 1 = \omega + \omega^2 + 1 = 0 \]
10: Since $\omega$ is a root of $P(z)$, the polynomial $z^2+z+1$ must be a factor of $P(z)$. We perform polynomial division to find the other factor:
11: \[ z^7 + z^5 + 1 = (z^2 + z + 1)(z^5 - z^4 + z^3 - z + 1) \]
12: Verification by expansion:
13: \[ (z^2 + z + 1)(z^5 - z^4 + z^3 - z + 1) = z^2(z^5 - z^4 + z^3 - z + 1) + z(z^5 - z^4 + z^3 - z + 1) + 1(z^5 - z^4 + z^3 - z + 1) \]
14: \[ = (z^7 - z^6 + z^5 - z^3 + z^2) + (z^6 - z^5 + z^4 - z^2 + z) + (z^5 - z^4 + z^3 - z + 1) \]
15: \[ = z^7 + (-z^6 + z^6) + (z^5 - z^5 + z^5) + (z^4 - z^4) + (-z^3 + z^3) + (z^2 - z^2) + (z - z) + 1 \]
16: \[ = z^7 + z^5 + 1 \]
17: Thus, $A_n$ is the product of two integers: $F_1 = z^2 + z + 1$ and $F_2 = z^5 - z^4 + z^3 - z + 1$. For $A_n$ to be a prime number, one of these factors must be equal to 1.
18: 
19: We examine the range of $z$ for non-negative integers $n$:
20: Since $n \ge 0$, $k = n^2+n+1 \ge 1$. Thus, $z = 3^{4k} \ge 3^4 = 81$.
21: 1. For $F_1$:
22: \[ F_1 = z^2 + z + 1 \ge 81^2 + 81 + 1 = 6561 + 81 + 1 = 6643 \]
23: Clearly, $F_1 > 1$ for all $n \ge 0$.
24: 2. For $F_2$:
25: We can rewrite $F_2$ as:
26: \[ F_2 = z^4(z - 1) + z(z^2 - 1) + 1 \]
27: Since $z \ge 81$, both $(z-1)$ and $(z^2-1)$ are positive. Thus:
28: \[ F_2 \ge 81^4(80) + 81(81^2 - 1) + 1 > 1 \]
29: Since $A_n$ is the product of two integers $F_1$ and $F_2$, both of which are strictly greater than 1 for all non-negative integers $n$, $A_n$ is always composite.
30: 
31: Consequently, there are no non-negative integers $n$ such that $A_n$ is a prime number.
32: 
33: \(\square\)
