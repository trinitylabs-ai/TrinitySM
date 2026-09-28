Arbitrarily pick any one person - call her Pip - and her $n$ arcs.
 The initial idea is to try to apply Hall's marriage lemma to match
 the $n$ people with Pip's arcs (such that each such person is happy
 with their matched arc). To that end, construct the obvious bipartite
 graph $\mathfrak{G}$ between the people and the arcs for Pip.

 We now consider the following algorithm, which takes several steps.
 \begin{itemize}
 \item If a perfect matching of $\mathfrak{G}$ exists, we're done!
 \item We're probably not that lucky. Per Hall's condition, this means there
 is a bad set $\mathcal{B}_{1}$ of people, who are compatible with
 fewer than $\left|\mathcal{B}_{1}\right|$ of the arcs. Then delete
 $\mathcal{B}_{1}$ and the neighbors of $\mathcal{B}_{1}$, then try
 to find a matching on the remaining graph.
 \item If a matching exists now, terminate the algorithm. Otherwise, that
 means there's another bad set $\mathcal{B}_{2}$ for the remaining
 graph. We again delete $\mathcal{B}_{2}$ and the fewer than $\mathcal{B}_{2}$
 neighbors.
 \item Repeat until some perfect matching $\mathcal{M}$ is possible in the
 remaining graph, i.e. there are no more bad sets (and then terminate
 once that occurs).
 \end{itemize}
 Since Pip is a universal vertex, it's impossible to delete Pip, so
 the algorithm does indeed terminate with nonempty $\mathcal{M}$.

 We commit to assigning each of person in $\mathcal{M}$ their matched
 arc (in particular if there are no bad sets at all, the problem is
 already solved). Now we finish the problem by induction on $n$ (for
 the remaining people) by simply deleting the arcs used up by $\mathcal{M}$.

 To see why this deletion-induction works, consider any particular
 person Quinn not in $\mathcal{M}$. By definition, Quinn is not happy
 with any of the $\operatorname{arcs}$ in $\mathcal{M}$. So when
 an $\operatorname{arc}\mathcal{A}$ of $\mathcal{M}$ is deleted,
 it had value less than 1 for Quinn so in particular it couldn't contain
 entirely any of Quinn's arcs. Hence at most one endpoint among Quinn's
 arcs was in the deleted $\operatorname{arc}\mathcal{A}$. When this
 happens, this causes two arcs of Quinn to merge, and the merged value
 is

 \[
 (\geq1)+(\geq1)-(\leq1)\quad\geq1
 \]

 meaning the induction is OK.