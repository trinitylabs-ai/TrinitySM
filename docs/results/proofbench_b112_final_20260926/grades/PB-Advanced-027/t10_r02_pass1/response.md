The complex-number reformulation is essentially correct (assuming \(P\ne Q\)), but the strategic argument fails.

The decisive error is in Case 1: an open disk does not necessarily contain a point avoiding finitely many unit disks. For Alice’s successful choice, after normalizing \(P=0,Q=1\), the forbidden set \(F\) is the disk with diameter \([0,1]\). If
\[
u=\frac{v_{n+1}-v_1}{v_n-v_1}\in F,
\]
then
\[
|u|^2+|1-u|^2\le 1.
\]
Writing \(\delta_n=|v_n-v_1|\), this gives
\[
\delta_{n+1}^2+|v_{n+1}-v_n|^2\le \delta_n^2.
\]
Since distinct cities must be more than one unit apart,
\[
\delta_{n+1}^2<\delta_n^2-1,
\]
so the proposed construction cannot continue indefinitely. This is precisely the mechanism ensuring connectivity in the reference solution.

Case 2b also relies on the false assertion that a finite union of sets with empty interior cannot cover the plane. For example, \(\mathbb Q^2\) and its complement both have empty interior but cover \(\mathbb R^2\). Thus the existence of \(v_n\) is not established.

The submission concludes incorrectly that Bob wins and neither identifies Alice’s exterior-of-the-diameter-circle strategy nor proves the required connectivity or planarity. The correct ratio reformulation alone does not meet the stated partial-credit criteria.

<points>0 out of 7</points>