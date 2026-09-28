The answer is that Alice wins. Let's define a Bob-set $V$ to be
 a set of points in the plane with no three collinear and with all
 distances at least 1 . The point of the problem is to prove the following
 fact.

 Claim - Given a Bob-set $V\subseteq\mathbb{R}^{2}$, consider the
 Bob-graph with vertex set $V$ defined as follows: draw edge $ab$
 if and only if the disk with diameter $\overline{ab}$ contains no
 other points of $V$ on or inside it. Then the Bob-graph is connected
 and planar.

 Proving this claim shows that Alice wins since Alice can specify $\mathcal{S}$
 to be the set of points outside the disk of diameter $PQ$.

 We start with proving that every Bob-graph is connected. Assume for
 contradiction the graph is disconnected. Let $p$ and $q$ be two
 points in different connected components. Since $pq$ is not an edge,
 there exists a third point $r$ inside the disk with diameter $\overline{pq}$.

 Hence, $r$ is in a different connected component from at least one
 of $p$ or $q$ - let's say point $p$. Then we repeat the same argument
 on the disk with diameter $\overline{pr}$ to find a new point $s$,
 non-adjacent to either $p$ or $r$. See the figure below, where the
 X'ed out dashed edges indicate points which are not only non-adjacent
 but in different connected components.

 In this way we generate an infinite sequence of distances $\delta_{1},\delta_{2},\delta_{3},\ldots$
 among the non-edges in the picture above. By the "Pythagorean theorem"
 (or really the inequality for it), we have

 \[
 \delta_{i}^{2}\leq\delta_{i-1}^{2}-1
 \]

 and this eventually generates a contradiction for large $i$, since
 we get $0\leq\delta_{i}^{2}\leq\delta_{1}^{2}-(i-$ $1)$.

 Now we prove that every Bob-graph is planar. Assume for contradiction
 that edges $ac$ and $bd$ meet, meaning $abcd$ is a convex quadrilateral.
 WLOG assume $\angle bad\geq90^{\circ}$ (each quadrilateral has an
 angle at least $90^{\circ}$ ). Then the disk with diameter $\overline{bd}$
 contains $a$, contradiction.