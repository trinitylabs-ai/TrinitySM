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

1: To prove that for any positive integer $N$, the inequality $\left| \sum_{n=1}^N \frac{\delta(n)}{n} - \frac{2}{3}N \right| < 1$ holds, where $\delta(n)$ is the largest odd divisor of $n$, we proceed as follows.
2: 
3: ### 1. Derivation of a Recurrence Relation
4: Let $f(N) = \sum_{n=1}^N \frac{\delta(n)}{n}$. We partition the sum into terms where $n$ is odd and terms where $n$ is even:
5: \[ f(N) = \sum_{\substack{n=1 \\ n \text{ odd}}}^N \frac{\delta(n)}{n} + \sum_{\substack{n=1 \\ n \text{ even}}}^N \frac{\delta(n)}{n} \]
6: For any odd integer $n$, the largest odd divisor is $\delta(n) = n$, so $\frac{\delta(n)}{n} = 1$. The number of odd integers in the set $\{1, 2, \dots, N\}$ is exactly $\lceil N/2 \rceil$. Thus, the first sum is:
7: \[ \sum_{\substack{n=1 \\ n \text{ odd}}}^N 1 = \lceil N/2 \rceil \]
8: For any even integer $n$, let $n = 2m$. The largest odd divisor of $2m$ is the same as the largest odd divisor of $m$, so $\delta(2m) = \delta(m)$. As $n$ ranges over the even integers from $2$ to $N$, $m$ ranges over the integers from $1$ to $\lfloor N/2 \rfloor$. Thus, the second sum is:
9: \[ \sum_{m=1}^{\lfloor N/2 \rfloor} \frac{\delta(m)}{2m} = \frac{1}{2} \sum_{m=1}^{\lfloor N/2 \rfloor} \frac{\delta(m)}{m} = \frac{1}{2} f(\lfloor N/2 \rfloor) \]
10: Combining these results, we obtain the recurrence relation:
11: \[ f(N) = \lceil N/2 \rceil + \frac{1}{2} f(\lfloor N/2 \rfloor) \]
12: 
13: ### 2. Analysis of the Deviation
14: Define the deviation from the linear term as $g(N) = f(N) - \frac{2}{3}N$. We substitute $f(N) = g(N) + \frac{2}{3}N$ into the recurrence relation:
15: \[ g(N) + \frac{2}{3}N = \lceil N/2 \rceil + \frac{1}{2} \left( g(\lfloor N/2 \rfloor) + \frac{2}{3} \lfloor N/2 \rfloor \right) \]
16: \[ g(N) = \frac{1}{2} g(\lfloor N/2 \rfloor) + \lceil N/2 \rceil + \frac{1}{3} \lfloor N/2 \rfloor - \frac{2}{3}N \]
17: We evaluate this for the two possible parities of $N$:
18: - If $N = 2k$ (even), then $\lceil N/2 \rceil = k$ and $\lfloor N/2 \rfloor = k$:
19:   \[ g(2k) = \frac{1}{2} g(k) + k + \frac{1}{3}k - \frac{2}{3}(2k) = \frac{1}{2} g(k) + \frac{4}{3}k - \frac{4}{3}k = \frac{1}{2} g(k) \]
20: - If $N = 2k+1$ (odd), then $\lceil N/2 \rceil = k+1$ and $\lfloor N/2 \rfloor = k$:
21:   \[ g(2k+1) = \frac{1}{2} g(k) + (k+1) + \frac{1}{3}k - \frac{2}{3}(2k+1) = \frac{1}{2} g(k) + \frac{4}{3}k + 1 - \frac{4}{3}k - \frac{2}{3} = \frac{1}{2} g(k) + \frac{1}{3} \]
22: 
23: ### 3. Bounding the Deviation by Induction
24: We prove by induction that $0 \le g(N) < \frac{2}{3}$ for all $N \ge 0$.
25: - **Base Case:** For $N=0$, $f(0)=0$, so $g(0) = 0 - 0 = 0$. The inequality $0 \le 0 < 2/3$ holds.
26: - **Inductive Step:** Assume that $0 \le g(k) < 2/3$ for all $0 \le k < N$.
27:   - If $N=2k$, then $g(N) = \frac{1}{2}g(k)$. Since $0 \le g(k) < 2/3$, it follows that $0 \le g(N) < 1/3 < 2/3$.
28:   - If $N=2k+1$, then $g(N) = \frac{1}{2}g(k) + 1/3$. Since $0 \le g(k) < 2/3$, it follows that $1/3 \le g(N) < 1/3 + 1/3 = 2/3$.
29: In both cases, the property $0 \le g(N) < 2/3$ is preserved. Thus, by induction, the bound holds for all $N \ge 0$.
30: 
31: ### 4. Final Conclusion
32: Since $0 \le g(N) < 2/3$ for all positive integers $N$, we have:
33: \[ \left| g(N) \right| = \left| \sum_{n=1}^N \frac{\delta(n)}{n} - \frac{2}{3}N \right| < \frac{2}{3} < 1 \]
34: This completes the proof. $\square$
