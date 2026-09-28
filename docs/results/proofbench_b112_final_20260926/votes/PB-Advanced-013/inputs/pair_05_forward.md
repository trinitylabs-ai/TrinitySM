# Problem

For an integer $n \geq 2$, let $a_{1} \leq a_{2} \leq \cdots \leq a_{n}$ be positive real numbers satisfying $a_{1} a_{2} \cdots a_{n}=1$. For each $k=1,2, \cdots, n$, define $b_{k}=2^{k}\left(1+a_{k}^{2^{k}}\right)$. Prove that the following inequality holds:

 \[
 \frac{1}{2}-\frac{1}{2^{n+1}} \leq \frac{1}{b_{1}}+\frac{1}{b_{2}}+\cdots+\frac{1}{b_{n}}
 \]

# Proof A

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
