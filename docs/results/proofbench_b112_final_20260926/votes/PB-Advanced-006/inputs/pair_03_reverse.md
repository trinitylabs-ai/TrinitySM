# Problem

Find all functions$f:\mathbb{Z}\rightarrow\mathbb{Z}$
 such that the equation
 \[
 f(x-f(xy))=f(x)f(1-y)
 \]
 holds for all $x,y\in\mathbb{Z}$.

# Proof A

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

# Proof B

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
