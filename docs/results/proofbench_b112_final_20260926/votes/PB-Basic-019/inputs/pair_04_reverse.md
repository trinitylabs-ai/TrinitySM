# Problem

For any positive integer $n$, let $\delta(n)$ be the largest odd divisor of $n$. Prove for any $N>0$ that we have
 \[
 \left| \sum_{n=1}^N \frac{\delta(n)}{n}- \frac{2}{3}N \right| <1.
 \]

# Proof A

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
