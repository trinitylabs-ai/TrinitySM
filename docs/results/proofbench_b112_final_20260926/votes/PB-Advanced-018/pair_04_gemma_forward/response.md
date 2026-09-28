# Proof comparison

## Proof A
Established theorem: For $n \ge 5$, the constant $L=3$ satisfies the inequality $|La(n) - n^2| \le n + 2\sqrt{n} + 3$, provided that $a(n) = \lfloor n^2/3 \rfloor + 1$.
Claim gap: The proof does not rigorously establish that $a(n) = \lfloor n^2/3 \rfloor + 1$. The upper bound $a(n) \le \lfloor n^2/3 \rfloor + 1$ relies on an unproven claim that removing a subgraph with maximum degree 2 from an $n \times n$ grid graph does not destroy all paths of length $n-1$. The lower bound $a(n) \ge \lfloor n^2/3 \rfloor + 1$ relies on an unproven claim that a specific tiling of $1 \times 3$ blocks can block all paths of length $n-1$.
Qualifications and supplied repairs: None.
Decisive checks:
- Verified that for $k = \lfloor n^2/3 \rfloor + 1$, the balance property implies $q = \lfloor n^2/k \rfloor = 2$ for all $n \ge 5$.
- Verified that if $q=2$, each color class has size at most 3. Since the grid is bipartite, no color class can form a triangle, so the monochromatic subgraph $G_{mono}$ has maximum degree 2.
- Verified the arithmetic: $|3(\lfloor n^2/3 \rfloor + 1) - n^2| = |3\lfloor n^2/3 \rfloor + 3 - n^2|$. Letting $n^2 = 3m + r$ with $r \in \{0, 1, 2\}$, this equals $|3m + 3 - (3m + r)| = |3 - r|$, which is $\le 3$.
- Verified that $3 \le n + 2\sqrt{n} + 3$ for $n \ge 5$.

## Proof B
Established theorem: For $n \ge 5$, the constant $L=2$ satisfies the inequality $|La(n) - n^2| \le n + 2\sqrt{n} + 3$, provided that $a(n) = \lfloor n^2/2 \rfloor + 1$.
Claim gap: The proof fails to justify the value of $a(n)$. The upper bound $a(n) \le \lfloor n^2/2 \rfloor + 1$ is based on a false lemma (that removing a matching from a Hamiltonian bipartite graph with $N$ vertices leaves a path of length at least $N/2$). The lower bound is entirely missing.
Qualifications and supplied repairs: None.
Decisive checks:
- Falsified the central lemma: Let $G$ be a cycle $C_4$ (a Hamiltonian bipartite graph with $N=4$). Let $S$ be a perfect matching of size 2. $G \setminus S$ consists of two disjoint edges, so the longest path has length 1, which is less than $N/2 = 2$.
- Verified the arithmetic: $|2(\lfloor n^2/2 \rfloor + 1) - n^2| \le 2$.
- Verified that $2 \le n + 2\sqrt{n} + 3$ for $n \ge 5$.

## Decision
Winner: A
Reason: Proof A is significantly stronger because it attempts to establish both an upper and lower bound for $a(n)$ using plausible, albeit vague, arguments. Proof B relies on a demonstrably false lemma to justify its upper bound and provides no argument for the lower bound. Both proofs correctly calculate the constant $L$ based on their respective (unproven) claims for $a(n)$, but Proof A's premise is mathematically plausible while Proof B's is not.