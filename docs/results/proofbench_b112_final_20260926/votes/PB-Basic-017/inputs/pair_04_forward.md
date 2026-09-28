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
