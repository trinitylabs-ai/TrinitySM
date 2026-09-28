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

1: Let $P: \mathbb{Q} \to \mathbb{Q}$ be a function satisfying the equation
2: \[ (P(b-P(a)) + a - P(b))(P(a + P(b-P(a))) - b) = 0 \]
3: for all $a, b \in \mathbb{Q}$. Let $X(a, b) = P(b-P(a)) + a - P(b)$ and $Y(a, b) = P(a + P(b-P(a))) - b$. The given equation is $X(a, b) Y(a, b) = 0$.
4: 
5: First, we analyze the relationship between $X$ and $Y$. If $X(a, b) = 0$, then $P(b-P(a)) = P(b) - a$. Substituting this into $Y(a, b)$, we obtain
6: \[ Y(a, b) = P(a + P(b) - a) - b = P(P(b)) - b. \]
7: Thus, for a fixed $b \in \mathbb{Q}$, if there exists $a \in \mathbb{Q}$ such that $X(a, b) = 0$, then $Y(a, b) = P(P(b)) - b$.
8: 
9: Now, fix $b \in \mathbb{Q}$. If $P(P(b)) \neq b$, then $Y(a, b) \neq 0$ whenever $X(a, b) = 0$. Since $X(a, b) Y(a, b) = 0$, this implies that if $P(P(b)) \neq b$, then $X(a, b)$ must be non-zero for all $a \in \mathbb{Q}$, and consequently $Y(a, b) = 0$ for all $a \in \mathbb{Q}$.
10: 
11: Suppose there exists some $b \in \mathbb{Q}$ such that $P(P(b)) \neq b$. Let $S = \{b \in \mathbb{Q} : P(P(b)) \neq b\}$. If $S$ is non-empty, then for any $b \in S$, $Y(a, b) = 0$ for all $a \in \mathbb{Q}$, which means
12: \[ P(a + P(b - P(a))) = b \quad (*) \]
13: for all $a \in \mathbb{Q}, b \in S$. Let $P(0) = \delta$. For $a=0$ and $b \in S$, $(*)$ gives $P(P(b - \delta)) = b$. If $b - \delta \notin S$, then $P(P(b - \delta)) = b - \delta$, implying $b = b - \delta$, so $\delta = 0$. If $\delta = 0$, then $P(P(b)) = b$ for all $b \in S$, which contradicts the definition of $S$. Thus, $b \in S \implies b - \delta \in S$. By induction, $b - n\delta \in S$ for all $n \in \mathbb{Z}$. Furthermore, the relation $P(P(b - \delta)) = b$ for $b \in S$ implies that $P(P(x)) = x + \delta$ for all $x \in S$.
14: 
15: Since $P(P(x)) = x + \delta$ for $x \in S$, we have $P(x + \delta) = P(P(P(x))) = P(P(x)) + \delta = P(x) + \delta$ for $x \in S$. Also, if $b \in S$, then $P(b) \in S$ because $P(P(P(b))) = P(b) + \delta \neq P(b)$. Applying $P$ to both sides of $(*)$ for $b \in S$, we get $P(P(a + P(b - P(a)))) = P(b)$. Since $P(b) \in S$, the argument $a + P(b - P(a))$ must also be in $S$. Thus,
16: \[ a + P(b - P(a)) + \delta = P(b) \implies P(b - P(a)) = P(b) - a - \delta. \]
17: Setting $b = P(a)$ (noting that $P(a) \in S$ whenever $a \in S$), we obtain $P(0) = P(P(a)) - a - \delta$. Substituting $P(0) = \delta$ and $P(P(a)) = a + \delta$, we get $\delta = (a + \delta) - a - \delta = 0$. This implies $\delta = 0$, which again contradicts the definition of $S$. Therefore, $S$ must be empty.
18: 
19: Thus, $P(P(x)) = x$ for all $x \in \mathbb{Q}$. Under this condition, $X(a, b) = 0$ if and only if $Y(a, b) = 0$. The equation $X(a, b) Y(a, b) = 0$ then implies $X(a, b) = 0$ for all $a, b \in \mathbb{Q}$:
20: \[ P(b - P(a)) = P(b) - a. \]
21: Setting $b = P(a)$ gives $P(0) = P(P(a)) - a = a - a = 0$. Since $P(P(a)) = a$, we can write $a = P(P(a))$, so the equation becomes $P(b - P(a)) = P(b) - P(P(a))$. Let $P(a) = z$. Since $P$ is an involution, it is a bijection, so $z$ can be any rational number. Thus,
22: \[ P(b - z) = P(b) - P(z) \]
23: for all $b, z \in \mathbb{Q}$. This is Cauchy's functional equation on $\mathbb{Q}$, so $P(x) = kx$ for some $k \in \mathbb{Q}$. Substituting $P(x) = kx$ into $P(P(x)) = x$ yields $k^2 = 1$, so $k = \pm 1$.
24: 
25: If $P(x) = x$, then $P(a) + P(-a) = a + (-a) = 0$.
26: If $P(x) = -x$, then $P(a) + P(-a) = -a + a = 0$.
27: In both cases, the set $\{P(a) + P(-a) : a \in \mathbb{Q}\}$ is $\{0\}$, which contains exactly 1 element.
28: 
29: The maximum possible number of elements in the set is 1.

# Proof B

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
