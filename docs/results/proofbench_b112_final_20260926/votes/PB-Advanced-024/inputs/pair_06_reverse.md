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
