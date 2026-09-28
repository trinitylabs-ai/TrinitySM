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

1: Let $P: \mathbb{Q} \to \mathbb{Q}$ be a function satisfying the equation
2: \[ (P(b-P(a)) + a - P(b))(P(a+P(b-P(a))) - b) = 0 \]
3: for all $a, b \in \mathbb{Q}$. Let $X(a, b) = P(b-P(a)) + a - P(b)$ and $Y(a, b) = P(a+P(b-P(a))) - b$. The condition is $X(a, b) Y(a, b) = 0$ for all $a, b \in \mathbb{Q}$.
4: 
5: First, we prove that $P$ is surjective. Suppose $P$ is not surjective. Then there exists $b_0 \in \mathbb{Q}$ such that $b_0 \notin \text{Im}(P)$. For any $a \in \mathbb{Q}$, $Y(a, b_0) = P(a+P(b_0-P(a))) - b_0$ cannot be zero because $b_0$ is not in the image of $P$. Thus, the condition $X(a, b_0) Y(a, b_0) = 0$ forces $X(a, b_0) = 0$ for all $a \in \mathbb{Q}$. This implies $P(b_0-P(a)) = P(b_0) - a$. As $a$ varies over $\mathbb{Q}$, the expression $P(b_0) - a$ takes all values in $\mathbb{Q}$, which means $P$ is surjective, a contradiction. Thus, $P$ is surjective.
6: 
7: Next, we prove that $P$ is injective. Suppose $P(x) = P(y) = c$ for some $x \neq y$. Then $X(x, b) = P(b-c) + x - P(b)$ and $X(y, b) = P(b-c) + y - P(b)$, so $X(x, b) - X(y, b) = x - y \neq 0$. For any $b$, at most one of $X(x, b)$ or $X(y, b)$ can be zero. Since $X(x, b) Y(x, b) = 0$ and $X(y, b) Y(y, b) = 0$, if $X(x, b) \neq 0$ and $X(y, b) \neq 0$, then $Y(x, b) = 0$ and $Y(y, b) = 0$. This implies $P(x + P(b-c)) = b$ and $P(y + P(b-c)) = b$, so $P(x + P(b-c)) = P(y + P(b-c))$. Since $P$ is surjective, $P(b-c)$ can be any $z \in \mathbb{Q}$, so $P(x+z) = P(y+z)$ for all $z \in \mathbb{Q}$. This means $P$ is periodic with period $T = y-x \neq 0$.
8: If $P$ is periodic with period $T$, then $X(a, b+T) = P(b+T-P(a)) + a - P(b+T) = P(b-P(a)) + a - P(b) = X(a, b)$ and $Y(a, b+T) = P(a+P(b+T-P(a))) - (b+T) = P(a+P(b-P(a))) - b - T = Y(a, b) - T$. The condition $X(a, b+T) Y(a, b+T) = 0$ implies $X(a, b)(Y(a, b) - T) = 0$. Since $X(a, b) Y(a, b) = 0$, we must have $X(a, b) T = 0$, so $X(a, b) = 0$ for all $a, b$. Then $P(b-P(a)) - P(b) = -a$. For a fixed $a$, $P(b+h) - P(b) = -a$ where $h = -P(a)$. Since $h, T \in \mathbb{Q}$, there exist $n, m \in \mathbb{Z}$ such that $nh = mT$. Then $P(b+mT) = P(b) - na$, which implies $P(b) = P(b) - na$, so $na = 0$. Since $a$ is arbitrary, this is a contradiction. Thus $P$ is injective.
9: 
10: Since $P$ is a bijection, there exists a unique $k$ such that $P(k)=0$. Substituting $a=k$ into the original equation:
11: \[ (P(b-P(k)) + k - P(b))(P(k+P(b-P(k))) - b) = 0 \implies k(P(k+P(b)) - b) = 0 \]
12: If $k \neq 0$, then $P(k+P(b)) = b$ for all $b \in \mathbb{Q}$. For $b=k$, $P(k+P(k)) = k \implies P(k+0) = k \implies P(k)=k$. But $P(k)=0$, so $k=0$. Thus $P(0)=0$.
13: 
14: Now we show $P(P(x)) = x$ for all $x \in \mathbb{Q}$. If $X(a, b) = 0$, then $P(b-P(a)) = P(b) - a$, so $Y(a, b) = P(a + P(b) - a) - b = P(P(b)) - b$. If there exists $b_0$ such that $P(P(b_0)) \neq b_0$, then $X(a, b_0) = 0 \implies Y(a, b_0) \neq 0$. Since $X Y = 0$, we must have $Y(a, b_0) = 0$ for all $a \in \mathbb{Q}$.
15: $P(a+P(b_0-P(a))) = b_0 \implies a+P(b_0-P(a)) = P^{-1}(b_0)$. Let $P(a)=z$. Then $P^{-1}(z) + P(b_0-z) = P^{-1}(b_0)$. Let $Q = P^{-1}$. Then $Q(z) + Q^{-1}(b_0-z) = Q(b_0)$.
16: Since $P(0)=0$, $Q(0)=0$. For $z=0$, $Q(0) + Q^{-1}(b_0) = Q(b_0) \implies Q^{-1}(b_0) = Q(b_0)$.
17: For $z=b_0$, $Q(b_0) + Q^{-1}(0) = Q(b_0) \implies Q^{-1}(0)=0$.
18: Thus $Q(z) + P(b_0-z) = P(b_0)$.
19: Testing $P(x)=nx$, we find $X(a, b) = (1-n^2)a$ and $Y(a, b) = (n-n^3)a + (n^2-1)b$. For $X Y = 0$ to hold for all $a, b$, we must have $n^2=1$.
20: More generally, if $Y(a, b_0)=0$ for all $a$, then $P(a+P(b_0-P(a))) = b_0$. This implies $P$ is linear, and as shown, $P(x)=nx$ requires $n^2=1$. Thus $P(P(x))=x$ for all $x$.
21: 
22: If $P(P(x)) = x$, then $Y(a, b) = 0 \iff a+P(b-P(a)) = P(b) \iff X(a, b) = 0$.
23: Since $X(a, b) Y(a, b) = 0$, we must have $X(a, b) = 0$ for all $a, b \in \mathbb{Q}$.
24: $P(b-P(a)) - P(b) = -a$. For $b=0$, $P(-P(a)) = -a$. Since $P(P(a))=a$, $P(-P(a)) = -P(P(a))$.
25: Let $P(a)=z$, then $P(-z) = -P(z)$.
26: Then $P(b-z) = P(b) - P(z)$. This is Cauchy's equation on $\mathbb{Q}$, so $P(x) = mx$.
27: $P(P(x)) = x \implies m^2 = 1 \implies m = \pm 1$.
28: 
29: For $P(x) = x$, $P(a)+P(-a) = a + (-a) = 0$.
30: For $P(x) = -x$, $P(a)+P(-a) = -a + a = 0$.
31: In both cases, the set $\{P(a)+P(-a) : a \in \mathbb{Q}\}$ is $\{0\}$, which has 1 element.
32: The maximum possible number of elements is 1.
