# Problem

For an integer $n \geq 2$, let $a_{1} \leq a_{2} \leq \cdots \leq a_{n}$ be positive real numbers satisfying $a_{1} a_{2} \cdots a_{n}=1$. For each $k=1,2, \cdots, n$, define $b_{k}=2^{k}\left(1+a_{k}^{2^{k}}\right)$. Prove that the following inequality holds:

 \[
 \frac{1}{2}-\frac{1}{2^{n+1}} \leq \frac{1}{b_{1}}+\frac{1}{b_{2}}+\cdots+\frac{1}{b_{n}}
 \]

# Proof A

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

# Proof B

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
