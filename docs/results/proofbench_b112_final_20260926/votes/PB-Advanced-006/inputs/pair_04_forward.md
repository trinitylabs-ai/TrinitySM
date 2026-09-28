# Problem

Find all functions$f:\mathbb{Z}\rightarrow\mathbb{Z}$
 such that the equation
 \[
 f(x-f(xy))=f(x)f(1-y)
 \]
 holds for all $x,y\in\mathbb{Z}$.

# Proof A

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
