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
