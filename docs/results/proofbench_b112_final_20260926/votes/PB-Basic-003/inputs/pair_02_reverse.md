# Problem

Find all functions $f\colon \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a,b \in \mathbb{R}$,
 \[ (b - a)f(f(a)) = a f(a + f(b)). \]"

# Proof A

1: To find all functions $f: \mathbb{R} \rightarrow \mathbb{R}$ such that for all $a, b \in \mathbb{R}$,
2: \[ (b - a)f(f(a)) = a f(a + f(b)), \]
3: we proceed as follows:
4: 
5: **1. Preliminary Observations**
6: Let the given equation be $P(a, b)$.
7: $P(0, b) \implies b f(f(0)) = 0$ for all $b \in \mathbb{R}$, which implies $f(f(0)) = 0$.
8: $P(a, a) \implies 0 = a f(a + f(a))$, which implies $f(a + f(a)) = 0$ for all $a \neq 0$.
9: 
10: **2. Case 1: $f(0) = 0$**
11: If $f(0) = 0$, then $f(f(0)) = 0$ is naturally satisfied. We have $f(a + f(a)) = 0$ for all $a \neq 0$.
12: If $f$ is identically zero, $f(x) = 0$ for all $x$, which satisfies the equation.
13: Suppose $f$ is not identically zero. Let $S = \{x \in \mathbb{R} : f(x) = 0\}$. Since $f(0) = 0$, $0 \in S$.
14: If $S = \{0\}$, then for $a \neq 0$, $f(a + f(a)) = 0$ implies $a + f(a) = 0$, so $f(a) = -a$.
15: Checking $f(x) = -x$:
16: LHS: $(b - a)f(f(a)) = (b - a)f(-a) = (b - a)a$.
17: RHS: $a f(a + f(b)) = a f(a - b) = a(b - a)$.
18: LHS = RHS, so $f(x) = -x$ is a solution.
19: 
20: If $S$ contains some $a_0 \neq 0$, then $P(a_0, b)$ gives:
21: $(b - a_0)f(f(a_0)) = a_0 f(a_0 + f(b)) \implies (b - a_0)f(0) = a_0 f(a_0 + f(b)) \implies 0 = a_0 f(a_0 + f(b))$.
22: Thus, $f(a_0 + f(b)) = 0$ for all $b \in \mathbb{R}$. This implies that for any $v$ in the range of $f$, $a_0 + v \in S$.
23: Now consider $P(a, b)$ for $a \notin S$. Let $f(f(a)) = k$.
24: If $k \neq 0$, then $f(a + f(b)) = \frac{k(b - a)}{a}$. As $b$ varies, the right-hand side takes all real values, meaning $f$ is surjective. However, we found that $a_0 + \text{Range}(f) \subseteq S$. If $f$ is surjective, $\text{Range}(f) = \mathbb{R}$, so $a_0 + \mathbb{R} \subseteq S$, which implies $S = \mathbb{R}$, so $f(x) = 0$ for all $x$, contradicting that $f$ is not identically zero.
25: If $k = 0$ for all $a$, then $f(f(a)) = 0$ for all $a$. Then $P(a, b)$ becomes $0 = a f(a + f(b))$, so $f(a + f(b)) = 0$ for all $a \neq 0$. For a fixed $b$, $f(x) = 0$ for all $x \neq f(b)$. This implies $f$ can be non-zero at most at one point $z$.
26: - If $z = 0$, then $f(0) = w$ and $f(x) = 0$ for $x \neq 0$. $P(a, b)$ for $a \neq 0$ gives $(b - a)f(f(a)) = a f(a + f(b))$. Since $f(f(a)) = f(0) = w$, we have $(b - a)w = a f(a + f(b))$. If $b \neq 0$, $f(b) = 0$, so $(b - a)w = a f(a) = 0$ for all $b \neq 0$, implying $w = 0$.
27: - If $z \neq 0$, then $f(z) = w$ and $f(x) = 0$ for $x \neq z$. $P(a, b)$ for $a \neq z$ gives $0 = a f(a + f(b))$. If $b = z$, $f(b) = w$, so $0 = a f(a + w)$ for all $a \neq z$. For any $a \notin \{0, z\}$, we must have $f(a + w) = 0$, which means $a + w \neq z$. Thus $w \neq z - a$ for all $a \notin \{0, z\}$, which implies $w \in \{z - 0, z - z\} = \{z, 0\}$.
28: If $w = z$, then $f(z) = z$ and $f(x) = 0$ for $x \neq z$. $P(z, b)$ gives $(b - z)f(f(z)) = z f(z + f(b))$. Since $f(f(z)) = f(z) = z$, we have $(b - z)z = z f(z + f(b))$. For $b \neq z$, $f(b) = 0$, so $(b - z)z = z f(z) = z^2$, which implies $b = 2z$. This cannot hold for all $b \neq z$.
29: If $w = 0$, then $f(x) = 0$ for all $x$.
30: Thus, if $f(0) = 0$, the only solutions are $f(x) = 0$ and $f(x) = -x$.
31: 
32: **3. Case 2: $f(0) = c \neq 0$**
33: We know $f(f(0)) = 0$, so $f(c) = 0$.
34: $P(c, b) \implies (b - c)f(f(c)) = c f(c + f(b))$.
35: Since $f(c) = 0$, $f(f(c)) = f(0) = c$. Thus, $(b - c)c = c f(c + f(b))$.
36: Since $c \neq 0$, we have $f(c + f(b)) = b - c$.
37: To show that $f$ is injective, suppose $f(x) = f(y)$. Then $c + f(x) = c + f(y)$, so $f(c + f(x)) = f(c + f(y))$. By the identity $f(c + f(b)) = b - c$, this implies $x - c = y - c$, so $x = y$.
38: To show that $f$ is surjective, for any $y \in \mathbb{R}$, we can choose $b = y + c$. Then $f(c + f(y + c)) = (y + c) - c = y$.
39: Since $f$ is injective and $f(c) = 0$, $c$ is the unique root of $f$.
40: From $P(a, a)$, we have $f(a + f(a)) = 0$ for $a \neq 0$. Since $c$ is the unique root, $a + f(a) = c$ for all $a \neq 0$.
41: Thus, $f(a) = -a + c$ for all $a \neq 0$.
42: Since $f(0) = c$, the formula $f(x) = -x + c$ also holds for $x = 0$.
43: 
44: **4. Verification**
45: For $f(x) = 0$: $(b - a)(0) = a(0) \implies 0 = 0$. Correct.
46: For $f(x) = -x + c$:
47: $f(f(a)) = -(-a + c) + c = a$.
48: $f(a + f(b)) = f(a - b + c) = -(a - b + c) + c = b - a$.
49: $(b - a)a = a(b - a)$. Correct.
50: 
51: The functions satisfying the equation are $f(x) = 0$ and $f(x) = -x + c$ for any constant $c \in \mathbb{R}$.

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
