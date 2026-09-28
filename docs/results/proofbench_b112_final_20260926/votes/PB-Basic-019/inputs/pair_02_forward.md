# Problem

For any positive integer $n$, let $\delta(n)$ be the largest odd divisor of $n$. Prove for any $N>0$ that we have
 \[
 \left| \sum_{n=1}^N \frac{\delta(n)}{n}- \frac{2}{3}N \right| <1.
 \]

# Proof A

1: To prove that for any $N > 0$, the inequality $\left| \sum_{n=1}^N \frac{\delta(n)}{n} - \frac{2}{3}N \right| < 1$ holds, where $\delta(n)$ is the largest odd divisor of $n$, we proceed as follows.
2: 
3: ### 1. Representation of $\delta(n)/n$
4: By definition, any positive integer $n$ can be uniquely written as $n = 2^{v_2(n)} \cdot \delta(n)$, where $v_2(n)$ is the exponent of the highest power of 2 dividing $n$ (the 2-adic valuation) and $\delta(n)$ is the remaining odd part. Thus, we have:
5: \[ \frac{\delta(n)}{n} = \frac{1}{2^{v_2(n)}} \]
6: For any $N > 0$, the sum $\sum_{n=1}^N$ is understood as the sum over all positive integers $n \le N$. Let $M = \lfloor N \rfloor$. If $M=0$, the sum is empty and equals 0. If $M \ge 1$, the sum is:
7: \[ S(N) = \sum_{n=1}^M \frac{\delta(n)}{n} = \sum_{n=1}^M \frac{1}{2^{v_2(n)}} \]
8: 
9: ### 2. Summation by Grouping
10: For $M \ge 1$, we evaluate $S(N)$ by counting how many integers $n \in \{1, 2, \dots, M\}$ have a specific 2-adic valuation $v_2(n) = k$.
11: The number of integers in $\{1, \dots, M\}$ divisible by $2^k$ is $\lfloor M/2^k \rfloor$. An integer $n$ satisfies $v_2(n) = k$ if and only if it is divisible by $2^k$ but not by $2^{k+1}$. Therefore, the number of such $n$ is:
12: \[ \text{count}(k) = \lfloor \frac{M}{2^k} \rfloor - \lfloor \frac{M}{2^{k+1}} \rfloor \]
13: We can now rewrite the sum $S(N)$ as:
14: \[ S(N) = \sum_{k=0}^{\infty} \frac{1}{2^k} \left( \lfloor \frac{M}{2^k} \rfloor - \lfloor \frac{M}{2^{k+1}} \rfloor \right) \]
15: (Note that the sum is finite because $\lfloor M/2^k \rfloor = 0$ for $2^k > M$).
16: 
17: ### 3. Algebraic Simplification
18: Let $a_k = \lfloor M/2^k \rfloor$. Expanding the sum:
19: \[ S(N) = (a_0 - a_1) + \frac{1}{2}(a_1 - a_2) + \frac{1}{4}(a_2 - a_3) + \dots \]
20: Grouping the terms by $a_k$:
21: \[ S(N) = a_0 + a_1\left(\frac{1}{2} - 1\right) + a_2\left(\frac{1}{4} - \frac{1}{2}\right) + a_3\left(\frac{1}{8} - \frac{1}{4}\right) + \dots \]
22: \[ S(N) = a_0 - \frac{1}{2}a_1 - \frac{1}{4}a_2 - \frac{1}{8}a_3 - \dots = M - \sum_{k=1}^{\infty} \frac{1}{2^k} \lfloor \frac{M}{2^k} \rfloor \]
23: 
24: ### 4. Application of the Fractional Part
25: Using the identity $\lfloor x \rfloor = x - \{x\}$, where $\{x\}$ denotes the fractional part of $x$:
26: \[ S(N) = M - \sum_{k=1}^{\infty} \frac{1}{2^k} \left( \frac{M}{2^k} - \{ \frac{M}{2^k} \} \right) \]
27: \[ S(N) = M - \sum_{k=1}^{\infty} \frac{M}{4^k} + \sum_{k=1}^{\infty} \frac{1}{2^k} \{ \frac{M}{2^k} \} \]
28: The first summation is a geometric series: $\sum_{k=1}^{\infty} \frac{M}{4^k} = M \left( \frac{1/4}{1 - 1/4} \right) = \frac{M}{3}$.
29: Substituting this back into the expression for $S(N)$:
30: \[ S(N) = M - \frac{M}{3} + \sum_{k=1}^{\infty} \frac{1}{2^k} \{ \frac{M}{2^k} \} = \frac{2}{3}M + \sum_{k=1}^{\infty} \frac{1}{2^k} \{ \frac{M}{2^k} \} \]
31: This formula also holds for $M=0$, as both sides equal 0.
32: 
33: ### 5. Establishing the Bound
34: Let $R(M) = \sum_{k=1}^{\infty} \frac{1}{2^k} \{ \frac{M}{2^k} \}$. Since $0 \le \{x\} < 1$ for all $x$, we have:
35: \[ 0 \le R(M) < \sum_{k=1}^{\infty} \frac{1}{2^k} = 1 \]
36: Now we consider the difference for any $N > 0$:
37: \[ S(N) - \frac{2}{3}N = \frac{2}{3}M + R(M) - \frac{2}{3}N = R(M) - \frac{2}{3}(N - M) \]
38: Let $\epsilon = N - M = \{N\}$, where $0 \le \epsilon < 1$. Then:
39: \[ S(N) - \frac{2}{3}N = R(M) - \frac{2}{3}\epsilon \]
40: Since $0 \le R(M) < 1$ and $0 \le \frac{2}{3}\epsilon < \frac{2}{3}$, the value of the difference is bounded by:
41: \[ 0 - \frac{2}{3} < R(M) - \frac{2}{3}\epsilon < 1 - 0 \]
42: \[ -\frac{2}{3} < S(N) - \frac{2}{3}N < 1 \]
43: This implies that $\left| \sum_{n=1}^N \frac{\delta(n)}{n} - \frac{2}{3}N \right| < 1$ for all $N > 0$. \(\square\)

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
