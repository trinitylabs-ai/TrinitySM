# Problem

For an integer $n \geq 2$, let $a_{1} \leq a_{2} \leq \cdots \leq a_{n}$ be positive real numbers satisfying $a_{1} a_{2} \cdots a_{n}=1$. For each $k=1,2, \cdots, n$, define $b_{k}=2^{k}\left(1+a_{k}^{2^{k}}\right)$. Prove that the following inequality holds:

 \[
 \frac{1}{2}-\frac{1}{2^{n+1}} \leq \frac{1}{b_{1}}+\frac{1}{b_{2}}+\cdots+\frac{1}{b_{n}}
 \]

# Proof A

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

# Proof B

1: For an integer $n \geq 2$, let $0 < a_{1} \leq a_{2} \leq \cdots \leq a_{n}$ be real numbers satisfying $a_{1} a_{2} \cdots a_{n}=1$. We wish to prove that
2: \[ \sum_{k=1}^{n} \frac{1}{b_{k}} \geq \frac{1}{2}-\frac{1}{2^{n+1}}, \quad \text{where } b_{k}=2^{k}\left(1+a_{k}^{2^{k}}\right). \]
3: First, we observe that
4: \[ \sum_{k=1}^{n} \frac{1}{2^{k+1}} = \frac{1}{4} \left( \frac{1 - (1/2)^n}{1 - 1/2} \right) = \frac{1}{2} \left( 1 - \frac{1}{2^n} \right) = \frac{1}{2} - \frac{1}{2^{n+1}}. \]
5: Thus, the inequality is equivalent to showing that
6: \[ S = \sum_{k=1}^{n} \left( \frac{1}{2^{k}(1+a_{k}^{2^{k}})} - \frac{1}{2^{k+1}} \right) \geq 0. \]
7: Let $y_{k} = \ln a_{k}$. The conditions $a_{1} \leq \cdots \leq a_{n}$ and $\prod a_{k} = 1$ imply $y_{1} \leq \cdots \leq y_{n}$ and $\sum_{k=1}^{n} y_{k} = 0$. We rewrite the terms of the sum as
8: \[ f_{k}(y) = \frac{1}{2^{k}(1+e^{2^{k} y})} - \frac{1}{2^{k+1}} = \frac{2 - (1+e^{2^{k} y})}{2^{k+1}(1+e^{2^{k} y})} = \frac{1 - e^{2^{k} y}}{2^{k+1}(1+e^{2^{k} y})}. \]
9: Using the identity $\tanh(x) = \frac{e^{2x}-1}{e^{2x}+1}$, we have
10: \[ f_{k}(y) = -\frac{1}{2^{k+1}} \tanh(2^{k-1} y). \]
11: Let $g(z) = -\frac{1}{4} \tanh(z)$, $w_{k} = \frac{1}{2^{k-1}}$, and $z_{k} = 2^{k-1} y_{k}$. Then
12: \[ w_{k} g(z_{k}) = \frac{1}{2^{k-1}} \left( -\frac{1}{4} \tanh(2^{k-1} y_{k}) \right) = -\frac{1}{2^{k+1}} \tanh(2^{k-1} y_{k}) = f_{k}(y). \]
13: The constraint $\sum y_{k} = 0$ is equivalent to $\sum_{k=1}^{n} w_{k} z_{k} = \sum_{k=1}^{n} 2^{-(k-1)} 2^{k-1} y_{k} = \sum_{k=1}^{n} y_{k} = 0$.
14: The sum becomes $S = \sum_{k=1}^{n} w_{k} g(z_{k})$.
15: Since $y_{k}$ is non-decreasing, there exists an index $m \in \{1, \dots, n\}$ such that $y_{1} \leq \cdots \leq y_{m} \leq 0 < y_{m+1} \leq \cdots \leq y_{n}$. (If all $y_{k}=0$, then $S=0$. If all $y_{k} \leq 0$, then $\sum y_{k} = 0$ implies all $y_{k} = 0$).
16: Let $\mathcal{N} = \{1, \dots, m\}$ and $\mathcal{P} = \{m+1, \dots, n\}$.
17: Let $X = \sum_{k \in \mathcal{P}} w_{k} z_{k}$. Since $z_{k} > 0$ for $k \in \mathcal{P}$, we have $X > 0$.
18: Then $\sum_{k \in \mathcal{N}} w_{k} z_{k} = -X$.
19: The second derivative of $g(z)$ is $g''(z) = \frac{1}{2} \text{sech}^2(z) \tanh(z)$. Thus, $g$ is convex on $[0, \infty)$ and concave on $(-\infty, 0]$.
20: By Jensen's Inequality, for the positive terms:
21: \[ \sum_{k \in \mathcal{P}} w_{k} g(z_{k}) \geq W_{P} g\left( \frac{\sum_{k \in \mathcal{P}} w_{k} z_{k}}{W_{P}} \right) = W_{P} g(X/W_{P}), \]
22: where $W_{P} = \sum_{k \in \mathcal{P}} w_{k}$.
23: For the negative terms, since $g$ is concave on $(-\infty, 0]$, the sum $\sum_{k \in \mathcal{N}} w_{k} g(z_{k})$ subject to $\sum_{k \in \mathcal{N}} w_{k} z_{k} = -X$ and $z_{k} \leq 0$ is minimized at the extreme points of the constraint set. These occur when $z_{j} = -X/w_{j}$ for some $j \in \mathcal{N}$ and $z_{k} = 0$ for $k \neq j$.
24: The value at such a point is $w_{j} g(-X/w_{j}) + \sum_{k \neq j} w_{k} g(0) = w_{j} g(-X/w_{j})$.
25: Let $h(w) = w g(-X/w) = \frac{w}{4} \tanh(X/w)$.
26: The derivative is $h'(w) = \frac{1}{4} \left( \tanh(X/w) - \frac{X}{w} \text{sech}^2(X/w) \right)$.
27: Let $u = X/w > 0$. The expression $\tanh u - u \text{sech}^2 u$ is positive for $u > 0$ because its derivative is $2u \text{sech}^2 u \tanh u > 0$ and it vanishes at $u=0$. Thus, $h(w)$ is strictly increasing for $w > 0$.
28: The minimum of $w_{j} g(-X/w_{j})$ for $j \in \mathcal{N}$ occurs at the smallest weight $w_{m} = 2^{-(m-1)}$.
29: Hence, $\sum_{k \in \mathcal{N}} w_{k} g(z_{k}) \geq h(w_{m})$.
30: Combining these bounds, we have
31: \[ S \geq h(w_{m}) + W_{P} g(X/W_{P}) = h(w_{m}) - h(W_{P}). \]
32: We calculate $W_{P} = \sum_{k=m+1}^{n} \frac{1}{2^{k-1}} = \frac{1}{2^{m}} + \cdots + \frac{1}{2^{n-1}} = \frac{1}{2^{m-1}} - \frac{1}{2^{n-1}}$.
33: Since $w_{m} = \frac{1}{2^{m-1}}$, we have $W_{P} = w_{m} - \frac{1}{2^{n-1}} < w_{m}$.
34: Since $h$ is strictly increasing, $h(w_{m}) - h(W_{P}) > 0$.
35: Thus, $S \geq 0$ for all $n \geq 2$, which proves the inequality.
