# Proof comparison

## Proof A
Established theorem: The proof establishes that the minimum of the function $f(x,y,z) = x+y+z - 3\sqrt{3}(x^2y^2+y^2z^2+z^2x^2)$ on the domain $x^2+y^2+z^2=1, x,y,z \ge 0$ is 0, achieved at $x=y=z=1/\sqrt{3}$. This implies the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \ge 3\sqrt{3}(ab+bc+ca)$ for $a+b+c=1$.
Claim gap: NONE supported by checks. The reduction to symmetric cases via Lagrange multipliers is standard and correctly executed. The single-variable calculus in Case 2 is complex but the derivative and second derivative formulas are correct, and the boundary checks are valid.
Qualifications and supplied repairs: NONE. The argument is self-contained and rigorous, assuming standard calculus theorems (existence of extrema on compact sets, Lagrange multiplier conditions).
Decisive checks: 
- Line 9: Gradient calculation is correct. $\nabla (x^2y^2) = (2xy^2, 2x^2y, 0)$. Summing cyclic terms gives $\partial_x f = 1 - 3\sqrt{3}(2xy^2 + 2xz^2) = 1 - 6\sqrt{3}x(y^2+z^2)$. Correct.
- Line 14: The deduction that at least two variables must be equal at any interior critical point is correct. $xy-z^2 = yz-x^2 \implies x^2+xy - z^2-yz = 0 \implies (x-z)(x+y+z)=0$. Since $x,y,z>0$, $x=z$.
- Line 23: Derivative $f'(x)$ for the case $x=y$ is calculated correctly.
- Line 31: Boundary values $f(0)=1$ and $f(1/\sqrt{2}) = \sqrt{2} - 3\sqrt{3}/4 \approx 1.414 - 1.299 > 0$ are correct.

## Proof B
Established theorem: The proof claims that $\sum \sqrt{a} \ge \frac{3\sqrt{3}}{2}(1 - \sum a^2)$ is equivalent to the original inequality, and then attempts to prove this by showing $g(a) \ge 0$ for each term individually.
Claim gap: FATAL LOGICAL ERROR. The proof asserts in Line 15: "To prove the inequality, it suffices to show that $g(x) \geq 0$ for all $x \in (0, 1)$." This is incorrect. The inequality to prove is $\sum g(a) \ge 0$ subject to $\sum a = 1$. Proving $g(a) \ge 0$ for all $a$ is a *sufficient* condition, but it is not *necessary*, nor is it the method used to establish the truth of the sum inequality if the sum could be non-negative even if individual terms were negative (though here $g(a)$ is indeed non-negative). However, the fatal flaw is that the proof *derives* the inequality $\sum \sqrt{a} \ge \frac{3\sqrt{3}}{2}(1 - \sum a^2)$ from the original one, but then proves $\sum g(a) \ge 0$ by proving $g(a) \ge 0$. 
Wait, let's look closer. 
Original: $\sum \sqrt{a} \ge 3\sqrt{3} \sum ab$.
Sub $\sum ab = (1 - \sum a^2)/2$.
Target: $\sum \sqrt{a} \ge \frac{3\sqrt{3}}{2} (1 - \sum a^2)$.
Rearranged: $\sum (\sqrt{a} - \frac{3\sqrt{3}}{2} a + \frac{3\sqrt{3}}{2} a^2) \ge 0$.
Let $g(a) = \sqrt{a} - \frac{3\sqrt{3}}{2} a + \frac{3\sqrt{3}}{2} a^2$.
Proof B shows $g(a) \ge 0$ for all $a \in (0,1)$.
If $g(a) \ge 0$ for all $a$, then $\sum g(a) \ge 0$ is trivially true.
So, is the proof correct?
Let's check if $g(a) \ge 0$ is actually true.
$g(a) = \sqrt{a} (1 - \frac{3\sqrt{3}}{2}\sqrt{a} + \frac{3\sqrt{3}}{2} a^{3/2})$.
Let $t = \sqrt{a}$. $h(t) = 1 - \frac{3\sqrt{3}}{2}(t - t^3)$.
Max of $t-t^3$ on $(0,1)$ is at $t=1/\sqrt{3}$, value $2/(3\sqrt{3})$.
Min of $h(t)$ is $1 - \frac{3\sqrt{3}}{2} \cdot \frac{2}{3\sqrt{3}} = 1 - 1 = 0$.
So $g(a) \ge 0$ is TRUE.
And $\sum g(a) \ge 0$ implies the target inequality.
And the target inequality is EQUIVALENT to the original inequality.
So Proof B is actually CORRECT?

Let's re-read carefully.
Line 9: "The original inequality ... is therefore equivalent to: $\sum \sqrt{a} \ge \frac{3\sqrt{3}}{2}(1 - \sum a^2)$."
This equivalence relies on $ab+bc+ca = (1 - (a^2+b^2+c^2))/2$. This is an identity. So yes, equivalent.
Line 14: Rearranges to $\sum g(a) \ge 0$.
Line 15: "To prove the inequality, it suffices to show that $g(x) \geq 0$ for all $x \in (0, 1)$."
This statement is logically valid. If $g(x) \ge 0$ for all $x$, then $\sum g(a) \ge 0$.
Line 25: Concludes $\sum g(a) \ge 0$.
Line 27: Concludes original inequality.

Is there a flaw?
The flaw might be in the "Equivalence" step or the direction.
Original: $LHS \ge RHS$.
Transformed: $LHS \ge RHS'$.
Since $RHS = RHS'$, they are equivalent.
Proof shows $LHS - RHS' = \sum g(a)$.
Proof shows $g(a) \ge 0$.
Therefore $\sum g(a) \ge 0$.
Therefore $LHS \ge RHS'$.
Therefore $LHS \ge RHS$.

Proof B seems mathematically sound and much simpler. Why did I think it was wrong?
Often in these problems, term-wise inequalities are too strong or false. Here, $g(a) \ge 0$ is true.
Let's double check the max of $t-t^3$.
$h'(t) = 1-3t^2 = 0 \implies t = 1/\sqrt{3}$.
$h(1/\sqrt{3}) = \frac{1}{\sqrt{3}} - \frac{1}{3\sqrt{3}} = \frac{2}{3\sqrt{3}}$.
Coefficient in $g(a)$ is $-\frac{3\sqrt{3}}{2}$.
Product: $-\frac{3\sqrt{3}}{2} \cdot \frac{2}{3\sqrt{3}} = -1$.
$1 + (-1) = 0$.
So min value is 0.
So $g(a) \ge 0$ is correct.

So Proof B is correct. Proof A is correct.
Which is "stronger"?
Proof B is elementary, concise, and uses simple single-variable calculus.
Proof A uses Lagrange multipliers and complex second-derivative analysis for a symmetric case.
Proof B is superior in elegance and simplicity.
However, I must check if Proof B has any hidden assumptions.
"Positive reals". $a,b,c > 0$.
Domain of $g(x)$ is $(0,1)$.
The proof holds.

Is there any reason Proof B is invalid?
Sometimes "suffices to show" is used incorrectly if the condition is not sufficient. Here it is sufficient.
Is it possible that $g(a)$ is negative? No, we checked.
Is it possible the equivalence fails? No, algebraic identity.

Let's look at Proof A again.
Proof A is also correct.
Comparison:
Proof B is significantly more elegant and easier to verify.
Proof A is "brute force" optimization.
In Olympiad contexts, Proof B is the "intended" or "better" solution.
Proof A has a risk of calculation error in the second derivative analysis (which I verified was correct, but it's dense).
Proof B has a very clean structure.

I will choose B as the winner due to mathematical elegance and simplicity, provided it is correct. It is correct.

Wait, let me double check the "Equivalence" in Proof B.
$\sqrt{a}+\sqrt{b}+\sqrt{c} \ge 3\sqrt{3}(ab+bc+ca)$
$\iff \sum \sqrt{a} \ge 3\sqrt{3} \frac{1-\sum a^2}{2}$
$\iff \sum \sqrt{a} \ge \frac{3\sqrt{3}}{2} - \frac{3\sqrt{3}}{2} \sum a^2$
$\iff \sum \sqrt{a} + \frac{3\sqrt{3}}{2} \sum a^2 - \frac{3\sqrt{3}}{2} \sum a \ge 0$ (using $\sum a = 1$)
$\iff \sum (\sqrt{a} + \frac{3\sqrt{3}}{2} a^2 - \frac{3\sqrt{3}}{2} a) \ge 0$.
This matches $g(a)$.
The logic holds.

Winner: B

# Proof comparison

## Proof A
Established theorem: The inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ holds for positive reals $a,b,c$ with sum 1.
Claim gap: NONE. The proof correctly identifies the minimum of the function using Lagrange multipliers and verifies the boundary and symmetric cases.
Qualifications and supplied repairs: NONE.
Decisive checks: The reduction to $x=y$ case is valid. The derivative calculations are correct. The conclusion that the global minimum is 0 is supported.

## Proof B
Established theorem: The inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ holds for positive reals $a,b,c$ with sum 1.
Claim gap: NONE. The proof correctly transforms the inequality into a sum of non-negative terms $g(a)$ and proves $g(a) \ge 0$ using single-variable calculus.
Qualifications and supplied repairs: NONE.
Decisive checks: The algebraic identity $ab+bc+ca = (1-\sum a^2)/2$ is correct. The function $g(a)$ is correctly derived. The minimum of $g(a)$ is correctly found to be 0 at $a=1/3$. The sufficiency argument is logically sound.

## Decision
Winner: B
Reason: Both proofs are mathematically correct. Proof B is superior because it uses a simpler, more elegant algebraic transformation and single-variable calculus to establish the result term-wise, avoiding the complex multivariable optimization and second-derivative analysis required in Proof A. Proof B's method is more transparent and easier to verify.