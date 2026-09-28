# Problem

For any positive integer $n$, let $\delta(n)$ be the largest odd divisor of $n$. Prove for any $N>0$ that we have
 \[
 \left| \sum_{n=1}^N \frac{\delta(n)}{n}- \frac{2}{3}N \right| <1.
 \]

# Proof A

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

# Proof B

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
