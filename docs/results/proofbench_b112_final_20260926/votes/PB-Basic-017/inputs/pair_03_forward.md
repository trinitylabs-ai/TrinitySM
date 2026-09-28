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
