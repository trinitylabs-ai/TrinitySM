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
