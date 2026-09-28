The column-testing strategy correctly proves only the weak bound \(n\le 3001\).

The claimed lower bound is invalid:

- Peter cannot freely choose the columns of subsequently encountered obstacles; these depend on James’s path.
- The proposed invariant that encountered columns can remain pairwise nonadjacent is impossible: among \(3001\) columns, at most \(1501\) can be pairwise nonadjacent, far fewer than \(3000\).
- The assertion that Peter can place each \(c_p\) between every relevant pair of columns is unsupported and generally impossible.
- The argument tracks only encountered selected cells, ignoring information obtained from cells James has safely traversed.
- Consequently, the claimed obstruction to switching columns is not established.

Indeed, the ground-truth strategy guarantees success before the third penalty, directly refuting the proposed lower bound. The submission also solves neither the edge nor non-edge case required for the upper bound \(n\le3\), and it does not present a rigorous standalone proof of \(n\ge3\). Thus the listed partial-credit criteria are not met.

<points>0 out of 7</points>