# Proof comparison

## Proof A
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Fixed point analysis (lines 4-5): Correctly identifies that $g(x)=x \implies x=0$ and $g(0)$ must be a fixed point, thus $g(0)=0$.
- Monotonicity analysis (lines 7-9): Correctly proves $g(x)>x$ for $x>0$ and $g(x)<x$ for $x<0$ using the functional equation and the strictly increasing property.
- Recurrence relation (lines 12-15): Correctly derives the linear recurrence $a_{n+2} = a_{n+1} + 20a_n$ and solves the characteristic equation $r^2-r-20=0$ to find roots $5$ and $-4$.
- Bi-infinite orbit analysis (lines 18-27): Correctly defines $x_n = g^{(n)}(x_0)$ for $n \in \mathbb{Z}$. For $x_0 > 0$, $x_n$ must remain positive for all $n$. The expression $x_{-m} = B(x_0)(-1/4)^m [1 + \frac{A(x_0)}{B(x_0)}(-4/5)^m]$ shows that if $B(x_0) \neq 0$, the sign of $x_{-m}$ alternates for large $m$, which is a contradiction. Thus $B(x)=0$ for all $x$.
- Final conclusion (lines 29-34): Correctly concludes $g(x)=5x$ and verifies it satisfies all problem conditions.

## Proof B
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Fixed point analysis (line 3): Correctly identifies $g(0)=0$ using injectivity.
- Recurrence relation (lines 5-12): Correctly derives the recurrence $a_{n+2} = a_{n+1} + 20a_n$ and its general solution.
- Inverse recurrence (lines 14-19): Correctly derives the recurrence for $y_n = g^{-n}(x)$ as $20y_{n+2} + y_{n+1} - y_n = 0$ and solves the characteristic equation $20r^2+r-1=0$ to find roots $1/5$ and $-1/4$.
- Monotonicity analysis (lines 20-27): Correctly argues that $y_n$ must be strictly monotonic for $x \neq 0$. The difference $y_{n+1} - y_n = (-1/4)^n [-\frac{4}{5} C(x) (-4/5)^n - \frac{5}{4} D(x)]$ alternates sign for large $n$ if $D(x) \neq 0$, which is a contradiction. Thus $D(x)=0$.
- Final conclusion (lines 28-34): Correctly concludes $g(x)=5x$ and verifies it satisfies all problem conditions.

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct. Proof A is slightly more comprehensive as it explicitly establishes the property $g(x) > x$ for $x > 0$ and $g(x) < x$ for $x < 0$ before proceeding to the recurrence, and its argument for $B(x)=0$ based on the constant sign of the orbit is slightly more direct than the monotonicity argument in Proof B.