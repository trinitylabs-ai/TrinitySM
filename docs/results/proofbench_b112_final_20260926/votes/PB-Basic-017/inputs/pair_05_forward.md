# Problem

Find all non-negative integer $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number.

# Proof A

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

# Proof B

1: To find all non-negative integers $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number, we simplify the expression and investigate its divisibility.
2: 
3: Let $x = n^2 + n + 1$. Since $n$ is a non-negative integer, $x$ is a positive integer. Specifically, for $n=0$, $x=1$, and for $n \ge 1$, $x \ge 3$.
4: The expression for $A_n$ can be rewritten using the base 3:
5: \[ A_n = 1 + 3^{20x} + (3^2)^{14x} = 1 + 3^{20x} + 3^{28x} \]
6: Let $y = 3^{4x}$. Then $3^{20x} = (3^{4x})^5 = y^5$ and $3^{28x} = (3^{4x})^7 = y^7$. Substituting these into the expression for $A_n$, we obtain:
7: \[ A_n = y^7 + y^5 + 1 \]
8: We seek to factor the polynomial $P(y) = y^7 + y^5 + 1$. We test for roots using the primitive cube roots of unity. Let $\omega$ be a root of $y^2 + y + 1 = 0$, so $\omega^2 + \omega + 1 = 0$ and $\omega^3 = 1$. Evaluating $P(\omega)$:
9: \[ P(\omega) = \omega^7 + \omega^5 + 1 = \omega^1 + \omega^2 + 1 = 0 \]
10: Since $P(\omega) = 0$, the polynomial $y^2 + y + 1$ is a factor of $P(y)$. By polynomial division, we find:
11: \[ y^7 + y^5 + 1 = (y^2 + y + 1)(y^5 - y^4 + y^3 - y + 1) \]
12: To verify this factorization, we expand the product:
13: \begin{align*} (y^2 + y + 1)(y^5 - y^4 + y^3 - y + 1) &= y^2(y^5 - y^4 + y^3 - y + 1) + y(y^5 - y^4 + y^3 - y + 1) + 1(y^5 - y^4 + y^3 - y + 1) \\ &= (y^7 - y^6 + y^5 - y^3 + y^2) + (y^6 - y^5 + y^4 - y^2 + y) + (y^5 - y^4 + y^3 - y + 1) \\ &= y^7 + (-1+1)y^6 + (1-1+1)y^5 + (1-1)y^4 + (-1+1)y^3 + (1-1)y^2 + (1-1)y + 1 \\ &= y^7 + y^5 + 1 \end{align*}
14: For $A_n$ to be a prime number, it must be that one of the two factors is equal to 1.
15: 1.  For the first factor: Since $n \ge 0$, we have $x = n^2 + n + 1 \ge 1$, so $y = 3^{4x} \ge 3^4 = 81$. Thus, $y^2 + y + 1 \ge 81^2 + 81 + 1 = 6643$, which is strictly greater than 1.
16: 2.  For the second factor: Let $f(y) = y^5 - y^4 + y^3 - y + 1$. We can rewrite this as:
17:     \[ f(y) = y^4(y - 1) + y(y^2 - 1) + 1 \]
18:     Since $y \ge 81$, it follows that $y - 1 > 0$ and $y^2 - 1 > 0$. Therefore, $f(y) > 1$.
19: 
20: Since $A_n$ is the product of two integers $y^2+y+1$ and $y^5-y^4+y^3-y+1$, both of which are strictly greater than 1 for all non-negative integers $n$, $A_n$ is always a composite number.
21: 
22: Consequently, there are no non-negative integers $n$ such that $A_n$ is a prime number.
23: 
24: \(\square\)
