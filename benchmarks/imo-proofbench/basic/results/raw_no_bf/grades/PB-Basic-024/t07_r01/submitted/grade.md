The proposed solution is complete and correct.

- For \(c=0\), it correctly derives \(20^a+b^4=1\), forcing \(a=0\) and \(b=0\).
- For \(c\ge1\), reducing modulo \(11\) gives
  \[
  b^4\equiv-9^a\pmod{11}.
  \]
- The powers \(9^a\pmod{11}\) cycle through \(\{1,9,4,3,5\}\), so \(-9^a\) lies in \(\{2,6,7,8,10\}\).
- The fourth-power residues modulo \(11\) are correctly calculated as \(\{0,1,3,4,5,9\}\).
- These sets are disjoint, ruling out every \(c\ge1\).

Thus the unique solution is rigorously established as \((a,b,c)=(0,0,0)\).

<points>7 out of 7</points>