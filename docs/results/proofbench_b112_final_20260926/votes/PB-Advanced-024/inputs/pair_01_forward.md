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

# Proof B

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
