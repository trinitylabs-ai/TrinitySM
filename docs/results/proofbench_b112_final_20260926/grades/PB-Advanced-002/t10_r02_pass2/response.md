The Boolean-matrix reformulation is correct, and the solution makes meaningful progress by reducing the problem to bounding the number of distinct sets in one trajectory.

However, the decisive bounds are merely asserted:

- The characterization of the eventual period using SCC cyclicities is nontrivial and is not proved.
- More importantly, the claim that every \(120\times120\) Boolean matrix has preperiod \(P\le120^2\) is a major theorem, not a consequence of eventual periodicity alone. No justification is supplied, although this is essential to the argument.
- The numerical claim \(g(120)\approx3\cdot10^6\) is false. For example, the partition
  \[
  120=16+9+5+7+11+13+17+19+23
  \]
  gives
  \[
  g(120)\ge16\cdot9\cdot5\cdot7\cdot11\cdot13\cdot17\cdot19\cdot23
  =5{,}354{,}228{,}880.
  \]
  Although a correct sufficiently small bound could be obtained, it is absent from the submitted proof.

Thus the submission has a relevant orbit/SCC strategy, but the central stabilization argument is replaced by unsupported assertions and the stated numerical estimate is incorrect. This is substantial partial progress, not an almost-complete rigorous proof.

<points>1 out of 7</points>