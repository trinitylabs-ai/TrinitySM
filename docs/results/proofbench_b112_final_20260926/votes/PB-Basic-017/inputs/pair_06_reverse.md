# Problem

Find all non-negative integer $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number.

# Proof A

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

# Proof B

1: To find all non-negative integers $n$ such that $A_n = 1 + 3^{20(n^2+n+1)} + 9^{14(n^2+n+1)}$ is a prime number, we analyze the structure of the expression.
2: 
3: Let $k = n^2 + n + 1$. Since $n$ is a non-negative integer, $k$ is a positive integer. Specifically, for $n \ge 0$, the minimum value of $k$ is $0^2 + 0 + 1 = 1$.
4: The expression for $A_n$ is:
5: \[ A_n = 1 + 3^{20k} + 9^{14k} \]
6: Since $9 = 3^2$, we can rewrite the term $9^{14k}$ as:
7: \[ 9^{14k} = (3^2)^{14k} = 3^{28k} \]
8: Thus, the expression becomes:
9: \[ A_n = 3^{28k} + 3^{20k} + 1 \]
10: Let $z = 3^{4k}$. Since $k \ge 1$, we have $z = 3^{4(n^2+n+1)} \ge 3^4 = 81$. Substituting $z$ into the expression for $A_n$, we obtain:
11: \[ A_n = (3^{4k})^7 + (3^{4k})^5 + 1 = z^7 + z^5 + 1 \]
12: We now seek to factor the polynomial $P(z) = z^7 + z^5 + 1$. We test if $z^2 + z + 1$ is a factor by evaluating $P(z)$ at the roots of $z^2 + z + 1 = 0$. The roots are the primitive cube roots of unity, $\omega$ and $\omega^2$, where $\omega^3 = 1$ and $\omega \neq 1$.
13: Substituting $z = \omega$ into $P(z)$:
14: \[ P(\omega) = \omega^7 + \omega^5 + 1 = (\omega^3)^2 \cdot \omega + \omega^3 \cdot \omega^2 + 1 = 1^2 \cdot \omega + 1 \cdot \omega^2 + 1 = \omega^2 + \omega + 1 \]
15: Since $\omega^2 + \omega + 1 = 0$, we have $P(\omega) = 0$. Thus, $z^2 + z + 1$ is a factor of $z^7 + z^5 + 1$. Performing polynomial division, we find:
16: \[ z^7 + z^5 + 1 = (z^2 + z + 1)(z^5 - z^4 + z^3 - z + 1) \]
17: To verify this identity:
18: \[ (z^2 + z + 1)(z^5 - z^4 + z^3 - z + 1) = z^2(z^5 - z^4 + z^3 - z + 1) + z(z^5 - z^4 + z^3 - z + 1) + 1(z^5 - z^4 + z^3 - z + 1) \]
19: \[ = (z^7 - z^6 + z^5 - z^3 + z^2) + (z^6 - z^5 + z^4 - z^2 + z) + (z^5 - z^4 + z^3 - z + 1) \]
20: \[ = z^7 + (-z^6 + z^6) + (z^5 - z^5 + z^5) + (z^4 - z^4) + (-z^3 + z^3) + (z^2 - z^2) + (z - z) + 1 \]
21: \[ = z^7 + z^5 + 1 \]
22: For $A_n$ to be a prime number, one of the two factors must be equal to 1.
23: 1. The first factor is $F_1 = z^2 + z + 1$. Since $z \ge 81$, $F_1 \ge 81^2 + 81 + 1 = 6643 > 1$.
24: 2. The second factor is $F_2 = z^5 - z^4 + z^3 - z + 1$. We can rewrite this as:
25: \[ F_2 = z^4(z - 1) + z(z^2 - 1) + 1 \]
26: Since $z \ge 81$, we have $z - 1 \ge 80$ and $z^2 - 1 \ge 81^2 - 1 = 6560$. Because $z$ is positive, both terms $z^4(z - 1)$ and $z(z^2 - 1)$ are positive. Specifically, $F_2 \ge 81^4(80) + 81(6560) + 1$, which is strictly greater than 1.
27: 
28: Since $A_n$ is the product of two integers both strictly greater than 1 for all $n \ge 0$, $A_n$ is always composite.
29: 
30: Therefore, there are no non-negative integers $n$ such that $A_n$ is a prime number.
31: 
32: \(\square\)
