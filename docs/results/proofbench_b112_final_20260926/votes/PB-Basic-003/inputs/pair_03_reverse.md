# Problem

Find all functions $f\colon \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a,b \in \mathbb{R}$,
 \[ (b - a)f(f(a)) = a f(a + f(b)). \]"

# Proof A

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
