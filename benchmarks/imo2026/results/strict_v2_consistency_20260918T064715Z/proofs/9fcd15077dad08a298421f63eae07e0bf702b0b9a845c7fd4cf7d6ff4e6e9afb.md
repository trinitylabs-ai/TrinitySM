To prove the properties of the operation described, we analyze the evolution of the integers on the blackboard through prime factorization and potential functions.

### Part 1: Proof of Termination
Let the integers on the blackboard at any time $t$ be $a_1, a_2, \dots, a_{2026}$. A move is possible if there exist two integers $m, n > 1$ at different positions. Let $N(t)$ be the number of integers greater than 1 on the blackboard. The operation replaces $m$ and $n$ with $g = \gcd(m, n)$ and $k = \text{lcm}(m, n)/\gcd(m, n)$.

We define a potential function $V(t) = \sum_p \sum_{i=1}^{2026} (v_p(a_i))^2$, where $v_p(x)$ is the exponent of the prime $p$ in the prime factorization of $x$. Consider the effect of a move on $N(t)$ and $V(t)$:

1.  **Case 1: $\gcd(m, n) = 1$.**
    Here $g = 1$ and $k = mn$. The integers $m, n > 1$ are replaced by $1$ and $mn$. Thus, $N(t+1) = N(t) - 1$.
2.  **Case 2: $\gcd(m, n) > 1$.**
    If $m = n$, then $g = m$ and $k = 1$. Thus, $N(t+1) = N(t) - 1$.
    If $m \neq n$, then $g > 1$. Since $m \neq n$, it is impossible for $k = 1$ (as $\text{lcm}(m, n) = \gcd(m, n)$ implies $m = n$). Thus, $g > 1$ and $k > 1$, so $N(t+1) = N(t)$. We then examine $V(t)$. For any prime $p$, let $x = v_p(m)$ and $y = v_p(n)$. The operation replaces $x, y$ with $x' = \min(x, y)$ and $y' = \max(x, y) - \min(x, y) = |x - y|$. The change in the sum of squares for prime $p$ is:
    \[ (x')^2 + (y')^2 - (x^2 + y^2) = \min(x, y)^2 + (x - y)^2 - (x^2 + y^2) = \min(x, y)^2 - 2xy. \]
    If $x, y > 0$, then $\min(x, y)^2 - 2xy = \min(x, y)(\min(x, y) - 2\max(x, y)) < 0$. If one of $x, y$ is 0, the sum of squares remains unchanged. Since $\gcd(m, n) > 1$, there is at least one prime $p$ such that $v_p(m) > 0$ and $v_p(n) > 0$. Thus, $V(t+1) < V(t)$.

Since $N(t)$ is a non-increasing sequence of positive integers and $V(t)$ is a non-negative integer that strictly decreases whenever $N(t)$ remains constant, the process must terminate in finitely many moves. The process terminates when $N(t) \le 1$. Since $g \cdot k = \gcd(m, n) \cdot \frac{\text{lcm}(m, n)}{\gcd(m, n)} = \text{lcm}(m, n)$, and $\text{lcm}(m, n) > 1$ whenever $m, n > 1$, the property that at least one integer on the blackboard is greater than 1 is invariant. Because the initial integers are all greater than 1, the process must end with exactly one integer $M > 1$.

### Part 2: Proof of Invariance
To prove that $M$ is independent of the sequence of moves, we look at the exponents of each prime $p$. For a fixed prime $p$, let the exponents on the board be $x_1, x_2, \dots, x_{2026}$. The operation replaces two exponents $x, y$ with $\min(x, y)$ and $|x - y|$. 

This is the subtraction-based Euclidean algorithm. A fundamental property of this algorithm is that it preserves the greatest common divisor of the two numbers:
\[ \gcd(x, y) = \gcd(\min(x, y), |x - y|). \]
Consequently, for every prime $p$, the value $g_p = \gcd(x_1, x_2, \dots, x_{2026})$ is invariant throughout the process. At the end of the process, only one integer $M$ is greater than 1, meaning for each prime $p$, only one exponent $v_p(M)$ is non-zero and all other $v_p(a_i) = 0$. The invariant $g_p$ then satisfies:
\[ g_p = \gcd(0, 0, \dots, v_p(M), \dots, 0) = v_p(M). \]
Thus, the final value $M$ is uniquely determined by the initial integers:
\[ M = \prod_p p^{\gcd(v_p(a_1), v_p(a_2), \dots, v_p(a_{2026}))}. \]
Since this expression depends only on the initial values, $M$ is independent of the choices made by Confucius.