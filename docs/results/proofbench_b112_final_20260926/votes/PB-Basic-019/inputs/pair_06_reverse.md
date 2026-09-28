# Problem

For any positive integer $n$, let $\delta(n)$ be the largest odd divisor of $n$. Prove for any $N>0$ that we have
 \[
 \left| \sum_{n=1}^N \frac{\delta(n)}{n}- \frac{2}{3}N \right| <1.
 \]

# Proof A

1: To prove that for any positive integer $N > 0$,
2: \[ \left| \sum_{n=1}^N \frac{\delta(n)}{n} - \frac{2}{3}N \right| < 1, \]
3: where $\delta(n)$ is the largest odd divisor of $n$, we proceed as follows.
4: 
5: Every positive integer $n$ can be uniquely expressed as $n = 2^k \cdot m$, where $k \ge 0$ is an integer and $m$ is an odd positive integer. By definition, $\delta(n) = m$, which implies that $\frac{\delta(n)}{n} = \frac{m}{2^k m} = \frac{1}{2^k}$. Let $S(N) = \sum_{n=1}^N \frac{\delta(n)}{n}$. We can rewrite this sum by grouping terms according to the value of $k$:
6: \[ S(N) = \sum_{k=0}^M \frac{1}{2^k} c_k(N), \]
7: where $M = \lfloor \log_2 N \rfloor$ and $c_k(N)$ is the number of integers $n \in \{1, \dots, N\}$ such that $v_2(n) = k$. An integer $n \le N$ satisfies $v_2(n) = k$ if and only if $n$ is a multiple of $2^k$ but not a multiple of $2^{k+1}$. Thus,
8: \[ c_k(N) = \left\lfloor \frac{N}{2^k} \right\rfloor - \left\lfloor \frac{N}{2^{k+1}} \right\rfloor. \]
9: Substituting this into the expression for $S(N)$, we obtain:
10: \[ S(N) = \sum_{k=0}^M \frac{1}{2^k} \left( \left\lfloor \frac{N}{2^k} \right\rfloor - \left\lfloor \frac{N}{2^{k+1}} \right\rfloor \right). \]
11: Using the identity $\lfloor x \rfloor = x - \{x\}$, where $\{x\}$ denotes the fractional part of $x$, we expand the sum:
12: \[ S(N) = \sum_{k=0}^M \frac{1}{2^k} \left( \frac{N}{2^k} - \left\{ \frac{N}{2^k} \right\} \right) - \sum_{k=0}^M \frac{1}{2^k} \left( \frac{N}{2^{k+1}} - \left\{ \frac{N}{2^{k+1}} \right\} \right) \]
13: \[ S(N) = N \sum_{k=0}^M \frac{1}{4^k} - \sum_{k=0}^M \frac{1}{2^k} \left\{ \frac{N}{2^k} \right\} - \frac{N}{2} \sum_{k=0}^M \frac{1}{4^k} + \sum_{k=0}^M \frac{1}{2^k} \left\{ \frac{N}{2^{k+1}} \right\} \]
14: \[ S(N) = \frac{N}{2} \sum_{k=0}^M \frac{1}{4^k} + \sum_{k=0}^M \frac{1}{2^k} \left( \left\{ \frac{N}{2^{k+1}} \right\} - \left\{ \frac{N}{2^k} \right\} \right). \]
15: Evaluating the geometric series, we have $\sum_{k=0}^M (1/4)^k = \frac{1 - (1/4)^{M+1}}{3/4} = \frac{4}{3} (1 - \frac{1}{4^{M+1}})$. Thus, the first term is $\frac{2N}{3} (1 - \frac{1}{4^{M+1}}) = \frac{2N}{3} - \frac{2N}{3 \cdot 4^{M+1}}$.
16: The second term, $T(N)$, is:
17: \[ T(N) = \sum_{k=0}^M \frac{1}{2^k} \left\{ \frac{N}{2^{k+1}} \right\} - \sum_{k=0}^M \frac{1}{2^k} \left\{ \frac{N}{2^k} \right\} \]
18: \[ T(N) = \left( \left\{ \frac{N}{2} \right\} + \frac{1}{2} \left\{ \frac{N}{4} \right\} + \dots + \frac{1}{2^M} \left\{ \frac{N}{2^{M+1}} \right\} \right) - \left( \{ N \} + \frac{1}{2} \left\{ \frac{N}{2} \right\} + \dots + \frac{1}{2^M} \left\{ \frac{N}{2^M} \right\} \right). \]
19: Since $N$ is an integer, $\{N\} = 0$. Regrouping the terms, we find:
20: \[ T(N) = \left\{ \frac{N}{2} \right\} \left( 1 - \frac{1}{2} \right) + \left\{ \frac{N}{4} \right\} \left( \frac{1}{2} - \frac{1}{4} \right) + \dots + \left\{ \frac{N}{2^M} \right\} \left( \frac{1}{2^{M-1}} - \frac{1}{2^M} \right) + \frac{1}{2^M} \left\{ \frac{N}{2^{M+1}} \right\} \]
21: \[ T(N) = \sum_{k=1}^M \frac{1}{2^k} \left\{ \frac{N}{2^k} \right\} + \frac{1}{2^M} \left\{ \frac{N}{2^{M+1}} \right\}. \]
22: Let $E(N) = S(N) - \frac{2N}{3}$. Then:
23: \[ E(N) = \sum_{k=1}^M \frac{1}{2^k} \left\{ \frac{N}{2^k} \right\} + \frac{1}{2^M} \left\{ \frac{N}{2^{M+1}} \right\} - \frac{2N}{3 \cdot 4^{M+1}}. \]
24: Since $0 \le \{x\} < 1$, the sum is bounded by $\sum_{k=1}^M \frac{1}{2^k} + \frac{1}{2^M} = (1 - \frac{1}{2^M}) + \frac{1}{2^M} = 1$. Thus, $E(N) < 1$.
25: For the lower bound, since the sum is non-negative and $N < 2^{M+1}$, we have:
26: \[ E(N) > - \frac{2N}{3 \cdot 4^{M+1}} > - \frac{2 \cdot 2^{M+1}}{3 \cdot 4^{M+1}} = - \frac{4}{3 \cdot 2^{M+1}} = - \frac{2}{3 \cdot 2^M} \ge - \frac{2}{3} > -1. \]
27: Thus, $|E(N)| < 1$ for all $N > 0$.
28: 
29: \(\square\)

# Proof B

1: To prove that for any positive integer $N > 0$,
2: \[ \left| \sum_{n=1}^N \frac{\delta(n)}{n} - \frac{2}{3}N \right| < 1, \]
3: where $\delta(n)$ is the largest odd divisor of $n$, we define the sum $S(N) = \sum_{n=1}^N \frac{\delta(n)}{n}$ and establish a recurrence relation for $S(N)$.
4: 
5: ### 1. Deriving the Recurrence for $S(N)$
6: We split the sum $S(2N)$ into terms where $n$ is odd and terms where $n$ is even:
7: \[ S(2N) = \sum_{\substack{n=1 \\ n \text{ odd}}}^{2N} \frac{\delta(n)}{n} + \sum_{\substack{n=1 \\ n \text{ even}}}^{2N} \frac{\delta(n)}{n}. \]
8: For odd $n$, the largest odd divisor of $n$ is $n$ itself, so $\delta(n) = n$. There are exactly $N$ odd integers in the range $[1, 2N]$, thus:
9: \[ \sum_{\substack{n=1 \\ n \text{ odd}}}^{2N} \frac{\delta(n)}{n} = \sum_{\substack{n=1 \\ n \text{ odd}}}^{2N} \frac{n}{n} = \sum_{\substack{n=1 \\ n \text{ odd}}}^{2N} 1 = N. \]
10: For even $n$, we can write $n = 2m$ for $m \in \{1, 2, \dots, N\}$. The largest odd divisor of $2m$ is the same as the largest odd divisor of $m$, so $\delta(2m) = \delta(m)$. Thus:
11: \[ \sum_{\substack{n=1 \\ n \text{ even}}}^{2N} \frac{\delta(n)}{n} = \sum_{m=1}^N \frac{\delta(2m)}{2m} = \sum_{m=1}^N \frac{\delta(m)}{2m} = \frac{1}{2} \sum_{m=1}^N \frac{\delta(m)}{m} = \frac{1}{2} S(N). \]
12: Combining these, we have:
13: \[ S(2N) = N + \frac{1}{2} S(N). \]
14: For the odd case $S(2N+1)$, we add the term for $n = 2N+1$. Since $2N+1$ is odd, $\delta(2N+1) = 2N+1$:
15: \[ S(2N+1) = S(2N) + \frac{\delta(2N+1)}{2N+1} = S(2N) + 1 = N + \frac{1}{2} S(N) + 1. \]
16: 
17: ### 2. Analyzing the Error Term $f(N)$
18: Let $f(N) = S(N) - \frac{2}{3}N$. We derive recurrences for $f(N)$ using the relations for $S(N)$:
19: For $f(2N)$:
20: \[ f(2N) = S(2N) - \frac{2}{3}(2N) = N + \frac{1}{2} S(N) - \frac{4}{3}N = \frac{1}{2} S(N) - \frac{1}{3}N = \frac{1}{2} \left( S(N) - \frac{2}{3}N \right) = \frac{1}{2} f(N). \]
21: For $f(2N+1)$:
22: \[ f(2N+1) = S(2N+1) - \frac{2}{3}(2N+1) = S(2N) + 1 - \frac{4}{3}N - \frac{2}{3} = \left( N + \frac{1}{2} S(N) \right) - \frac{4}{3}N + \frac{1}{3} = \frac{1}{2} S(N) - \frac{1}{3}N + \frac{1}{3} = \frac{1}{2} f(N) + \frac{1}{3}. \]
23: 
24: ### 3. Proof by Induction
25: We prove by induction that $0 < f(N) < \frac{2}{3}$ for all $N \ge 1$.
26: **Base Case:** For $N=1$, $S(1) = \frac{\delta(1)}{1} = 1$. Then $f(1) = 1 - \frac{2}{3} = \frac{1}{3}$. Since $0 < \frac{1}{3} < \frac{2}{3}$, the base case holds.
27: **Inductive Step:** Assume $0 < f(k) < \frac{2}{3}$ for all $1 \le k < m$.
28: - If $m = 2N$, then $f(2N) = \frac{1}{2} f(N)$. Given $0 < f(N) < \frac{2}{3}$, it follows that $0 < f(2N) < \frac{1}{3}$, so $0 < f(2N) < \frac{2}{3}$.
29: - If $m = 2N+1$, then $f(2N+1) = \frac{1}{2} f(N) + \frac{1}{3}$. Given $0 < f(N) < \frac{2}{3}$, it follows that $\frac{1}{3} < f(2N+1) < \frac{1}{3} + \frac{1}{3} = \frac{2}{3}$, so $0 < f(2N+1) < \frac{2}{3}$.
30: 
31: Thus, by induction, $0 < f(N) < \frac{2}{3}$ for all $N \ge 1$.
32: 
33: ### Conclusion
34: Since $0 < f(N) < \frac{2}{3}$ for all $N > 0$, we have $|f(N)| < \frac{2}{3} < 1$. Substituting $f(N)$ back into the original expression:
35: \[ \left| \sum_{n=1}^N \frac{\delta(n)}{n} - \frac{2}{3}N \right| < 1. \]
36: \(\square\)
