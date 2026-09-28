The case \(f(0)=0\) is handled correctly: the argument establishes surjectivity for a nonzero solution and then obtains \(f(x)=-x\), while \(f\equiv0\) is also verified.

For \(c=f(0)\ne0\), the important identity
\[
f(c+f(b))=b-c
\]
is correctly derived. However, there are two gaps:

- Several subsequent divisions require exclusions such as \(x\ne0,c\) and \(f(b)\ne0\), which are not stated.
- More importantly, the quadratic relation only implies pointwise that
  \[
  f(x)\in\{-c,c-x\},
  \]
  not that one of these formulas holds globally. The submitted dichotomy between the two global functions is therefore unjustified.

This gap is locally repairable using the already-established identity: if \(f(x)=-c\), then
\[
f(c+f(x))=f(0)=c=x-c,
\]
so \(x=2c\), where \(-c=c-x\) anyway. Hence \(f(x)=c-x\) everywhere. Thus the core solution is correct, but a necessary final exclusion of mixed branches is missing.

<points>6 out of 7</points>