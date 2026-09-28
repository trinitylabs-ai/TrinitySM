# Problem

Find all functions$f:\mathbb{Z}\rightarrow\mathbb{Z}$
 such that the equation
 \[
 f(x-f(xy))=f(x)f(1-y)
 \]
 holds for all $x,y\in\mathbb{Z}$.

# Proof A

1: To find all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that the equation
2: \[ f(x - f(xy)) = f(x)f(1 - y) \quad (*) \]
3: holds for all $x, y \in \mathbb{Z}$, we proceed as follows.
4: 
5: ### 1. Constant Solutions
6: Let $f(n) = c$ for all $n \in \mathbb{Z}$. Substituting into $(*)$:
7: \[ c = c^2 \implies c(c - 1) = 0 \implies c = 0 \text{ or } c = 1. \]
8: Both $f(n) = 0$ and $f(n) = 1$ are solutions.
9: 
10: ### 2. Non-constant Solutions
11: Assume $f$ is not constant. Setting $x = 0$ in $(*)$:
12: \[ f(-f(0)) = f(0)f(1 - y). \]
13: If $f(0) \neq 0$, then $f(1 - y) = \frac{f(-f(0))}{f(0)}$ for all $y \in \mathbb{Z}$, which implies $f$ is constant. Thus, we must have $f(0) = 0$.
14: Setting $y = 0$ in $(*)$:
15: \[ f(x - f(0)) = f(x)f(1) \implies f(x) = f(x)f(1). \]
16: Since $f$ is not identically zero, there exists $x$ such that $f(x) \neq 0$, forcing $f(1) = 1$.
17: Setting $y = 1$ in $(*)$:
18: \[ f(x - f(x)) = f(x)f(0) = 0. \]
19: Setting $x = 1$ in $(*)$:
20: \[ f(1 - f(y)) = f(1)f(1 - y) = f(1 - y). \]
21: 
22: Let $K = \{ n \in \mathbb{Z} \mid f(n) = 0 \}$. We know $0 \in K$.
23: From $f(x - f(x)) = 0$, we have $x - f(x) \in K$ for all $x \in \mathbb{Z}$.
24: If $y \in K$, then $f(1 - y) = f(1 - f(y)) = f(1 - 0) = f(1) = 1$.
25: Then $(1 - y) - f(1 - y) = 1 - y - 1 = -y \in K$. Thus, $y \in K \iff -y \in K$.
26: 
27: **Case A: $K = \{0\}$.**
28: From $x - f(x) \in K$, we have $x - f(x) = 0$ for all $x \in \mathbb{Z}$, so $f(x) = x$.
29: Checking this in $(*)$: $LHS = f(x - xy) = x - xy$ and $RHS = f(x)f(1 - y) = x(1 - y) = x - xy$.
30: So $f(n) = n$ is a solution.
31: 
32: **Case B: $K \neq \{0\}$.**
33: Let $x_0$ be the smallest positive integer in $K$. Since $f(1) = 1$, $x_0 \geq 2$.
34: If $x \in K$, then $f(x - f(xy)) = f(x)f(1 - y) = 0$, so $x - f(xy) \in K$ for all $y \in \mathbb{Z}$.
35: For $x = x_0$, we have $x_0 - f(x_0 y) \in K$ for all $y \in \mathbb{Z}$.
36: If $0 < f(x_0 y) < x_0$, then $0 < x_0 - f(x_0 y) < x_0$, contradicting the minimality of $x_0$.
37: Thus, for all $y$, $f(x_0 y) \notin \{1, 2, \dots, x_0 - 1\}$.
38: Since $x - f(x) \in K$ for all $x$, we have $2 - f(2) \in K$.
39: If $f(2) = 1$, then $1 \in K$, but $x_0 \geq 2$.
40: If $f(2) = 0$, then $x_0 = 2$.
41: If $f(2) = -1$, then $3 \in K$, so $x_0 \leq 3$.
42: If $f(2) \notin \{-1, 0, 1\}$, then $2 - f(2) \in K$. If $2 - f(2) > 0$, then $2 - f(2) \geq x_0$. If $2 - f(2) < 0$, then $f(2) - 2 \geq x_0$.
43: 
44: Subcase B1: $x_0 = 2$.
45: Then $f(2) = 0$. Testing $f(n) = n \pmod 2$ (range $\{0, 1\}$):
46: If $x$ is even, $f(x) = 0$, so $LHS = f(\text{even} - f(xy)) = f(\text{even} - 0) = 0$ and $RHS = 0$.
47: If $x$ is odd, $f(x) = 1$. If $y$ is even, $f(xy) = 0$, $LHS = f(\text{odd} - 0) = 1$, $RHS = 1 \cdot f(\text{odd}) = 1$.
48: If $y$ is odd, $f(xy) = 1$, $LHS = f(\text{odd} - 1) = f(\text{even}) = 0$, $RHS = 1 \cdot f(\text{even}) = 0$.
49: So $f(n) = n \pmod 2$ is a solution.
50: 
51: Subcase B2: $x_0 = 3$.
52: Then $f(1) = 1, f(2) \neq 0, f(3) = 0$.
53: From $2 - f(2) \in K$, since $x_0 = 3$, we must have $2 - f(2) \leq 0$ or $2 - f(2) \geq 3$.
54: If $f(2) = -1$, then $2 - (-1) = 3 \in K$, which is consistent.
55: Testing $f(n) = n \pmod 3$ with range $\{-1, 0, 1\}$:
56: This function is completely multiplicative: $f(xy) = f(x)f(y)$.
57: Also, $f(n) \equiv n \pmod 3$ for all $n$, so $x - f(xy) \equiv x - xy \pmod 3$, which implies $f(x - f(xy)) = f(x - xy)$.
58: Since $f$ is completely multiplicative, $f(x - xy) = f(x(1 - y)) = f(x)f(1 - y)$.
59: Thus, $f(n) = n \pmod 3$ (range $\{-1, 0, 1\}$) is a solution.
60: 
61: If $x_0 > 3$, we already showed that $f(2)$ must be $-1$ to satisfy $2 - f(2) \in K$ (since $f(2)=0 \implies x_0=2$ and $f(2)=1 \implies x_0=1$), but $f(2) = -1 \implies 3 \in K$, contradicting $x_0 > 3$. Thus, no other solutions exist in Case B.
62: 
63: The functions are $f(n) = 0$, $f(n) = 1$, $f(n) = n$, $f(n) = n \pmod 2$ (range $\{0, 1\}$), and $f(n) = n \pmod 3$ (range $\{-1, 0, 1\}$).

# Proof B

1: We seek all functions $f: \mathbb{Z} \to \mathbb{Z}$ such that
2: \[ f(x - f(xy)) = f(x)f(1 - y) \quad (*) \]
3: holds for all $x, y \in \mathbb{Z}$.
4: 
5: **1. Constant Solutions**
6: Let $f(x) = c$ for all $x \in \mathbb{Z}$. Substituting into $(*)$ gives $c = c \cdot c$, so $c^2 - c = 0$, which implies $c = 0$ or $c = 1$.
7: - If $f(x) = 0$, then $f(x - f(xy)) = 0$ and $f(x)f(1 - y) = 0 \cdot 0 = 0$. This is a solution.
8: - If $f(x) = 1$, then $f(x - f(xy)) = 1$ and $f(x)f(1 - y) = 1 \cdot 1 = 1$. This is a solution.
9: 
10: **2. Non-Constant Solutions**
11: Suppose $f$ is not constant.
12: Substituting $y = 1$ into $(*)$ gives $f(x - f(x)) = f(x)f(0)$.
13: Substituting $x = 0$ into $(*)$ gives $f(-f(0)) = f(0)f(1 - y)$.
14: If $f(0) = c \neq 0$, then $f(1 - y) = \frac{f(-c)}{c}$ for all $y \in \mathbb{Z}$, which implies $f$ is a constant function. Since we assumed $f$ is not constant, we must have $f(0) = 0$.
15: Returning to the $y = 1$ equation, $f(0) = 0$ implies $f(x - f(x)) = 0$ for all $x \in \mathbb{Z}$.
16: Substituting $x = 1$ into $(*)$ gives $f(1 - f(y)) = f(1)f(1 - y)$.
17: Let $f(1) = a$. Then $f(1 - f(y)) = a f(1 - y)$.
18: Substituting $y = 0$ into this equation, and using $f(0) = 0$, we get $f(1 - f(0)) = a f(1)$, so $f(1) = a^2$. Thus $a = a^2$, meaning $a \in \{0, 1\}$.
19: If $a = 0$, then $f(1) = 0$. Substituting $y = 0$ into $(*)$ gives $f(x - f(0)) = f(x)f(1)$, so $f(x) = 0$ for all $x$, which is a constant solution.
20: Thus, $f(1) = 1$. The equation $f(1 - f(y)) = a f(1 - y)$ becomes $f(1 - f(y)) = f(1 - y)$.
21: 
22: **3. Analysis of $f(2)$**
23: Let $f(2) = k$. From $f(x - f(x)) = 0$ with $x = 2$, we have $f(2 - k) = 0$.
24: From $f(1 - f(y)) = f(1 - y)$ with $y = 2$, we have $f(1 - k) = f(-1)$.
25: Substituting $y = 2$ into $(*)$ gives $f(x - f(2x)) = f(x)f(-1)$.
26: Let $f(-1) = a$. Then $f(x - f(2x)) = a f(x)$.
27: For $x = 1$, $f(1 - f(2)) = a f(1) \implies f(1 - k) = a$.
28: For $y = -1$ in $f(1 - f(y)) = f(1 - y)$, we have $f(1 - a) = f(2) = k$.
29: 
30: **Case A: $k = 0$**
31: Then $f(2) = 0$. From $f(1 - k) = a$, we have $f(1) = a$, so $a = 1$.
32: Then $f(-1) = 1$. The equation $f(x - f(2x)) = a f(x)$ becomes $f(x - f(2x)) = f(x)$.
33: Testing $f(x) = x \pmod 2$ (with range $\{0, 1\}$):
34: - If $x$ is even, $f(x) = 0$. LHS: $f(x - f(xy)) = f(\text{even} - f(xy))$. If $xy$ is even, $f(xy)=0 \implies f(\text{even})=0$. If $xy$ is odd, $f(xy)=1 \implies f(\text{odd})=1$. However, $f(x)f(1-y) = 0 \cdot f(1-y) = 0$. For this to hold, $xy$ must be even whenever $x$ is even, which is true.
35: - If $x$ is odd, $f(x) = 1$. LHS: $f(x - f(xy))$. If $y$ is even, $xy$ is even, $f(xy)=0 \implies f(\text{odd})=1$. RHS: $1 \cdot f(1-\text{even}) = f(\text{odd}) = 1$. If $y$ is odd, $xy$ is odd, $f(xy)=1 \implies f(\text{odd}-1)=f(\text{even})=0$. RHS: $1 \cdot f(1-\text{odd}) = f(\text{even}) = 0$.
36: Thus, $f(x) = x \pmod 2$ is a solution.
37: 
38: **Case B: $k = 2$**
39: Then $f(2) = 2$. From $f(1 - k) = a$, we have $f(-1) = a$.
40: From $f(1 - a) = k$, we have $f(1 - a) = 2$.
41: If $a = -1$, then $f(2) = 2$, which is consistent.
42: Testing $f(x) = x$:
43: LHS: $f(x - f(xy)) = x - xy$.
44: RHS: $f(x)f(1 - y) = x(1 - y) = x - xy$.
45: Thus, $f(x) = x$ is a solution.
46: 
47: **Case C: $k = -1$**
48: Then $f(2) = -1$. From $f(1 - k) = a$, we have $f(2) = a$, so $a = -1$.
49: Then $f(1 - a) = k \implies f(2) = -1$, which is consistent.
50: Testing $f(x) = x \pmod 3$ with range $\{0, 1, -1\}$:
51: - If $x \equiv 0 \pmod 3$, $f(x) = 0$, so both sides are 0.
52: - If $x \equiv 1 \pmod 3$, $f(x) = 1$, LHS $f(1 - f(y))$, RHS $f(1 - y)$. This holds as $f(1 - f(y)) = f(1 - y)$ for $f(x) = x \pmod 3$.
53: - If $x \equiv 2 \pmod 3$, $f(x) = -1$, LHS $f(2 - f(2y))$, RHS $-f(1 - y)$.
54:   - $y \equiv 0 \pmod 3 \implies f(2 - 0) = -1, -f(1) = -1$.
55:   - $y \equiv 1 \pmod 3 \implies f(2 - f(2)) = f(2 - (-1)) = f(3) = 0, -f(0) = 0$.
56:   - $y \equiv 2 \pmod 3 \implies f(2 - f(4)) = f(2 - 1) = f(1) = 1, -f(-1) = -(-1) = 1$.
57: Thus, $f(x) = x \pmod 3$ (with range $\{0, 1, -1\}$) is a solution.
58: 
59: **4. Exhaustiveness**
60: For any non-constant solution, we have $f(0)=0, f(1)=1$. If $f(x) = x \pmod n$ (balanced range), then the maximum absolute value is $M = \lfloor n/2 \rfloor$. The equation $f(x - f(xy)) = f(x)f(1 - y)$ implies $M^2 \le M$ if the range is fully utilized, so $M \le 1$, which means $n \le 3$. For $n=2$, we get $f(x) = x \pmod 2$. For $n=3$, we get $f(x) = x \pmod 3$. For $f(x) = x$, the range is unbounded.
61: 
62: The solutions are $f(x) = 0$, $f(x) = 1$, $f(x) = x$, $f(x) = \begin{cases} 0 & x \text{ is even} \\ 1 & x \text{ is odd} \end{cases}$, and $f(x) = \begin{cases} 0 & x \equiv 0 \pmod 3 \\ 1 & x \equiv 1 \pmod 3 \\ -1 & x \equiv 2 \pmod 3 \end{cases}$.
