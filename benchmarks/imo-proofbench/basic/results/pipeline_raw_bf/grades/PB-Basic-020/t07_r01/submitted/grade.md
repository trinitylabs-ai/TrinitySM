The solution’s overall structure is valid:

- It correctly factors the equation as  
  \[
  a(a-b)=(b+1)(b^2-b+1)
  \]
  and divides into the two possible divisibility cases.
- In Case 1, the algebra and discriminant calculation are correct. However, the claim that the discriminant is negative for every \(m\ge2\) merely because its leading coefficient is negative and it is negative at \(m=2\) is not logically sufficient. This is a minor, locally repairable gap: indeed,
  \[
  D=-m^2(3m^2+2m-7)-2m+1<0
  \]
  for \(m\ge2\), since \(3m^2+2m-7>0\).
- In Case 2, the parametrization, discriminant computation, and treatment of \(n=1,2\) are correct.
- For \(n\ge3\), the discriminant is correctly placed strictly between the consecutive squares
  \[
  (n^2+n+2)^2 \quad\text{and}\quad (n^2+n+3)^2,
  \]
  excluding further solutions.
- The resulting pair \((7,3)\) is correctly verified.

Thus the proof is essentially complete, with only a small unjustified inequality claim that is easily repaired.

<points>6 out of 7</points>