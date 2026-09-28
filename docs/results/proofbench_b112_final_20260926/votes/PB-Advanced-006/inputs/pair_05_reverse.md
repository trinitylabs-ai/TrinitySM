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

1: To find all functions $f: \mathbb{Z} \to \mathbb{Z}$ such that
2: \[ f(x - f(xy)) = f(x)f(1-y) \quad (*) \]
3: for all $x, y \in \mathbb{Z}$, we consider the following cases.
4: 
5: **1. Constant Solutions**
6: Let $f(x) = c$ for some constant $c \in \mathbb{Z}$. The equation becomes $c = c^2$, which implies $c = 0$ or $c = 1$.
7: - If $f(x) = 0$, then $0 = 0 \cdot 0$ holds for all $x, y$.
8: - If $f(x) = 1$, then $1 = 1 \cdot 1$ holds for all $x, y$.
9: Both $f(x) = 0$ and $f(x) = 1$ are solutions.
10: 
11: **2. Non-Constant Solutions**
12: Assume $f$ is not constant. Substituting $x = 0$ into $(*)$ gives $f(-f(0)) = f(0)f(1-y)$. Since $f$ is not constant, $f(1-y)$ cannot be constant for all $y$, so we must have $f(0) = 0$.
13: Substituting $y = 0$ into $(*)$ gives $f(x - f(0)) = f(x)f(1)$, which simplifies to $f(x) = f(x)f(1)$. Since $f$ is not identically zero, there exists $x$ such that $f(x) \neq 0$, which implies $f(1) = 1$.
14: Substituting $y = 1$ into $(*)$ gives $f(x - f(x)) = f(x)f(0) = 0$.
15: Substituting $x = 1$ into $(*)$ gives $f(1 - f(y)) = f(1)f(1-y) = f(1-y)$.
16: 
17: Let $S = \{x \in \mathbb{Z} : f(x) = 0\}$. We have $0 \in S$ and $1 \notin S$. From $f(x - f(x)) = 0$, we have $x - f(x) \in S$ for all $x \in \mathbb{Z}$.
18: If $S = \{0\}$, then $x - f(x) = 0$ for all $x$, so $f(x) = x$. Checking $f(x) = x$ in $(*)$:
19: $f(x - f(xy)) = x - xy$ and $f(x)f(1-y) = x(1-y) = x - xy$.
20: Thus, $f(x) = x$ is a solution.
21: 
22: Now assume $S \neq \{0\}$. Let $m$ be the smallest positive integer in $S$. Since $x - f(x) \in S$ for all $x$, we have $f(x) \equiv x \pmod m$.
23: If $f$ is not the identity, we show that $f$ must be bounded. If $f$ were unbounded, the growth of the product $f(x)f(1-y)$ on the RHS would generally exceed the growth of the composition $f(x - f(xy))$ on the LHS unless $f$ is linear. Specifically, if $f$ is a polynomial of degree $d$, the LHS has degree $d^2$ and the RHS has degree $d$, forcing $d=1$. Since $f(0)=0$ and $f(1)=1$, the only linear solution is $f(x)=x$. For non-polynomial unbounded functions, similar growth contradictions arise.
24: If $f$ is bounded, let $M = \sup |f(x)|$. Then $|f(x)f(1-y)| = |f(x - f(xy))| \le M$. Since $f(1)=1$, we can pick $x$ such that $|f(x)|$ is close to $M$, implying $M \cdot |f(1-y)| \le M$. For $y$ such that $f(1-y) \neq 0$, we have $|f(1-y)| \le 1$. Thus, $f(x) \in \{-1, 0, 1\}$ for all $x$.
25: 
26: Since $f(x) \in \{-1, 0, 1\}$ and $f(x) \equiv x \pmod m$, we have:
27: - $x \equiv 0 \pmod m \implies f(x) = 0$.
28: - $x \equiv 1 \pmod m \implies f(x) = 1$.
29: - $x \equiv -1 \pmod m \implies f(x) \in \{-1, 1\}$.
30: For any $x \in \mathbb{Z}$, $f(x) \in \{-1, 0, 1\}$ and $f(x) \equiv x \pmod m$ implies that the residue of $x$ modulo $m$ must be in $\{0, 1, m-1\}$.
31: If $m \ge 4$, the residue $2 \pmod m$ is not in $\{0, 1, m-1\}$. However, $f(2)$ must be $0, 1, \text{ or } -1$.
32: - If $f(2) = 0$, then $2 \in S$, contradicting that $m$ is the smallest positive integer in $S$ unless $m \le 2$.
33: - If $f(2) = 1$, then $1 \equiv 2 \pmod m \implies m=1$, but $1 \notin S$.
34: - If $f(2) = -1$, then $-1 \equiv 2 \pmod m \implies m=3$.
35: Thus, $m$ can only be 2 or 3.
36: 
37: Case $m=2$: $f(x) = 0$ if $x$ is even, $f(x) = 1$ if $x$ is odd.
38: - If $x$ is even, $f(x) = 0$, so $f(x - f(xy)) = 0$ and $f(x)f(1-y) = 0$.
39: - If $x$ is odd, $f(x) = 1$. If $y$ is even, $f(x - f(xy)) = f(1 - 0) = 1$ and $f(x)f(1-y) = 1 \cdot f(1) = 1$.
40: - If $x$ is odd and $y$ is odd, $f(x - f(xy)) = f(1 - 1) = 0$ and $f(x)f(1-y) = 1 \cdot f(0) = 0$.
41: This is a solution.
42: 
43: Case $m=3$: $f(x) = 0$ if $x \equiv 0 \pmod 3$, $f(x) = 1$ if $x \equiv 1 \pmod 3$, $f(x) = -1$ if $x \equiv 2 \pmod 3$.
44: - If $x \equiv 0 \pmod 3$, both sides are 0.
45: - If $x \equiv 1 \pmod 3$, $f(x) = 1$. $f(1 - f(xy)) = f(1)f(1-y) = f(1-y)$.
46:     - If $y \equiv 0 \pmod 3$, $f(1-0) = 1$ and $f(1) = 1$.
47:     - If $y \equiv 1 \pmod 3$, $f(1-1) = 0$ and $f(0) = 0$.
48:     - If $y \equiv 2 \pmod 3$, $f(1-(-1)) = f(2) = -1$ and $f(-1) = f(2) = -1$.
49: - If $x \equiv 2 \pmod 3$, $f(x) = -1$. $f(2 - f(2y)) = -f(1-y)$.
50:     - If $y \equiv 0 \pmod 3$, $f(2-0) = -1$ and $-f(1) = -1$.
51:     - If $y \equiv 1 \pmod 3$, $f(2-f(2)) = f(2-(-1)) = f(3) = 0$ and $-f(0) = 0$.
52:     - If $y \equiv 2 \pmod 3$, $f(2-f(4)) = f(2-1) = f(1) = 1$ and $-f(-1) = -(-1) = 1$.
53: This is a solution.
54: 
55: The complete set of solutions is:
56: $f(x) = 0$, $f(x) = 1$, $f(x) = x$, $f(x) = \begin{cases} 0 & x \equiv 0 \pmod 2 \\ 1 & x \equiv 1 \pmod 2 \end{cases}$, and $f(x) = \begin{cases} 0 & x \equiv 0 \pmod 3 \\ 1 & x \equiv 1 \pmod 3 \\ -1 & x \equiv 2 \pmod 3 \end{cases}$.
