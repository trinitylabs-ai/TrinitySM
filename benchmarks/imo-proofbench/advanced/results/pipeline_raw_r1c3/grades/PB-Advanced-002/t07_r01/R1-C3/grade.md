The solution has a plausible overall strategy, and it correctly reduces the problem—under the literal ordered definition—to bounding the length of an orbit of \(f\). It also identifies SCC periods and an LCM/Landau-function bound as relevant.

However, the essential estimates are not proved:

- The claim that powers of every \(120\times120\) Boolean matrix have pre-period at most \(120^2\) is a substantial theorem and is merely asserted. This is a major component of the proof.
- The numerical bound \(g(120)<2\cdot10^{10}\) is also asserted without justification.
- The statement that the eventual period from a vertex equals the LCM of all reachable SCC periods is not generally true; only divisibility by such an LCM is guaranteed. For example, a looped vertex feeding into a directed \(2\)-cycle can yield an eventually constant reachable set despite the reachable SCC periods having LCM \(2\).
- The claim that each singleton sequence becomes periodic within \(n\) steps is false in general; Boolean-matrix transients can be quadratic.

Although the incorrect equality can be weakened to obtain the needed upper bound, the unproved quadratic-transient and Landau estimates are central, not minor omissions. Thus the submission is not eligible for 6 or 7 points, but its orbit reduction and LCM/SCC framework constitute the specified partial progress.

<points>1 out of 7</points>