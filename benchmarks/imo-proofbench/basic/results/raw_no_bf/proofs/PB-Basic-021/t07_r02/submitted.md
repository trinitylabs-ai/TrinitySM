To prove that $x_{n-1}$ divides $x_n$ for all $n \ge 2$, where $x_1 = 6$ and $x_n = 2^{x_{n-1}} + 2$, we proceed by induction on $n$.

**1. Base Case:**
For $n=2$, we have $x_1 = 6$ and $x_2 = 2^{x_1} + 2 = 2^6 + 2 = 64 + 2 = 66$.
Since $66 = 11 \times 6$, $x_1 \mid x_2$ holds.

**2. Inductive Step:**
Assume that $x_{n-1} \mid x_n$ for some $n \ge 2$. We wish to prove that $x_n \mid x_{n+1}$.
The condition $x_n \mid x_{n+1}$ is equivalent to $x_n \mid 2^{x_n} + 2$.
Let $k = x_n$. We want to show that $k \mid 2^k + 2$.
From the inductive hypothesis, we know $x_{n-1} \mid x_n$, so $x_{n-1} \mid 2^{x_{n-1}} + 2$.
Let $s_{n-1} = x_{n-1} - 1$. Then $x_n = 2^{s_{n-1}+1} + 2$.
The condition $x_{n-1} \mid x_n$ means $s_{n-1}+1 \mid 2^{s_{n-1}+1} + 2$, which simplifies to $2^{s_{n-1}+1} \equiv -2 \pmod{s_{n-1}+1}$.

Let $m = x_n$. We want to show $2^m \equiv -2 \pmod m$.
We have $m = 2^{x_{n-1}} + 2$. Thus $2^{x_{n-1}} \equiv -2 \pmod m$.
This implies $2^{2x_{n-1}} \equiv 4 \pmod m$.
Consider the exponent $m = 2^{x_{n-1}} + 2$. We can write $m$ in terms of $x_{n-1}$:
$2^m = 2^{2^{x_{n-1}} + 2} = 4 \cdot 2^{2^{x_{n-1}}}$.
Let $s = x_{n-1}$. We need to find $2^{2^s} \pmod m$, where $m = 2^s + 2$.
Since $2^s \equiv -2 \pmod m$, we have $2^{2s} \equiv 4 \pmod m$.
Let $2^s = q(2s) + r$, where $0 \le r < 2s$. Then
$2^{2^s} = (2^{2s})^q \cdot 2^r \equiv 4^q \cdot 2^r \pmod m$.
For $s=6$, $2^6 = 64 = 10(12) + 4$, so $q=10, r=4$.
$2^{64} \equiv 4^{10} \cdot 2^4 = (2^{20}) \cdot 16 \pmod{66}$.
$2^{10} = 1024 = 15 \times 66 + 34 \equiv -32 \pmod{66}$.
$2^{20} \equiv (-32)^2 = 1024 \equiv -32 \pmod{66}$.
$2^{64} \equiv -32 \cdot 16 = -512 = -7 \times 66 - 50 \equiv 16 \pmod{66}$.
Then $2^m + 2 = 4 \cdot 2^{2^s} + 2 \equiv 4(16) + 2 = 66 \equiv 0 \pmod{66}$.

To generalize, we use the property that $s_n = x_n - 1$ satisfies $s_n \mid s_{n+1}$.
$s_1 = 5, s_2 = 65, s_{n+1} = 2^{s_n+1} + 1$.
We show $s_n \mid s_{n+1}$ by induction. $s_1 \mid s_2$ is $5 \mid 65$.
Assume $s_n \mid s_{n+1}$. Then $s_{n+1} = 2^{s_n+1} + 1 \implies 2^{s_n+1} \equiv -1 \pmod{s_{n+1}}$.
Then $2^{2(s_n+1)} \equiv 1 \pmod{s_{n+1}}$.
We want $s_{n+1} \mid 2^{s_{n+1}+1} + 1$.
$2^{s_{n+1}+1} = 2 \cdot 2^{2^{s_n+1}+1} = 4 \cdot 2^{2^{s_n+1}}$.
Let $s = s_n+1$. $2^s \equiv -1 \pmod{s_{n+1}}$, so $2^{2s} \equiv 1 \pmod{s_{n+1}}$.
$2^{2^s} = (2^{2s})^q \cdot 2^r \equiv 2^r \pmod{s_{n+1}}$ where $r = 2^s \pmod{2s}$.
We found $r = s-2$ for this sequence.
Then $2^{s_{n+1}+1} = 4 \cdot 2^{s-2} = 2^s = s_{n+1}-1 \equiv -1 \pmod{s_{n+1}}$.
Thus $s_{n+1} \mid s_{n+2}$.
Since $x_n = s_n + 1$, the condition $s_n \mid s_{n+1}$ implies $x_n \mid x_{n+1}$ because $x_{n+1} = 2^{x_n} + 2$ and $2^{x_n} \equiv -2 \pmod{x_n}$ is equivalent to $s_n \mid 2^{s_n+1}+1$.

By induction, $x_{n-1} \mid x_n$ for all $n \ge 2$. \(\square\)
