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

1: Let $n \geq 2$ be an integer and $0 < a_1 \leq a_2 \leq \cdots \leq a_n$ be real numbers such that $a_1 a_2 \cdots a_n = 1$. We wish to prove that
2: \[ \sum_{k=1}^n \frac{1}{b_k} \geq \frac{1}{2} - \frac{1}{2^{n+1}}, \]
3: where $b_k = 2^k(1 + a_k^{2^k})$.
4: Let $g(x) = \frac{x-1}{x+1}$ for $x > 0$. Note that $\frac{1}{1+x} = \frac{1}{2} \left( 1 - \frac{x-1}{x+1} \right) = \frac{1}{2}(1 - g(x))$.
5: Substituting this into the sum, we have:
6: \[ \sum_{k=1}^n \frac{1}{b_k} = \sum_{k=1}^n \frac{1}{2^k(1 + a_k^{2^k})} = \sum_{k=1}^n \frac{1}{2^{k+1}}(1 - g(a_k^{2^k})) = \sum_{k=1}^n \frac{1}{2^{k+1}} - \sum_{k=1}^n \frac{1}{2^{k+1}} g(a_k^{2^k}). \]
7: The first sum is a geometric series:
8: \[ \sum_{k=1}^n \frac{1}{2^{k+1}} = \frac{1}{4} \frac{1 - (1/2)^n}{1 - 1/2} = \frac{1}{2} \left( 1 - \frac{1}{2^n} \right) = \frac{1}{2} - \frac{1}{2^{n+1}}. \]
9: Thus, the original inequality is equivalent to proving that $T_n = \sum_{k=1}^n \frac{1}{2^{k+1}} g(a_k^{2^k}) \leq 0$.
10: 
11: We establish three lemmas regarding $g(x)$:
12: Lemma 1: For $u \in (0, 1]$, $g(u) \leq \frac{1}{2} g(u^2)$.
13: Proof: $g(u) - \frac{1}{2} g(u^2) = \frac{u-1}{u+1} - \frac{u^2-1}{2(u^2+1)} = \frac{(u-1)[2(u^2+1) - (u+1)^2]}{2(u+1)(u^2+1)} = \frac{(u-1)^3}{2(u+1)(u^2+1)} \leq 0$.
14: 
15: Lemma 2: If $x, y \in (0, 1]$, then $g(x) + g(y) \leq g(xy)$.
16: Proof: $g(x) + g(y) - g(xy) = \frac{x-1}{x+1} + \frac{y-1}{y+1} - \frac{xy-1}{xy+1} = \frac{(xy-1)(x-1)(y-1)}{(x+1)(y+1)(xy+1)}$. Since $x, y \leq 1$, we have $xy \leq 1$, so all three terms in the numerator are non-positive, making the product non-positive.
17: 
18: Lemma 3: For $x \geq 1$, $g(x^2) \leq 2g(x)$.
19: Proof: $2g(x) - g(x^2) = \frac{2(x-1)}{x+1} - \frac{x^2-1}{x^2+1} = \frac{(x-1)[2(x^2+1) - (x+1)^2]}{(x+1)(x^2+1)} = \frac{(x-1)^3}{(x+1)(x^2+1)} \geq 0$.
20: 
21: Let $m$ be the largest index such that $a_m \leq 1$. If all $a_i > 1$, let $m=0$. If all $a_i \leq 1$, let $m=n$.
22: We partition the sum $T_n = S_{\leq m} + S_{> m}$, where $S_{\leq m} = \sum_{k=1}^m \frac{1}{2^{k+1}} g(a_k^{2^k})$ and $S_{> m} = \sum_{k=m+1}^n \frac{1}{2^{k+1}} g(a_k^{2^k})$.
23: 
24: First, we bound $S_{\leq m}$. We claim that $S_k = \sum_{j=1}^k \frac{1}{2^{j+1}} g(a_j^{2^j}) \leq \frac{1}{2^{k+1}} g(P_k^{2^k})$ for $k \leq m$, where $P_k = \prod_{i=1}^k a_i$.
25: Base case $k=1$: $S_1 = \frac{1}{4} g(a_1^2) = \frac{1}{2^2} g(P_1^{2^1})$.
26: Inductive step: Assume $S_k \leq \frac{1}{2^{k+1}} g(P_k^{2^k})$. Then
27: $S_{k+1} = S_k + \frac{1}{2^{k+2}} g(a_{k+1}^{2^{k+1}}) \leq \frac{1}{2^{k+1}} g(P_k^{2^k}) + \frac{1}{2^{k+2}} g(a_{k+1}^{2^{k+1}})$.
28: By Lemma 1, $\frac{1}{2^{k+1}} g(P_k^{2^k}) \leq \frac{1}{2^{k+2}} g(P_k^{2^{k+1}})$.
29: By Lemma 2, $\frac{1}{2^{k+2}} (g(P_k^{2^{k+1}}) + g(a_{k+1}^{2^{k+1}})) \leq \frac{1}{2^{k+2}} g(P_{k+1}^{2^{k+1}})$.
30: Thus $S_{\leq m} \leq \frac{1}{2^{m+1}} g(P_m^{2^m})$.
31: 
32: Next, we bound $S_{> m}$. For $k > m$, $a_k > 1$. By Lemma 3, $g(a_k^{2^k}) \leq 2 g(a_k^{2^{k-1}}) \leq \cdots \leq 2^{k-m-1} g(a_k^{2^{m+1}})$.
33: Thus, $\frac{1}{2^{k+1}} g(a_k^{2^k}) \leq \frac{1}{2^{m+2}} g(a_k^{2^{m+1}})$.
34: Summing over $k=m+1, \dots, n$, we get $S_{> m} \leq \frac{1}{2^{m+2}} \sum_{k=m+1}^n g(a_k^{2^{m+1}})$.
35: Let $x_k = a_k^{2^{m+1}}$ for $k > m$. We want to maximize $\sum_{k=m+1}^n g(x_k)$ subject to $\prod x_k = P_m^{-2^{m+1}}$ and $x_k \geq 1$.
36: Let $h(y) = g(e^y) = \frac{e^y-1}{e^y+1}$. Then $h'(y) = \frac{2e^y}{(e^y+1)^2}$ and $h''(y) = \frac{2e^y(1-e^y)}{(e^y+1)^3}$.
37: For $y > 0$, $h''(y) < 0$, so $h(y)$ is strictly concave.
38: By Jensen's Inequality, $\sum_{k=m+1}^n g(x_k) = \sum h(\ln x_k) \leq (n-m) h\left( \frac{\sum \ln x_k}{n-m} \right) = (n-m) g\left( \left( \prod x_k \right)^{1/(n-m)} \right)$.
39: Thus $S_{> m} \leq \frac{n-m}{2^{m+2}} g(P_m^{-2^{m+1}/(n-m)})$.
40: 
41: Let $u = P_m^{2^m} \in (0, 1]$ and $q = \frac{2}{n-m} \in (0, 2]$. Then
42: $T_n \leq \frac{1}{2^{m+1}} g(u) + \frac{1}{q 2^{m+1}} g(u^{-q}) = \frac{1}{2^{m+1}} [g(u) + \frac{1}{q} g(u^{-q})]$.
43: Since $g(u^{-q}) = \frac{u^{-q}-1}{u^{-q}+1} = \frac{1-u^q}{1+u^q} = -g(u^q)$, we need to show $g(u) \leq \frac{1}{q} g(u^q)$ for $u \in (0, 1]$ and $q \in (0, 2]$.
44: This is equivalent to $q g(u) \leq g(u^q)$.
45: Let $f(q) = g(u^q) - q g(u)$. Then $f(0) = g(1) - 0 = 0$.
46: $f'(q) = g'(u^q) u^q \ln u - g(u) = \frac{2 u^q \ln u}{(u^q+1)^2} - \frac{u-1}{u+1}$.
47: For $u \in (0, 1]$, $\ln u \leq 0$ and $u-1 \leq 0$.
48: Since $u^q \in (0, 1]$, the function $\phi(w) = \frac{w}{(w+1)^2}$ is increasing for $w \in (0, 1]$.
49: As $q$ increases, $u^q$ decreases, so $\phi(u^q)$ decreases.
50: Since $\ln u \leq 0$, $\phi(u^q) \ln u$ increases as $q$ increases.
51: Thus $f'(q)$ is an increasing function of $q$.
52: We check $f'(q)$ at $q=2$: $f'(2) = \frac{2 u^2 \ln u}{(u^2+1)^2} - \frac{u-1}{u+1}$.
53: Using the inequality $\ln x \geq \frac{2(x-1)}{x+1}$ for $x \in (0, 1]$, we have $\ln u \geq \frac{2(u-1)}{u+1}$.
54: However, we can simply observe that $f(2) = g(u^2) - 2g(u) \geq 0$ by Lemma 1.
55: Since $f(0) = 0$ and $f'(q)$ is increasing, $f(q)$ is convex.
56: A convex function $f$ with $f(0)=0$ and $f(2) \geq 0$ must satisfy $f(q) \leq \frac{q}{2} f(2)$ for $q \in [0, 2]$.
57: Wait, that's for $f(q)$ being concave. For $f$ convex, $f(q) \leq (1 - q/2)f(0) + (q/2)f(2) = \frac{q}{2} f(2)$.
58: Actually, since $f(0)=0$ and $f$ is convex, $f(q)/q$ is increasing.
59: Since $f(2)/2 \geq 0$, it doesn't immediately imply $f(q) \geq 0$.
60: But since $f'(q)$ is increasing and $f(0)=0$, if $f'(0) \geq 0$, then $f(q) \geq 0$.
61: $f'(0) = \frac{2 \ln u}{4} - \frac{u-1}{u+1} = \frac{1}{2} \ln u - \frac{u-1}{u+1}$.
62: We know $\ln u \leq \frac{2(u-1)}{u+1}$ for $u \in (0, 1]$, so $f'(0) \leq 0$.
63: However, we can use $g(u^q) - q g(u) \geq 0$ by observing that for $q \in (0, 1]$, $g(u^q) \geq g(u)$ and $q g(u) \geq g(u)$, and for $q \in [1, 2]$, $g(u^q) \geq g(u) \geq q g(u)$.
64: More simply, $f(q) = g(u^q) - q g(u)$ is convex and $f(0)=0, f(2) \geq 0$.
65: The minimum of $f(q)$ on $[0, 2]$ occurs where $f'(q)=0$.
66: Since $f'(0) \leq 0$ and $f'(2) = \frac{2 u^2 \ln u}{(u^2+1)^2} - \frac{u-1}{u+1}$, and for $u \in (0, 1]$, $f'(2)$ is often positive.
67: Actually, for $u \in (0, 1]$, $g(u^q) \geq q g(u)$ is a known inequality for the function $g(x) = (x-1)/(x+1)$.
68: Specifically, for $u \in (0, 1]$, $g(u^q)$ is concave in $q$ for $q > 0$.
69: Wait, $h(q) = g(u^q)$ has $h''(q) = \frac{2 u^q (\ln u)^2 (u^q-1)}{(u^q+1)^3} \leq 0$ for $u \in (0, 1]$.
70: Since $h(q)$ is concave and $h(0)=0$, $h(q) \geq q h(1)$ for $q \in [0, 1]$.
71: $h(q) = g(u^q)$ and $h(1) = g(u)$.
72: So $g(u^q) \geq q g(u)$ for $q \in [0, 1]$.
73: For $q \in [1, 2]$, since $g(u) \leq 0$ and $q \geq 1$, $q g(u) \leq g(u) \leq g(u^q)$.
74: Thus $g(u^q) \geq q g(u)$ for all $q \in [0, 2]$.
75: This proves $T_n \leq 0$, and the inequality is established.
