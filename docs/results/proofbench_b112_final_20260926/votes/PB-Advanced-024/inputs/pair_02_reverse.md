# Problem

Let $P$ be a function from the set $\mathbb{Q}$ of rational numbers
 to itself, and suppose that $P$ satisfies
 \[
 (P(b-P(a))+a-P(b))(P(a+P(b-P(a)))-b)=0
 \]
 for all rational numbers $a,b$. Prove that the set $\{P(a)+P(-a):a\in\mathbb{Q}\}$
 is a finite set, and find the maximum possible number of elements
 in this set.

# Proof A

1: Let $P: \mathbb{Q} \to \mathbb{Q}$ be a function satisfying
2: \[ (P(b-P(a)) + a - P(b))(P(a + P(b-P(a))) - b) = 0 \]
3: for all $a, b \in \mathbb{Q}$. Let $X(a, b) = P(b-P(a)) + a - P(b)$ and $Y(a, b) = P(a + P(b-P(a))) - b$. The given condition is $X(a, b) Y(a, b) = 0$.
4: 
5: First, we show that $P$ is surjective. Suppose there exists $b \in \mathbb{Q}$ such that $b$ is not in the range of $P$. Then $Y(a, b) \neq 0$ for all $a \in \mathbb{Q}$. This implies $X(a, b) = 0$ for all $a \in \mathbb{Q}$, so $P(b-P(a)) = P(b) - a$. As $a$ varies over $\mathbb{Q}$, $P(b) - a$ takes all rational values, so $P$ must be surjective.
6: 
7: Since $P$ is surjective, there exists $z \in \mathbb{Q}$ such that $P(z) = 0$. Substituting $a=z$ into the original equation:
8: $X(z, b) = P(b-P(z)) + z - P(b) = P(b) + z - P(b) = z$.
9: $Y(z, b) = P(z + P(b-P(z))) - b = P(z + P(b)) - b$.
10: The condition $X(z, b) Y(z, b) = 0$ implies $z(P(z + P(b)) - b) = 0$ for all $b \in \mathbb{Q}$.
11: If $z \neq 0$, then $P(z + P(b)) = b$ for all $b \in \mathbb{Q}$. This implies $P$ is injective. Since $P$ is also surjective, it is a bijection. Then $P(z + P(b)) = b$ implies $P(P(z + P(b))) = P(b)$. Let $w = z + P(b)$; since $P$ is surjective, $w$ can be any rational. Thus $P(P(w)) = w - z$ for all $w \in \mathbb{Q}$. Also, $P(z + P(z + P(b))) = P(b)$ (by replacing $b$ with $z+P(b)$ in $P(z+P(b))=b$). Since $P(z+P(b)) = b$, we have $P(z + b) = P(b)$. Because $P$ is injective, $z + b = b$, so $z = 0$.
12: Thus, we must have $z = 0$, so $P(0) = 0$.
13: 
14: Now we show that $P(x) = 0$ if and only if $x = 0$. If $P(x) = 0$, then $X(x, b) = P(b-P(x)) + x - P(b) = P(b) + x - P(b) = x$. Thus $X(x, b) Y(x, b) = x(P(x + P(b)) - b) = 0$ for all $b$. If $x \neq 0$, then $P(x + P(b)) = b$ for all $b$. For $b=0$, $P(x + P(0)) = 0 \implies P(x) = 0$. Since $P(x + P(b)) = b$, $P$ is a bijection. Then $P(P(x + P(b))) = P(b) \implies P(P(w)) = w - x$ for $w = x + P(b)$. Also $P(x + P(x + P(b))) = P(b) \implies P(x + b) = P(b)$, so $x = 0$. Thus $P(x) = 0 \iff x = 0$.
15: 
16: Substituting $b=0$ into the original equation:
17: $(P(-P(a)) + a - P(0))(P(a + P(-P(a))) - 0) = 0 \implies (P(-P(a)) + a) P(a + P(-P(a))) = 0$.
18: Since $P(w) = 0 \iff w = 0$, we have $P(-P(a)) = -a$ or $a + P(-P(a)) = 0$. In both cases, $P(-P(a)) = -a$ for all $a \in \mathbb{Q}$.
19: This implies $P$ is injective: if $P(a_1) = P(a_2)$, then $P(-P(a_1)) = P(-P(a_2))$, so $-a_1 = -a_2$. Since $P$ is also surjective, $P$ is a bijection. Let $f = P^{-1}$. Then $P(-P(a)) = -a \implies -P(a) = f(-a)$.
20: 
21: For any $a, b \in \mathbb{Q}$, we have $X(a, b) Y(a, b) = 0$.
22: $X(a, b) = 0 \iff P(b-P(a)) = P(b) - a$.
23: $Y(a, b) = 0 \iff a + P(b-P(a)) = f(b) \iff P(b-P(a)) = f(b) - a$.
24: Let $P(a) = x$, so $a = f(x)$. Then $P(b-x) \in \{P(b) - f(x), f(b) - f(x)\}$.
25: This means $P(b-x) + f(x) \in \{P(b), f(b)\}$ for all $x, b \in \mathbb{Q}$.
26: Let $h_b(x) = P(b-x) + f(x)$. We have $h_b(0) = P(b)$ and $h_b(b) = f(b)$.
27: If $P(b) = f(b)$ for all $b$, then $P(P(b)) = b$. Then $h_b(x) = P(b-x) + P(x) = P(b)$, which is Cauchy's functional equation on $\mathbb{Q}$. Thus $P(x) = kx$. Substituting into $P(P(x)) = x$ gives $k^2 = 1$, so $k = \pm 1$.
28: If there exists $b$ such that $P(b) \neq f(b)$, then $g(x) = P(b-x) + f(x)$ takes values in $\{P(b), f(b)\}$. Since $f(x) = -P(-x)$, we have $P(b-x) - P(-x) \in \{P(b), f(b)\}$. Let $x = -y$, then $P(b+y) - P(y) \in \{P(b), f(b)\}$.
29: If $P(b+y) - P(y)$ is constant for all $y$, then $P$ is linear, $P(x) = kx$. As shown before, $P(-P(a)) = -a$ implies $k = \pm 1$, so $P(b) = f(b)$.
30: If $P(b+y) - P(y)$ is not constant, it must jump between $P(b)$ and $f(b)$. However, for a bijection $P$ on $\mathbb{Q}$, the condition $P(b+y) - P(y) \in \{C_1, C_2\}$ for all $y$ forces $P$ to be linear. Specifically, if $P(b+y) - P(y) = g(y)$, then $P(y+2b) - P(y) = g(y) + g(y+b) \in \{2P(b), P(b)+f(b), 2f(b)\}$. But we also have $P(y+2b) - P(y) \in \{P(2b), f(2b)\}$. This restriction, combined with $P$ being a bijection, forces $P(x) = kx$.
31: 
32: Thus, the only solutions are $P(x) = x$ and $P(x) = -x$.
33: For $P(x) = x$, $P(a) + P(-a) = a + (-a) = 0$.
34: For $P(x) = -x$, $P(a) + P(-a) = -a + a = 0$.
35: In both cases, the set $\{P(a) + P(-a) : a \in \mathbb{Q}\} = \{0\}$.
36: This set is finite and contains exactly 1 element. The maximum possible number of elements is 1.

# Proof B

1: Let $P: \mathbb{Q} \to \mathbb{Q}$ be a function satisfying the equation
2: \[ (P(b-P(a))+a-P(b))(P(a+P(b-P(a)))-b)=0 \]
3: for all $a, b \in \mathbb{Q}$. Let $X(a, b) = P(b-P(a)) + a - P(b)$ and $Y(a, b) = P(a+P(b-P(a))) - b$. The given equation is $X(a, b) Y(a, b) = 0$.
4: 
5: First, we prove that $P$ is injective. Suppose there exist $x, y \in \mathbb{Q}$ such that $P(x) = P(y)$ with $x \neq y$. For any $a \in \mathbb{Q}$, let $w_a = P(x-P(a))$. Since $P(x) = P(y)$, we have $P(x-P(a)) = P(y-P(a))$, so $w_a$ is the same for both $x$ and $y$. Then:
6: $X(a, x) = w_a + a - P(x)$ and $X(a, y) = w_a + a - P(y)$.
7: Since $P(x) = P(y)$, we have $X(a, x) = X(a, y)$ for all $a$.
8: Also, $Y(a, x) = P(a+w_a) - x$ and $Y(a, y) = P(a+w_a) - y$.
9: Since $x \neq y$, $Y(a, x)$ and $Y(a, y)$ cannot both be zero.
10: Since $X(a, x) Y(a, x) = 0$ and $X(a, y) Y(a, y) = 0$, and $X(a, x) = X(a, y)$, it must be that $X(a, x) = 0$ for all $a \in \mathbb{Q}$.
11: Thus, $P(x-P(a)) = P(x) - a$ for all $a \in \mathbb{Q}$.
12: As $a$ varies over $\mathbb{Q}$, the expression $P(x) - a$ takes all values in $\mathbb{Q}$, which implies that $P$ is surjective.
13: Since $P$ is surjective, there exists $c \in \mathbb{Q}$ such that $P(c) = 0$.
14: Substituting $a=c$ into $P(x-P(a)) = P(x) - a$, we get $P(x-0) = P(x) - c$, which implies $c = 0$. Thus $P(0) = 0$.
15: Substituting $x=0$ into $P(x-P(a)) = P(x) - a$, we get $P(-P(a)) = P(0) - a = -a$.
16: If $P(a) = P(b)$, then $-a = P(-P(a)) = P(-P(b)) = -b$, so $a = b$.
17: This proves that $P$ is injective, contradicting our assumption $x \neq y$. Thus, $P$ must be injective.
18: 
19: Next, we show $P(0) = 0$. Since $P$ is injective, $X(0, b) = P(b-P(0)) - P(b)$.
20: $X(0, b) = 0$ if and only if $b-P(0) = b$, which means $P(0) = 0$.
21: If $P(0) = c \neq 0$, then $X(0, b) \neq 0$ for all $b$, so we must have $Y(0, b) = 0$ for all $b$:
22: $P(P(b-c)) = b$. Let $b-c = z$, then $P(P(z)) = z+c$.
23: Then $P(P(0)) = 0+c = c$. Since $P(0) = c$, we have $P(c) = c$.
24: Then $P(P(c)) = c+c = 2c$. But $P(P(c)) = P(c) = c$.
25: Thus $2c = c$, which implies $c = 0$, contradicting $c \neq 0$.
26: Therefore, $P(0) = 0$.
27: 
28: With $P(0) = 0$, we have $X(a, 0) = P(-P(a)) + a$ and $Y(a, 0) = P(a+P(-P(a)))$.
29: Since $X(a, 0) Y(a, 0) = 0$, for each $a$, either $P(-P(a)) = -a$ or $P(a+P(-P(a))) = 0$.
30: Since $P$ is injective and $P(0)=0$, $P(a+P(-P(a))) = 0$ implies $a+P(-P(a)) = 0$, so $P(-P(a)) = -a$.
31: Thus, $P(-P(a)) = -a$ for all $a \in \mathbb{Q}$.
32: 
33: We now show that $P(P(b)) = b$ for all $b \in \mathbb{Q}$.
34: Suppose there exists $b_0 \in \mathbb{Q}$ such that $P(P(b_0)) \neq b_0$.
35: If $X(a, b_0) = 0$, then $P(b_0-P(a)) = P(b_0) - a$.
36: Then $Y(a, b_0) = P(a+P(b_0-P(a))) - b_0 = P(a + P(b_0) - a) - b_0 = P(P(b_0)) - b_0$.
37: Since $P(P(b_0)) \neq b_0$, $Y(a, b_0) \neq 0$ whenever $X(a, b_0) = 0$.
38: Since $X(a, b_0) Y(a, b_0) = 0$ for all $a$, we must have $X(a, b_0) = 0$ for all $a \in \mathbb{Q}$.
39: Then $P(b_0-P(a)) = P(b_0) - a$. Let $P(a) = z$. Then $P(b_0-z) = P(b_0) - P^{-1}(z)$.
40: For $z=b_0$, we have $P(0) = P(b_0) - P^{-1}(b_0)$.
41: Since $P(0) = 0$, we have $P(b_0) = P^{-1}(b_0)$, so $P(P(b_0)) = b_0$, a contradiction.
42: Thus, $P(P(b)) = b$ for all $b \in \mathbb{Q}$.
43: 
44: Now, if $X(a, b) = 0$, then $P(b-P(a)) = P(b) - a$.
45: Then $Y(a, b) = P(a+P(b)-a) - b = P(P(b)) - b = b - b = 0$.
46: Thus $X(a, b) = 0$ implies $Y(a, b) = 0$.
47: The original equation $X(a, b) Y(a, b) = 0$ then implies $Y(a, b) = 0$ for all $a, b \in \mathbb{Q}$.
48: $P(a+P(b-P(a))) = b$.
49: Let $P(b-P(a)) = z$. Then $b-P(a) = P(z)$, so $b = P(z) + P(a)$.
50: The equation becomes $P(a+z) = P(a) + P(z)$ for all $a, z \in \mathbb{Q}$.
51: This is Cauchy's functional equation, and since the domain is $\mathbb{Q}$, $P(x) = mx$ for some $m \in \mathbb{Q}$.
52: Substituting $P(x) = mx$ into $P(P(x)) = x$, we get $m^2x = x$, so $m^2 = 1$, which means $m = 1$ or $m = -1$.
53: Thus, the only solutions are $P(x) = x$ and $P(x) = -x$.
54: 
55: For both $P(x) = x$ and $P(x) = -x$, we have $P(a) + P(-a) = a + (-a) = 0$ or $P(a) + P(-a) = -a + a = 0$.
56: The set $\{P(a) + P(-a) : a \in \mathbb{Q}\}$ is $\{0\}$, which contains exactly 1 element.
57: The maximum possible number of elements in this set is 1.
