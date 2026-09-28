# Problem

Find all functions $f\colon \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a,b \in \mathbb{R}$,
 \[ (b - a)f(f(a)) = a f(a + f(b)). \]"

# Proof A

1: To find all functions $f: \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a, b \in \mathbb{R}$,
2: \[ (b - a)f(f(a)) = a f(a + f(b)), \]
3: we proceed as follows:
4: 
5: **1. Constant Solutions**
6: If $f(x) = c$ for some constant $c$, the equation becomes $(b - a)c = ac$, which simplifies to $bc - ac = ac$, or $bc = 2ac$. For this to hold for all $a, b \in \mathbb{R}$, we must have $c = 0$. Thus, $f(x) = 0$ is a solution.
7: 
8: **2. Initial Properties**
9: Setting $a = 0$ in the original equation gives $b f(f(0)) = 0 \cdot f(0 + f(b)) = 0$. Since this holds for all $b \in \mathbb{R}$, we must have $f(f(0)) = 0$. Let $f(0) = c$. Then $f(c) = 0$.
10: 
11: **3. Case 1: $c \neq 0$**
12: Substituting $a = c$ into the original equation:
13: \[ (b - c)f(f(c)) = c f(c + f(b)). \]
14: Since $f(c) = 0$, we have $f(f(c)) = f(0) = c$. Thus, $(b - c)c = c f(c + f(b))$. Since $c \neq 0$, we divide by $c$ to obtain:
15: \[ f(c + f(b)) = b - c. \quad (*) \]
16: This equation implies that $f$ is a bijection. Specifically, since the right-hand side $b - c$ takes all real values as $b$ varies, $f$ is surjective. If $f(x) = f(y)$, then $f(c + f(x)) = f(c + f(y))$, which implies $x - c = y - c$, so $x = y$, meaning $f$ is injective.
17: 
18: Next, substitute $b = c$ into the original equation:
19: \[ (c - a)f(f(a)) = a f(a + f(c)). \]
20: Since $f(c) = 0$, we have $(c - a)f(f(a)) = a f(a)$. For $a \neq c$, this gives:
21: \[ f(f(a)) = \frac{a f(a)}{c - a}. \quad (**) \]
22: Substituting $(**)$ back into the original equation:
23: \[ (b - a) \frac{a f(a)}{c - a} = a f(a + f(b)). \]
24: For $a \neq 0$ and $a \neq c$, we have $f(a + f(b)) = \frac{(b - a)f(a)}{c - a}$.
25: Let $f(b) = z$. Then $f(a + z) = \frac{f(a)}{c - a} (f^{-1}(z) - a)$.
26: Setting $b = 0$ in $(*)$ gives $f(c + f(0)) = 0 - c$, so $f(c + c) = -c$, which means $f(2c) = -c$.
27: Substituting $a = 2c$ into the relation $f(a + f(b)) = \frac{(b - a)f(a)}{c - a}$:
28: \[ f(2c + f(b)) = \frac{(b - 2c)f(2c)}{c - 2c} = \frac{(b - 2c)(-c)}{-c} = b - 2c. \]
29: Let $f(b) = z$. Then $f(2c + z) = f^{-1}(z) - 2c$.
30: We already have $f(c + z) = f^{-1}(z) - c$ from $(*)$. Subtracting these two yields:
31: \[ f(2c + z) - f(c + z) = (f^{-1}(z) - 2c) - (f^{-1}(z) - c) = -c. \]
32: Let $x = c + z$, then $f(x + c) - f(x) = -c$, or $f(x + c) = f(x) - c$.
33: Using this in $f(c + z) = f^{-1}(z) - c$, we get $f(z) - c = f^{-1}(z) - c$, so $f(z) = f^{-1}(z)$, which implies $f(f(z)) = z$ for all $z$.
34: Now substitute $f^{-1}(z) = f(z)$ into $f(a + z) = \frac{f(a)}{c - a} (f^{-1}(z) - a)$:
35: \[ f(a + z) = \frac{f(a)}{c - a} (f(z) - a). \]
36: Setting $z = c$ gives $f(a + c) = \frac{f(a)}{c - a} (f(c) - a) = \frac{f(a)}{c - a} (0 - a) = \frac{-a f(a)}{c - a}$.
37: From $(**)$, we have $f(f(a)) = \frac{a f(a)}{c - a}$, so $f(a + c) = -f(f(a))$.
38: Since $f(f(a)) = a$, we have $f(a + c) = -a$.
39: Also, we know $f(a + c) = f(a) - c$. Thus:
40: \[ f(a) - c = -a \implies f(a) = c - a. \]
41: Checking $f(x) = c - x$:
42: LHS: $(b - a)f(f(a)) = (b - a)a$.
43: RHS: $a f(a + f(b)) = a f(a + c - b) = a(c - (a + c - b)) = a(b - a)$.
44: LHS = RHS, so $f(x) = c - x$ is a solution for any $c \in \mathbb{R}$.
45: 
46: **4. Case 2: $c = 0$**
47: If $f(0) = 0$, then $f(f(0)) = 0$. Setting $b = 0$ in the original equation gives:
48: \[ -a f(f(a)) = a f(a + f(0)) = a f(a). \]
49: For $a \neq 0$, $f(f(a)) = -f(a)$. Since $f(f(0)) = 0 = -f(0)$, this holds for all $a \in \mathbb{R}$.
50: Substituting $f(f(a)) = -f(a)$ into the original equation:
51: \[ (b - a)(-f(a)) = a f(a + f(b)) \implies a f(a) - b f(a) = a f(a + f(b)). \]
52: For $a \neq 0$, $f(a + f(b)) = f(a)(1 - \frac{b}{a})$.
53: If $f$ is not identically zero, there exists $a \neq 0$ such that $f(a) \neq 0$. Then $f(a + f(b))$ is a non-constant linear function of $b$, which implies $f$ is a bijection.
54: Let $f(1) = k$. Since $f$ is a bijection and $f(0) = 0$, we must have $k \neq 0$.
55: Setting $a = 1$ in $f(a + f(b)) = f(a)(1 - \frac{b}{a})$ gives:
56: \[ f(1 + f(b)) = k(1 - b). \]
57: Applying $f$ to both sides:
58: \[ f(f(1 + f(b))) = f(k(1 - b)). \]
59: Using $f(f(x)) = -f(x)$, we have $-f(1 + f(b)) = f(k(1 - b))$.
60: Substituting $f(1 + f(b)) = k(1 - b)$ into this equation:
61: \[ -k(1 - b) = f(k(1 - b)) \implies f(k(1 - b)) = k(b - 1). \]
62: Let $z = k(1 - b)$. Then $b - 1 = -z/k$.
63: Substituting this into the equation gives $f(z) = k(-z/k) = -z$.
64: Testing $f(x) = -x$ (which is $c - x$ with $c = 0$):
65: LHS: $(b - a)f(f(a)) = (b - a)a$.
66: RHS: $a f(a + f(b)) = a f(a - b) = a(b - a)$.
67: LHS = RHS, so $f(x) = -x$ is a solution.
68: 
69: **Conclusion**
70: The solutions are $f(x) = 0$ and $f(x) = c - x$ for any $c \in \mathbb{R}$.

# Proof B

1: To find all functions $f: \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a, b \in \mathbb{R}$,
2: \[ (b - a) f(f(a)) = a f(a + f(b)), \tag{1} \]
3: we proceed as follows.
4: 
5: Setting $a = 0$ in (1), we have:
6: \[ (b - 0) f(f(0)) = 0 \cdot f(0 + f(b)) \implies b f(f(0)) = 0. \]
7: Since this must hold for all $b \in \mathbb{R}$, we must have $f(f(0)) = 0$. Let $f(0) = c$. Then $f(c) = 0$.
8: 
9: Setting $b = a$ in (1), we have:
10: \[ (a - a) f(f(a)) = a f(a + f(a)) \implies 0 = a f(a + f(a)). \]
11: For all $a \neq 0$, it follows that $f(a + f(a)) = 0$.
12: 
13: We now consider two cases based on the value of $c$.
14: 
15: Case 1: $c \neq 0$.
16: Substituting $a = c$ into (1), we have:
17: \[ (b - c) f(f(c)) = c f(c + f(b)). \]
18: Since $f(c) = 0$, we have $f(f(c)) = f(0) = c$. Thus,
19: \[ (b - c) c = c f(c + f(b)). \]
20: Since $c \neq 0$, we divide by $c$ to obtain:
21: \[ f(c + f(b)) = b - c. \tag{2} \]
22: We check for injectivity. Suppose $f(b_1) = f(b_2)$ for some $b_1, b_2 \in \mathbb{R}$. Then $f(c + f(b_1)) = f(c + f(b_2))$. Applying (2), we get $b_1 - c = b_2 - c$, which implies $b_1 = b_2$. Thus, $f$ is injective.
23: Since $f$ is injective and $f(c) = 0$, we have $f(x) = 0$ if and only if $x = c$.
24: From the previously derived property $f(a + f(a)) = 0$ for $a \neq 0$, we conclude that $a + f(a) = c$ for all $a \neq 0$. Thus, $f(a) = c - a$ for all $a \neq 0$.
25: For $a = 0$, we have $f(0) = c$, which is consistent with $c - 0 = c$.
26: Therefore, $f(x) = c - x$ for all $x \in \mathbb{R}$.
27: 
28: Case 2: $c = 0$.
29: If $c = 0$, then $f(0) = 0$. Equation (1) becomes:
30: \[ (b - a) f(f(a)) = a f(a + f(b)). \]
31: If $f$ is the constant function $f(x) = 0$, it clearly satisfies (1).
32: Suppose $f$ is not identically zero. We first show that $f$ must be a bijection.
33: If $f(f(a)) = 0$ for all $a \in \mathbb{R}$, then $a f(a + f(b)) = 0$ for all $a, b$. For $a \neq 0$, $f(a + f(b)) = 0$. Let $R_f$ be the range of $f$. Then for any $y \in R_f$ and any $a \neq 0$, $a + y$ is a root of $f$. This implies that $f$ vanishes on $\mathbb{R} \setminus \{y\}$. If $R_f$ contains more than one element, $f$ must be identically zero. If $R_f$ is a singleton $\{y\}$, then $f(x) = y$ for all $x$, which implies $f(f(x)) = y$; since $f(f(a)) = 0$, we have $y = 0$, so $f \equiv 0$.
34: Thus, there must exist some $a_0 \neq 0$ such that $f(f(a_0)) \neq 0$. For this $a_0$, we have:
35: \[ f(a_0 + f(b)) = \frac{f(f(a_0))}{a_0} (b - a_0). \]
36: As $b$ varies over $\mathbb{R}$, the right-hand side takes all real values, so $f$ is surjective. Furthermore, if $f(b_1) = f(b_2)$, then $f(a_0 + f(b_1)) = f(a_0 + f(b_2))$, which implies $b_1 - a_0 = b_2 - a_0$, so $b_1 = b_2$. Thus, $f$ is a bijection.
37: Since $f$ is a bijection and $f(0) = 0$, we have $f(x) = 0$ if and only if $x = 0$.
38: From $f(a + f(a)) = 0$ for $a \neq 0$, we conclude $a + f(a) = 0$, so $f(a) = -a$ for all $a \neq 0$.
39: Since $f(0) = 0$, we have $f(x) = -x$ for all $x \in \mathbb{R}$. This is a special case of $f(x) = c - x$ with $c = 0$.
40: 
41: Final Verification:
42: 1. If $f(x) = 0$, then $(b - a) \cdot 0 = a \cdot 0$, which is $0 = 0$.
43: 2. If $f(x) = c - x$, then $f(f(a)) = c - (c - a) = a$ and $f(a + f(b)) = c - (a + c - b) = b - a$.
44:    The equation $(b - a) f(f(a)) = a f(a + f(b))$ becomes $(b - a) a = a (b - a)$, which is true.
45: 
46: The functions satisfying the equation are $f(x) = 0$ and $f(x) = c - x$ for any $c \in \mathbb{R}$.
