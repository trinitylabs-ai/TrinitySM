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
