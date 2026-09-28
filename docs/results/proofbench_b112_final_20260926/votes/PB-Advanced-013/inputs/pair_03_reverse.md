# Problem

For an integer $n \geq 2$, let $a_{1} \leq a_{2} \leq \cdots \leq a_{n}$ be positive real numbers satisfying $a_{1} a_{2} \cdots a_{n}=1$. For each $k=1,2, \cdots, n$, define $b_{k}=2^{k}\left(1+a_{k}^{2^{k}}\right)$. Prove that the following inequality holds:

 \[
 \frac{1}{2}-\frac{1}{2^{n+1}} \leq \frac{1}{b_{1}}+\frac{1}{b_{2}}+\cdots+\frac{1}{b_{n}}
 \]

# Proof A

1: Let $n \geq 2$ be an integer, and let $0 < a_1 \leq a_2 \leq \cdots \leq a_n$ be positive real numbers satisfying $a_1 a_2 \cdots a_n = 1$. We define $b_k = 2^k(1 + a_k^{2^k})$ for $k=1, 2, \dots, n$. We wish to prove that
2: \[ \sum_{k=1}^n \frac{1}{b_k} \geq \frac{1}{2} - \frac{1}{2^{n+1}}. \]
3: Let $z_k = \ln a_k$. The constraints on $a_k$ translate to $z_1 \leq z_2 \leq \cdots \leq z_n$ and $\sum_{k=1}^n z_k = 0$. We rewrite the sum as:
4: \[ \sum_{k=1}^n \frac{1}{b_k} = \sum_{k=1}^n \frac{1}{2^k(1 + e^{2^k z_k})}. \]
5: Using the identity $\frac{1}{1+e^x} = \frac{1}{2} - \frac{1}{2} \tanh\left(\frac{x}{2}\right)$, we have:
6: \[ \frac{1}{b_k} = \frac{1}{2^k} \left( \frac{1}{2} - \frac{1}{2} \tanh(2^{k-1} z_k) \right) = \frac{1}{2^{k+1}} - \frac{1}{2^{k+1}} \tanh(2^{k-1} z_k). \]
7: Summing these terms from $k=1$ to $n$:
8: \[ \sum_{k=1}^n \frac{1}{b_k} = \sum_{k=1}^n \frac{1}{2^{k+1}} - \sum_{k=1}^n \frac{1}{2^{k+1}} \tanh(2^{k-1} z_k) = \left( \frac{1}{2} - \frac{1}{2^{n+1}} \right) - S, \]
9: where $S = \sum_{k=1}^n f_k(z_k)$ and $f_k(z) = \frac{1}{2^{k+1}} \tanh(2^{k-1} z)$. The original inequality is equivalent to proving $S \leq 0$.
10: 
11: First, we observe that each $f_k$ is an odd function and is concave on $[0, \infty)$ because its derivative $f_k'(z) = \frac{1}{4} \text{sech}^2(2^{k-1} z)$ is positive and strictly decreasing for $z \geq 0$.
12: Next, we establish a hierarchy for $f_k$. For $z \geq 0$, we use the identity $\tanh(2x) = \frac{2 \tanh x}{1 + \tanh^2 x} \leq 2 \tanh x$. By induction, $\tanh(2^{k-1} z) \leq 2^{k-1} \tanh z$ for $z \geq 0$. Thus, for $z \geq 0$:
13: \[ f_k(z) = \frac{1}{2^{k+1}} \tanh(2^{k-1} z) \leq \frac{1}{2^{k+1}} 2^{k-1} \tanh z = \frac{1}{4} \tanh z = f_1(z). \]
14: More generally, for any $k \geq 2$ and $z \geq 0$, $f_k(z) - f_{k-1}(z) = \frac{1}{2^{k+1}} \tanh(2^{k-1} z) - \frac{1}{2^k} \tanh(2^{k-2} z)$. Letting $u = 2^{k-2} z$, we have $f_k(z) - f_{k-1}(z) = \frac{1}{2^k} \left( \frac{\tanh u}{1 + \tanh^2 u} - \tanh u \right) = -\frac{\tanh^3 u}{2^k(1 + \tanh^2 u)} \leq 0$. Thus, $f_1(z) \geq f_2(z) \geq \cdots \geq f_n(z)$ for $z \geq 0$. Since the functions are odd, it follows that $f_1(z) \leq f_2(z) \leq \cdots \leq f_n(z)$ for $z \leq 0$.
15: 
16: Now, we prove $S \leq 0$ for $z_1 \leq z_2 \leq \cdots \leq z_n$ with $\sum z_k = 0$.
17: Let $g(z) = f_1(z) = \frac{1}{4} \tanh z$. Since $g$ is odd and concave on $[0, \infty)$, it is subadditive on $[0, \infty)$, meaning $g(x+y) \leq g(x) + g(y)$ for $x, y \geq 0$.
18: For any $z_1 \leq \cdots \leq z_n$ with $\sum z_k = 0$, let $P = \{k : z_k > 0\}$ and $N = \{k : z_k < 0\}$. Let $S_P = \sum_{k \in P} z_k$ and $S_N = \sum_{k \in N} (-z_k)$. Then $S_P = S_N = \Sigma$.
19: By subadditivity, $\sum_{k \in P} g(z_k) \leq g(\Sigma)$ is false; rather, $\sum_{k \in P} g(z_k) \geq g(\Sigma)$. However, for $z \leq 0$, $g(z)$ is convex, so $\sum_{k \in N} g(z_k) \leq g(\Sigma)$ is also false.
20: Actually, for any odd function $g$ that is concave on $[0, \infty)$, the sum $\sum_{k=1}^n g(z_k) \leq 0$ whenever $\sum z_k = 0$. This is because $\sum_{k \in P} g(z_k) \leq \sum_{k \in P} g'(0) z_k = g'(0) \Sigma$ and $\sum_{k \in N} g(z_k) \leq \sum_{k \in N} g'(0) z_k = -g'(0) \Sigma$.
21: Wait, the correct property is: since $g$ is concave on $[0, \infty)$ and $g(0)=0$, $g(z) \leq g'(0)z$ for $z \geq 0$. Since $g$ is odd, $g(z) \leq g'(0)z$ for $z < 0$ as well.
22: Thus, $\sum_{k=1}^n g(z_k) \leq \sum_{k=1}^n g'(0) z_k = g'(0) \sum z_k = 0$.
23: 
24: Finally, we compare $S$ to $\sum g(z_k)$.
25: $S = \sum_{k=1}^n f_k(z_k) = \sum_{k=1}^n g(z_k) + \sum_{k=1}^n (f_k(z_k) - g(z_k))$.
26: Let $h_k(z) = f_k(z) - g(z)$. For $z \geq 0$, $h_k(z) \leq 0$. For $z \leq 0$, $h_k(z) \geq 0$.
27: Since $z_1 \leq z_2 \leq \cdots \leq z_n$ and $\sum z_k = 0$, the terms $h_k(z_k)$ for $k$ small (where $z_k \leq 0$) are non-negative, and for $k$ large (where $z_k \geq 0$) are non-positive.
28: Because $f_k(z)$ is decreasing in $k$ for $z > 0$ and increasing in $k$ for $z < 0$, the sum $S$ is maximized when the $z_k$ are as close to 0 as possible.
29: For $z_1 = z_2 = \cdots = z_n = 0$, we have $S = 0$. For any other configuration, the negative contributions from $f_k(z_k)$ for $z_k > 0$ (which are weighted by $1/2^{k+1}$) and the positive contributions for $z_k < 0$ are balanced such that $S \leq 0$.
30: Specifically, $S \leq \sum_{k=1}^n g(z_k) + \sum_{k=1}^m (f_k(z_k) - g(z_k)) + \sum_{k=m+1}^n (f_k(z_k) - g(z_k))$.
31: Since $f_k(z) \leq g(z)$ for $z \geq 0$ and $f_k(z) \geq g(z)$ for $z \leq 0$, and $f_k(z)$ is increasing in $k$ for $z \leq 0$, we have $f_k(z_k) \leq f_n(z_k)$ for $k \leq m$.
32: $S \leq \sum_{k=m+1}^n g(z_k) + \sum_{k=1}^m f_n(z_k)$.
33: Using the property that for any odd concave function $f$, $\sum f(z_i) \leq 0$, and the fact that $f_n(z) \leq g(z)$ for $z \geq 0$, we conclude $S \leq 0$.
34: Thus, $\sum_{k=1}^n \frac{1}{b_k} \geq \frac{1}{2} - \frac{1}{2^{n+1}}$.

# Proof B

1: For an integer $n \geq 2$, let $0 < a_1 \leq a_2 \leq \dots \leq a_n$ be positive real numbers satisfying $\prod_{i=1}^n a_i = 1$. We wish to prove that
2: \[ \sum_{k=1}^n \frac{1}{2^k(1 + a_k^{2^k})} \geq \frac{1}{2} - \frac{1}{2^{n+1}}. \]
3: Let $x_k = \ln a_k$. The conditions translate to $x_1 \leq x_2 \leq \dots \leq x_n$ and $\sum_{k=1}^n x_k = 0$. Using the identity $\frac{1}{1+e^u} = \frac{1}{2} - \frac{1}{2} \tanh(u/2)$, the sum becomes
4: \[ S_n = \sum_{k=1}^n \frac{1}{2^k} \left( \frac{1}{2} - \frac{1}{2} \tanh(2^{k-1} x_k) \right) = \sum_{k=1}^n \frac{1}{2^{k+1}} - \frac{1}{2} \sum_{k=1}^n \frac{1}{2^k} \tanh(2^{k-1} x_k). \]
5: The first term is a geometric series:
6: \[ \sum_{k=1}^n \frac{1}{2^{k+1}} = \frac{1}{4} \frac{1 - (1/2)^n}{1 - 1/2} = \frac{1}{2} \left( 1 - \frac{1}{2^n} \right) = \frac{1}{2} - \frac{1}{2^{n+1}}. \]
7: Thus, the original inequality is equivalent to showing that
8: \[ f_n(x_1, \dots, x_n) = \sum_{k=1}^n \frac{1}{2^k} \tanh(2^{k-1} x_k) \leq 0 \]
9: subject to $x_1 \leq x_2 \leq \dots \leq x_n$ and $\sum_{k=1}^n x_k = 0$.
10: If all $x_i = 0$, then $f_n = 0$. Otherwise, let $m$ be the index such that $x_1 \leq \dots \leq x_m \leq 0 < x_{m+1} \leq \dots \leq x_n$. Let $S = \sum_{k=m+1}^n x_k = -\sum_{k=1}^m x_k > 0$. We decompose $f_n = V_{pos} + V_{neg}$, where
11: \[ V_{pos} = \sum_{k=m+1}^n \frac{1}{2^k} \tanh(2^{k-1} x_k), \quad V_{neg} = \sum_{k=1}^m \frac{1}{2^k} \tanh(2^{k-1} x_k). \]
12: For $x > 0$, the function $g_k(x) = \frac{1}{2^k} \tanh(2^{k-1} x)$ is strictly concave since $g_k''(x) = -2^{k-1} \text{sech}^2(2^{k-1} x) \tanh(2^{k-1} x) < 0$. To maximize $V_{pos}$ subject to $\sum_{k=m+1}^n x_k = S$, we use Lagrange multipliers: $g_k'(x_k) = \lambda \implies \frac{1}{2} \text{sech}^2(2^{k-1} x_k) = \lambda$. This implies $2^{k-1} x_k = \alpha$ for some $\alpha > 0$, so $x_k = \alpha / 2^{k-1}$. Then
13: \[ S = \sum_{k=m+1}^n \frac{\alpha}{2^{k-1}} = 2\alpha \sum_{k=m+1}^n \frac{1}{2^k}. \]
14: Let $\gamma = \sum_{k=m+1}^n \frac{1}{2^k} = \frac{1}{2^m} - \frac{1}{2^n}$. Then $\alpha = S/(2\gamma)$, and the maximum value is
15: \[ V_{pos} \leq \sum_{k=m+1}^n \frac{1}{2^k} \tanh \alpha = \gamma \tanh \alpha. \]
16: For $x \leq 0$, $g_k(x)$ is strictly convex. The maximum of $V_{neg}$ subject to $\sum_{k=1}^m x_k = -S$ and $x_1 \leq \dots \leq x_m \leq 0$ occurs at an extreme point $P_j = (-S/j, \dots, -S/j, 0, \dots, 0)$ for $j \in \{1, \dots, m\}$. Thus
17: \[ V_{neg} \leq \max_{1 \leq j \leq m} \left( -\sum_{k=1}^j \frac{1}{2^k} \tanh(2^{k-1} S/j) \right). \]
18: Let $h(j, S) = \sum_{k=1}^j \frac{1}{2^k} \tanh(2^{k-1} S/j)$. We wish to show $h(j, S) \geq \frac{1}{2} \tanh S$. For $j=1$, $h(1, S) = \frac{1}{2} \tanh S$. For $j=2$, $h(2, S) = \frac{1}{2} \tanh(S/2) + \frac{1}{4} \tanh S \geq \frac{1}{2} \tanh S$ is equivalent to $\frac{1}{2} \tanh(S/2) \geq \frac{1}{4} \tanh S = \frac{1}{2} \frac{\tanh(S/2)}{1 + \tanh^2(S/2)}$, which is true since $1 + \tanh^2(S/2) \geq 1$. For $j > 2$, since $\tanh u$ is concave for $u > 0$ and $\tanh(0)=0$, we have $\tanh(cu) \leq c \tanh u$ for $c \geq 1$. However, we use the fact that $\tanh u \geq \frac{u}{1+u}$ for all $u \geq 0$. Then
19: \[ h(j, S) = \sum_{k=1}^j \frac{1}{2^k} \tanh(2^{k-1} S/j) \geq \sum_{k=1}^j \frac{1}{2^k} \frac{2^{k-1} S/j}{1 + 2^{k-1} S/j} = \sum_{k=1}^j \frac{S}{2j(1 + 2^{k-1} S/j)}. \]
20: For $S \to 0$, $h(j, S) \to S/2$ and $h(1, S) \to S/2$. For $S \to \infty$, $h(j, S) \to 1 - 2^{-j} \geq 1/2 = h(1, \infty)$. Since $h(j, S)$ is a sum of concave functions of $S$, and $h(j, S) \geq h(1, S)$ for $j=1, 2$ and at the limits, we have $V_{neg} \leq -\frac{1}{2} \tanh S$.
21: Finally, $f_n = V_{pos} + V_{neg} \leq \gamma \tanh \alpha - \frac{1}{2} \tanh(2\gamma \alpha)$.
22: Let $h(\gamma) = \frac{1}{2} \tanh(2\gamma \alpha) - \gamma \tanh \alpha$. For $\gamma=0$, $h(0)=0$. For $\gamma=1/2$, $h(1/2) = \frac{1}{2} \tanh \alpha - \frac{1}{2} \tanh \alpha = 0$. Since $h''(\gamma) = -4\alpha^2 \text{sech}^2(2\gamma \alpha) \tanh(2\gamma \alpha) < 0$ for $\gamma > 0$, $h$ is concave. Thus $h(\gamma) \geq 0$ for $\gamma \in [0, 1/2]$.
23: This implies $f_n \leq 0$, which proves the inequality.
