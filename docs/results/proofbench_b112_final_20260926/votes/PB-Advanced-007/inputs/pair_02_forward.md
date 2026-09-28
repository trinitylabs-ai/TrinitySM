# Problem

Prove that there exist two real-coefficient polynomials $P(x)$ and $Q(x)$ satisfying the following condition:

 (Condition) The degree of the polynomial $P(x)$ is at least 2024, the degree of $Q(x)$ is at least 2, and for any real number $x$, the following holds:

 \[
 P(Q(x)-x-1)=Q(P(x))
 \]

# Proof A

1: To prove that there exist real-coefficient polynomials $P(x)$ and $Q(x)$ such that $\deg P \ge 2024$, $\deg Q \ge 2$, and $P(Q(x)-x-1) = Q(P(x))$ for all real $x$, we consider polynomials of the following forms:
2: \[ P(x) = (x-h)^n + k, \quad Q(x) = x^2 + ax + b \]
3: where $n \ge 2024$. Substituting these into the given condition $P(Q(x)-x-1) = Q(P(x))$, we have:
4: \[ P(x^2 + ax + b - x - 1) = Q((x-h)^n + k) \]
5: \[ (x^2 + (a-1)x + b-1-h)^n + k = ((x-h)^n + k)^2 + a((x-h)^n + k) + b \]
6: Expanding the right-hand side:
7: \[ (x^2 + (a-1)x + b-1-h)^n + k = (x-h)^{2n} + 2k(x-h)^n + k^2 + a(x-h)^n + ak + b \]
8: \[ (x^2 + (a-1)x + b-1-h)^n + k = (x-h)^{2n} + (2k+a)(x-h)^n + k^2 + ak + b \]
9: To satisfy this equation for all $x$, we can set the base of the power on the left-hand side equal to the base of the power on the right-hand side:
10: \[ x^2 + (a-1)x + b-1-h = (x-h)^2 = x^2 - 2hx + h^2 \]
11: Comparing the coefficients of $x$ and the constant terms, we obtain:
12: 1) $a-1 = -2h \implies a = 1-2h$
13: 2) $b-1-h = h^2 \implies b = h^2+h+1$
14: 
15: With this substitution, the functional equation simplifies to:
16: \[ (x-h)^{2n} + k = (x-h)^{2n} + (2k+a)(x-h)^n + k^2 + ak + b \]
17: For this to hold for all $x$, the coefficients of $(x-h)^n$ and the constant terms must match:
18: 3) $2k+a = 0 \implies k = -a/2$
19: 4) $k = k^2 + ak + b$
20: 
21: Substituting $a = 1-2h$ into (3), we find $k = -(1-2h)/2 = h - 1/2$. Now we substitute $a=1-2h$, $b=h^2+h+1$, and $k=h-1/2$ into (4):
22: \[ h - \frac{1}{2} = \left(h - \frac{1}{2}\right)^2 + (1-2h)\left(h - \frac{1}{2}\right) + h^2+h+1 \]
23: Expanding the right-hand side:
24: \[ h - \frac{1}{2} = \left(h^2 - h + \frac{1}{4}\right) + \left(h - \frac{1}{2} - 2h^2 + h\right) + h^2+h+1 \]
25: \[ h - \frac{1}{2} = (h^2 - 2h^2 + h^2) + (-h + 2h + h) + \left(\frac{1}{4} - \frac{1}{2} + 1\right) \]
26: \[ h - \frac{1}{2} = 2h + \frac{3}{4} \]
27: Solving for $h$:
28: \[ h = -\frac{1}{2} - \frac{3}{4} = -\frac{5}{4} \]
29: Using $h = -5/4$, we determine the other parameters:
30: \[ a = 1 - 2\left(-\frac{5}{4}\right) = 1 + \frac{5}{2} = \frac{7}{2} \]
31: \[ b = \left(-\frac{5}{4}\right)^2 + \left(-\frac{5}{4}\right) + 1 = \frac{25}{16} - \frac{20}{16} + \frac{16}{16} = \frac{21}{16} \]
32: \[ k = -\frac{5}{4} - \frac{1}{2} = -\frac{7}{4} \]
33: We verify condition (4) with these values:
34: \[ k^2 + ak + b = \left(-\frac{7}{4}\right)^2 + \left(\frac{7}{2}\right)\left(-\frac{7}{4}\right) + \frac{21}{16} = \frac{49}{16} - \frac{49}{8} + \frac{21}{16} = \frac{49 - 98 + 21}{16} = -\frac{28}{16} = -\frac{7}{4} \]
35: Since $k = -7/4$, the condition is satisfied. Thus, for any $n \ge 2024$, the polynomials
36: \[ P(x) = \left(x + \frac{5}{4}\right)^n - \frac{7}{4} \quad \text{and} \quad Q(x) = x^2 + \frac{7}{2}x + \frac{21}{16} \]
37: satisfy the given condition. The degree of $P(x)$ is $n \ge 2024$ and the degree of $Q(x)$ is 2, fulfilling all requirements.

# Proof B

1: To prove that there exist real-coefficient polynomials $P(x)$ and $Q(x)$ satisfying the condition $P(Q(x)-x-1) = Q(P(x))$ with $\deg(P) \ge 2024$ and $\deg(Q) \ge 2$, we seek a specific form for $P$ and $Q$.
2: 
3: Let $Q(x) = x^2 + x + 1$. Then the expression $Q(x) - x - 1$ simplifies to $x^2$. The condition $P(Q(x)-x-1) = Q(P(x))$ then becomes:
4: \[ P(x^2) = P(x)^2 + P(x) + 1 \]
5: We search for a polynomial $P(x)$ of the form $P(x) = x^n + a_{n-1}x^{n-1} + \dots + a_0$ for $n \ge 2024$.
6: Equating the leading coefficients of $P(x^2)$ and $P(x)^2 + P(x) + 1$, we have $a_n = a_n^2$, which implies $a_n = 1$ since $P$ is not the zero polynomial.
7: Matching the coefficient of $x^{2n-1}$ in the equation $P(x^2) = P(x)^2 + P(x) + 1$:
8: The LHS $P(x^2)$ has no $x^{2n-1}$ term. The RHS $P(x)^2 + P(x) + 1$ contains the term $2a_n a_{n-1} x^{2n-1} = 2a_{n-1} x^{2n-1}$. Thus, $2a_{n-1} = 0$, implying $a_{n-1} = 0$.
9: Continuing this for all odd powers $x^{2n-k}$, we find $a_{n-k} = 0$ for all odd $k$.
10: If we test the form $P(x) = x^n + c$, the equation becomes:
11: \[ x^{2n} + c = (x^n + c)^2 + (x^n + c) + 1 = x^{2n} + (2c+1)x^n + c^2 + c + 1 \]
12: For this to hold for all $x$, we must have:
13: 1. $2c + 1 = 0 \implies c = -1/2$.
14: 2. $c = c^2 + c + 1 \implies c^2 + 1 = 0$.
15: This system has no real solutions.
16: 
17: However, if we consider the case where $P$ and $Q$ are constants, we find solutions like $P(x) = 1, Q(x) = x^2 - x + 1$, where $P(Q(x)-x-1) = 1$ and $Q(P(x)) = Q(1) = 1^2 - 1 + 1 = 1$. To satisfy $\deg(P) \ge 2024$, we look for a non-constant $P$ such that $Q(P(x)) = P(Q(x)-x-1)$.
18: 
19: We search for polynomials of the form $Q(x) = qx^2 + x + c$ and $P(x) = bx^n + a$ for some $n \ge 2024$.
20: First, we simplify the expression $Q(x) - x - 1$:
21: \[ Q(x) - x - 1 = (qx^2 + x + c) - x - 1 = qx^2 + c - 1 \]
22: The condition $P(Q(x)-x-1) = Q(P(x))$ then becomes:
23: \[ b(qx^2 + c - 1)^n + a = q(bx^n + a)^2 + (bx^n + a) + c \]
24: Expanding the right-hand side:
25: \[ b(qx^2 + c - 1)^n + a = qb^2x^{2n} + (2qab + b)x^n + qa^2 + a + c \]
26: 
27: For $n=2$, the left-hand side is $b(q^2x^4 + 2q(c-1)x^2 + (c-1)^2) + a$. Matching the coefficients of $x^4, x^2,$ and the constant term:
28: 1. $bq^2 = qb^2 \implies q = b$ (assuming $q, b \neq 0$).
29: 2. $2bq(c-1) = 2qab + b \implies 2q^2(c-1) = 2q^2a + q \implies 2q(c-1) = 2qa + 1$.
30: 3. $b(c-1)^2 + a = qa^2 + a + c \implies q(c-1)^2 = qa^2 + c$.
31: 
32: From (2), we have $a = c - 1 - \frac{1}{2q}$. Substituting this into (3):
33: \[ q(c-1)^2 = q\left(c - 1 - \frac{1}{2q}\right)^2 + c \]
34: \[ q(c-1)^2 = q\left((c-1)^2 - \frac{c-1}{q} + \frac{1}{4q^2}\right) + c \]
35: \[ q(c-1)^2 = q(c-1)^2 - (c-1) + \frac{1}{4q} + c \]
36: \[ 0 = -c + 1 + \frac{1}{4q} + c \implies 1 + \frac{1}{4q} = 0 \implies q = -\frac{1}{4} \]
37: Thus, for $n=2$, any $c \in \mathbb{R}$ works with $q = b = -1/4$ and $a = c + 1$.
38: 
39: For $n \ge 2024$, we repeat the matching process. The leading coefficients require $bq^n = qb^2 \implies b = q^{n-1}$. The right-hand side contains only terms $x^{2n}, x^n,$ and $x^0$. The left-hand side $b(qx^2 + c - 1)^n + a$ is a polynomial in $x^2$ and contains terms $x^{2n}, x^{2n-2}, \dots, x^0$. For the polynomials to be equal, the coefficients of all terms $x^{2k}$ where $2k \neq 2n$ and $2k \neq n$ must be zero.
40: Specifically, the coefficient of $x^{2n-2}$ is $b \binom{n}{n-1} q^{n-1} (c-1)$. For this to be zero (given $b, q \neq 0$), we must have $c = 1$.
41: When $c=1$, the left-hand side simplifies to $bq^n x^{2n} + a$. Now we match the remaining coefficients:
42: 1. $x^{2n}$: $bq^n = qb^2 \implies b = q^{n-1}$.
43: 2. $x^n$: The LHS has no $x^n$ term (since $n \ge 2024 > 0$), so the RHS coefficient must be zero: $2qab + b = 0 \implies b(2qa + 1) = 0 \implies a = -1/(2q)$.
44: 3. Constant term: $a = qa^2 + a + c \implies qa^2 + 1 = 0$ (since $c=1$).
45: 
46: Substituting $a = -1/(2q)$ into $qa^2 + 1 = 0$:
47: \[ q\left(-\frac{1}{2q}\right)^2 + 1 = 0 \implies \frac{q}{4q^2} + 1 = 0 \implies \frac{1}{4q} + 1 = 0 \implies q = -\frac{1}{4} \]
48: Then $a = -1/(2 \cdot -1/4) = 2$ and $b = (-1/4)^{n-1}$.
49: For any $n \ge 2024$, the polynomials $Q(x) = -\frac{1}{4}x^2 + x + 1$ and $P(x) = (-\frac{1}{4})^{n-1}x^n + 2$ satisfy the condition.
50: 
51: \(\square\)
