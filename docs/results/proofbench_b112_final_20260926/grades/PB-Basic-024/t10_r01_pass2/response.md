The proposed solution is complete and correct.

- For \(c=0\), it correctly derives \(a=0\) and then \(b=0\).
- For \(c\ge1\), reduction modulo \(11\) gives
  \[
  b^4\equiv -9^a\pmod{11}.
  \]
- The powers of \(9\) modulo \(11\) are correctly listed as \(\{1,3,4,5,9\}\), so \(-9^a\) belongs to \(\{2,6,7,8,10\}\).
- The fourth-power residues modulo \(11\) are correctly found to be \(\{0,1,3,4,5,9\}\).
- These sets are disjoint, yielding a valid contradiction for every \(a\) when \(c\ge1\).

Thus the unique solution is rigorously established as \((0,0,0)\).

<points>7 out of 7</points>