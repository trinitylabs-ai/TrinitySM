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
