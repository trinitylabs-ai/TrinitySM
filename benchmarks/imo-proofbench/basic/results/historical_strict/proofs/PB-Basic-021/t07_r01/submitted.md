To prove that $x_{n-1}$ divides $x_n$ for all integers $n \ge 2$, where $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$ for $n \ge 2$, we proceed by induction.

**1. Base Case**
For $n=2$, we have $x_1 = 6$ and $x_2 = 2^6 + 2 = 64 + 2 = 66$. Since $66 = 6 \times 11$, it follows that $x_1 \mid x_2$.

**2. Inductive Hypothesis**
Let $m_n = x_n - 1$. We define a property $Q_n$ as follows: $m_n$ is an odd multiple of $m_{n-1}$.
For $n=2$, $m_2 = x_2 - 1 = 65$ and $m_1 = x_1 - 1 = 5$. Since $65 = 13 \times 5$ and $13$ is odd, $Q_2$ is true.

**3. Proving $Q_n \implies x_n \mid x_{n+1}$**
Assume $Q_n$ is true. Then $x_n - 1 = (2k+1)(x_{n-1} - 1)$ for some integer $k$.
We want to show that $x_n \mid x_{n+1}$, which is equivalent to $x_n \mid 2^{x_n} + 2$.
Note that $x_n = 2(2^{x_{n-1}-1} + 1)$. Let $d_n = 2^{x_{n-1}-1} + 1$. Then $x_n \mid 2^{x_n} + 2$ is equivalent to $d_n \mid 2^{x_n-1} + 1$ because $2^{x_n} + 2 = 2(2^{x_n-1} + 1)$.
From the definition of $d_n$, we have $2^{x_{n-1}-1} \equiv -1 \pmod{d_n}$. Since $Q_n$ implies $x_n - 1 = (2k+1)(x_{n-1}-1)$, we have:
\[ 2^{x_n-1} = \left(2^{x_{n-1}-1}\right)^{2k+1} \equiv (-1)^{2k+1} = -1 \pmod{d_n} \]
Thus, $d_n \mid 2^{x_n-1} + 1$, which implies $x_n \mid 2^{x_n} + 2 = x_{n+1}$.

**4. Proving $Q_n \implies Q_{n+1}$**
Assume $Q_n$ is true. We wish to show $Q_{n+1}$: $m_{n+1}$ is an odd multiple of $m_n$.
$m_{n+1} = x_{n+1} - 1 = 2^{x_n} + 1$ and $m_n = x_n - 1 = 2^{x_{n-1}} + 1$.
We examine $2^{x_n} + 1 \pmod{m_n}$. Since $2^{x_{n-1}} \equiv -1 \pmod{m_n}$, it follows that $2^{2x_{n-1}} \equiv 1 \pmod{m_n}$.
We now determine $x_n \pmod{2x_{n-1}}$. Consider the ratio:
\[ q = \frac{x_n}{x_{n-1}} = \frac{2(2^{x_{n-1}-1} + 1)}{x_{n-1}} = \frac{2^{x_{n-1}-1} + 1}{2^{x_{n-2}-1} + 1} \]
Because $Q_{n-1}$ is true (implied by the induction chain), $x_{n-1}-1 = (2j+1)(x_{n-2}-1)$. Let $a = x_{n-2}-1$. Then:
\[ 2^{x_{n-1}-1} + 1 = (2^a)^{2j+1} + 1 = (2^a + 1) \sum_{i=0}^{2j} (-2^a)^i \]
The sum $\sum_{i=0}^{2j} (-2^a)^i \equiv \sum_{i=0}^{2j} (-(-1))^i = \sum_{i=0}^{2j} 1 = 2j+1 \pmod{2^a+1}$, which is odd. Thus, $q$ is odd.
Since $q$ is odd, $x_n = (2l+1)x_{n-1} = 2lx_{n-1} + x_{n-1}$. Then:
\[ 2^{x_n} = (2^{2x_{n-1}})^l \cdot 2^{x_{n-1}} \equiv 1^l \cdot (-1) = -1 \pmod{m_n} \]
Thus $2^{x_n} + 1 \equiv 0 \pmod{m_n}$. Since both $2^{x_n} + 1$ and $m_n$ are odd, the quotient is necessarily odd. This proves $Q_{n+1}$ is true.

**Conclusion**
By induction, $Q_n$ is true for all $n \ge 2$, and since $Q_n \implies x_n \mid x_{n+1}$, it follows that $x_{n-1} \mid x_n$ for all $n \ge 2$. \(\square\)
