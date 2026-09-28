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
2: \[ (b - a)f(f(a)) = a f(a + f(b)), \]
3: we examine several cases based on the properties of $f$.
4: 
5: **1. Constant Solutions**
6: Suppose $f(x) = k$ for some constant $k$. Substituting this into the original equation:
7: \[ (b - a)k = ak \implies bk - ak = ak \implies bk = 2ak. \]
8: For this to hold for all $a, b \in \mathbb{R}$, we must have $k = 0$.
9: Checking $f(x) = 0$: $(b - a) \cdot 0 = a \cdot 0 \implies 0 = 0$.
10: Thus, $f(x) = 0$ is a solution.
11: 
12: **2. Non-constant Solutions**
13: Let $f(0) = c$. Substituting $a = 0$ into the original equation:
14: \[ (b - 0)f(f(0)) = 0 \cdot f(0 + f(b)) \implies b f(c) = 0. \]
15: Since this must hold for all $b \in \mathbb{R}$, we have $f(c) = 0$.
16: 
17: **Case 2.1: $c = 0$**
18: If $f(0) = 0$, the original equation becomes $(b - a)f(f(a)) = a f(a + f(b))$.
19: Setting $b = 0$:
20: \[ -a f(f(a)) = a f(a + f(0)) = a f(a). \]
21: For $a \neq 0$, we have $f(f(a)) = -f(a)$. Since $f(f(0)) = f(0) = 0 = -f(0)$, the identity $f(f(a)) = -f(a)$ holds for all $a \in \mathbb{R}$. Substituting this back into the original equation:
22: \[ (b - a)(-f(a)) = a f(a + f(b)). \]
23: If $f(a) = 0$ for all $a$, we return to the solution $f(x) = 0$. If there exists some $a \neq 0$ such that $f(a) \neq 0$, then for a fixed $a$, the expression $\frac{(a - b)f(a)}{a}$ can take any real value as $b$ varies. Thus, $f(a + f(b))$ takes all real values, meaning $f$ is surjective.
24: Since $f$ is surjective, for any $y \in \mathbb{R}$, there exists $x$ such that $f(x) = y$. Then $f(y) = f(f(x)) = -f(x) = -y$.
25: Checking $f(x) = -x$:
26: LHS: $(b - a)f(f(a)) = (b - a)a = ab - a^2$.
27: RHS: $a f(a + f(b)) = a f(a - b) = a(-(a - b)) = ab - a^2$.
28: This is a solution.
29: 
30: **Case 2.2: $c \neq 0$**
31: Setting $a = c$ in the original equation:
32: \[ (b - c)f(f(c)) = c f(c + f(b)). \]
33: Since $f(c) = 0$, we have $f(f(c)) = f(0) = c$. Thus:
34: \[ (b - c)c = c f(c + f(b)) \implies f(c + f(b)) = b - c. \]
35: Setting $b = c$ in the original equation:
36: \[ (c - a)f(f(a)) = a f(a + f(c)) = a f(a + 0) = a f(a). \]
37: For $a \neq c$, $f(f(a)) = \frac{a f(a)}{c - a}$.
38: Setting $b = 0$ in the original equation:
39: \[ (0 - a)f(f(a)) = a f(a + f(0)) = a f(a + c). \]
40: For $a \neq 0$, $f(a + c) = -f(f(a)) = \frac{a f(a)}{a - c}$.
41: From $f(c + f(b)) = b - c$, we apply $f$ to both sides:
42: \[ f(f(c + f(b))) = f(b - c). \]
43: We note that if $f(b) = 0$, then $f(c + f(b)) = f(c) = 0$, so $b - c = 0$, which means $b = c$. Thus, for $b \neq c$, we have $f(b) \neq 0$. This ensures that $x = c + f(b) \neq c$, allowing us to use the identity $f(f(x)) = \frac{x f(x)}{c - x}$ with $x = c + f(b)$:
44: \[ f(b - c) = \frac{(c + f(b)) f(c + f(b))}{c - (c + f(b))} = \frac{(c + f(b))(b - c)}{-f(b)}. \]
45: Let $b - c = x$, so $b = x + c$:
46: \[ f(x) = \frac{(c + f(x + c))x}{-f(x + c)} \implies f(x) (-f(x + c)) = cx + x f(x + c) \implies f(x + c) = \frac{-cx}{x + f(x)}. \]
47: Equating the two expressions for $f(x + c)$:
48: \[ \frac{x f(x)}{x - c} = \frac{-cx}{x + f(x)}. \]
49: For $x \neq 0, c$, we have $\frac{f(x)}{x - c} = \frac{-c}{x + f(x)}$, which implies:
50: \[ f(x)^2 + x f(x) = -cx + c^2 \implies f(x)^2 + x f(x) + cx - c^2 = 0. \]
51: Solving the quadratic for $f(x)$:
52: \[ f(x) = \frac{-x \pm \sqrt{x^2 - 4(cx - c^2)}}{2} = \frac{-x \pm \sqrt{(x - 2c)^2}}{2} = \frac{-x \pm |x - 2c|}{2}. \]
53: This implies that for each $x$, $f(x)$ is either $-c$ or $c - x$.
54: If $f(b) = -c$ for some $b$, then from $f(c + f(b)) = b - c$, we get $f(0) = b - c \implies c = b - c \implies b = 2c$.
55: Thus, for $b \neq 2c$, we must have $f(b) = c - b$. For $b = 2c$, $f(2c) = c - 2c = -c$.
56: Therefore, $f(x) = c - x$ for all $x \in \mathbb{R}$.
57: Checking $f(x) = c - x$:
58: LHS: $(b - a)f(f(a)) = (b - a)f(c - a) = (b - a)(c - (c - a)) = (b - a)a$.
59: RHS: $a f(a + f(b)) = a f(a + c - b) = a(c - (a + c - b)) = a(b - a)$.
60: This is a solution for any $c \in \mathbb{R}$.
61: 
62: The functions satisfying the equation are $f(x) = 0$ and $f(x) = c - x$ for any constant $c \in \mathbb{R}$.
