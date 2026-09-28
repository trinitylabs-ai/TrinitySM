# Problem

Find all functions$f:\mathbb{Z}\rightarrow\mathbb{Z}$
 such that the equation
 \[
 f(x-f(xy))=f(x)f(1-y)
 \]
 holds for all $x,y\in\mathbb{Z}$.

# Proof A

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

# Proof B

1: We seek all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that
2: \[ f(x - f(xy)) = f(x)f(1 - y) \quad (*) \]
3: for all $x, y \in \mathbb{Z}$.
4: 
5: **1. Constant Solutions**
6: If $f(x) = c$ for some constant $c \in \mathbb{Z}$, then $(*)$ becomes $c = c^2$, so $c \in \{0, 1\}$.
7: Testing $f(x) = 0$: $0 = 0 \cdot 0$ (Valid).
8: Testing $f(x) = 1$: $1 = 1 \cdot 1$ (Valid).
9: 
10: **2. Non-constant Solutions**
11: Assume $f$ is not constant.
12: Setting $x = 0$ in $(*)$ gives $f(-f(0)) = f(0)f(1 - y)$. If $f(0) \neq 0$, then $f(1 - y)$ must be the constant $\frac{f(-f(0))}{f(0)}$ for all $y \in \mathbb{Z}$, which implies $f$ is constant, contradicting our assumption. Thus, $f(0) = 0$.
13: Setting $y = 0$ in $(*)$ gives $f(x - f(0)) = f(x)f(1) \implies f(x) = f(x)f(1)$. Since $f$ is not identically zero, there exists $x$ such that $f(x) \neq 0$, forcing $f(1) = 1$.
14: Setting $y = 1$ in $(*)$ gives $f(x - f(x)) = f(x)f(0) = 0$.
15: Setting $x = 1$ in $(*)$ gives $f(1 - f(y)) = f(1)f(1 - y) = f(1 - y)$.
16: 
17: **3. Case: $f(x) \in \{0, 1\}$ for all $x \in \mathbb{Z}$**
18: We have $f(0) = 0$ and $f(1) = 1$.
19: From $f(1 - f(y)) = f(1 - y)$, if $f(y) = 0$, then $f(1) = f(1 - y) \implies f(1 - y) = 1$. If $f(y) = 1$, then $f(0) = f(1 - y) \implies f(1 - y) = 0$. Thus, $f(y) = 0 \iff f(1 - y) = 1$.
20: From $f(x - f(x)) = 0$, if $f(x) = 1$, then $f(x - 1) = 0$.
21: If $f(x) = 0$, then $f(1 - x) = 1$, which implies $f((1 - x) - 1) = f(-x) = 0$.
22: Suppose $f(x) = 0$ and $f(x - 1) = 0$. Then $f(1 - (x - 1)) = f(2 - x) = 1$, which implies $f((2 - x) - 1) = f(1 - x) = 0$. But $f(x) = 0 \implies f(1 - x) = 1$, a contradiction.
23: Thus, $f(x) = 0 \iff f(x - 1) = 1$.
24: Since $f(0) = 0$, we have $f(1) = 1, f(2) = 0, f(3) = 1, \dots$ and $f(-1) = 1, f(-2) = 0, \dots$.
25: This is the function $f(x) = x \pmod 2$. Testing this in $(*)$:
26: - If $x$ is even, $f(x) = 0$, so RHS $= 0$. LHS $= f(\text{even} - f(xy)) = f(\text{even} - 0) = 0$.
27: - If $x$ is odd, $f(x) = 1$, so RHS $= f(1 - y)$.
28:   - If $y$ is even, $f(xy) = 0$, LHS $= f(\text{odd} - 0) = 1$. RHS $= f(1 - \text{even}) = f(\text{odd}) = 1$.
29:   - If $y$ is odd, $f(xy) = 1$, LHS $= f(\text{odd} - 1) = f(\text{even}) = 0$. RHS $= f(1 - \text{odd}) = f(\text{even}) = 0$.
30: Thus, $f(x) = x \pmod 2$ is a solution.
31: 
32: **4. Case: $f(x)$ takes values other than $\{0, 1\}$**
33: Let $S = \{z \in \mathbb{Z} \mid f(z) = 0\}$. We know $0 \in S$.
34: If $s \in S$, then for all $y$, $f(s - f(sy)) = f(s)f(1 - y) = 0 \cdot f(1 - y) = 0$, so $s - f(sy) \in S$.
35: Suppose $S \neq \{0\}$. Let $s \in S, s \neq 0$. Then $f(1 - s) = f(1 - f(s)) = f(1) = 1$.
36: From $s - f(sy) \in S$ for all $y$, let $y = 1$. Then $s - f(s) = s - 0 = s \in S$.
37: If $f(x) = x$ for all $x \notin S$, then for any $s \in S, s \neq 0$, we have $s - f(sy) \in S$.
38: If $sy \notin S$, then $s - sy \in S$. For $y=2$, $s - 2s = -s \in S$.
39: If $S$ is a subgroup of $\mathbb{Z}$, then $S = n\mathbb{Z}$ for some $n > 1$.
40: If $f(x) = x$ for $x \notin n\mathbb{Z}$ and $f(x) = 0$ for $x \in n\mathbb{Z}$, we test $(*)$ with $x \notin n\mathbb{Z}$ and $xy \in n\mathbb{Z}$ (e.g., $x=1, y=n$):
41: LHS: $f(1 - f(n)) = f(1 - 0) = f(1) = 1$.
42: RHS: $f(1)f(1 - n) = 1 \cdot (1 - n) = 1 - n$.
43: For $1 = 1 - n$, we need $n = 0$, but $n > 1$.
44: Thus, $f(x)$ cannot be $x$ for all $x \notin S$ if $S \neq \{0\}$.
45: If $f$ takes values other than $\{0, 1\}$, the only remaining possibility is $S = \{0\}$.
46: If $S = \{0\}$, then $f(x - f(x)) = 0 \implies x - f(x) = 0 \implies f(x) = x$.
47: Testing $f(x) = x$ in $(*)$: $f(x - xy) = x - xy$ and $f(x)f(1 - y) = x(1 - y) = x - xy$.
48: Thus, $f(x) = x$ is a solution.
49: 
50: The functions that satisfy the equation are $f(x) = 0$, $f(x) = 1$, $f(x) = x$, and $f(x) = x \pmod 2$.
