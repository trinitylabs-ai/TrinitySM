# Proof comparison

## Proof A
Established theorem: None rigorously proven, but correctly identifies that a small constant number of penalties suffice (the actual answer is $n=3$). The submission attempts to prove sufficiency for 3 penalties.
Claim gap: Fatal local defect in the path construction for the 3-penalty case. The strategy assumes horizontal moves in untested rows are safe based only on row indices, ignoring that unknown obstacles can block those moves.
Qualifications and supplied repairs: NONE. The gap is intrinsic to the submitted path; no routine step bridges it.
Decisive checks: 
- Line 16 claims: "The horizontal move $(r_2-1, 3) \to (r_2-1, 1)$ is safe if $r_2-1 \neq r_1$ and $r_2-1 \neq r_3$." This is false. Safety depends on column occupancy, not row indices. Peter could place the obstacle for row $r_2-1$ at column 2, directly blocking the move. James has no information to guarantee safety here.
- Falsification check: Let $r_1=10, r_2=12, r_3=14$. Peter places obstacles at $(10,1), (12,2), (14,3)$ and $(11,2)$. James's prescribed path attempts $(11,3) \to (11,1)$, passing through $(11,2)$, which is forbidden. The construction fails. However, the core intuition that $\le 3$ penalties suffice is correct; a simpler weaving strategy with only 2 penalties actually works, making A's bound conservative but directionally sound.

## Proof B
Established theorem: 3000 penalties are sufficient (trivial upper bound). The submission claims $n=3001$ is necessary and sufficient.
Claim gap: Fundamental logical error in the necessity argument. The proof correctly identifies that columns in $C_{hit}$ are safe for unhit rows, but incorrectly concludes James cannot route between them. It fails to recognize that James can switch columns horizontally in rows $R_{hit}$ (where obstacles are known), making $|C_{hit}| \ge 2$ sufficient to bypass all known obstacles.
Qualifications and supplied repairs: NONE. The defect invalidates the lower bound entirely.
Decisive checks:
- Lines 14-21 argue that with $m < 3000$ penalties, James is blocked because he cannot move horizontally in unhit rows. This overlooks that horizontal moves are only needed in rows $R_{hit}$ to bypass known obstacles. In any $r \in R_{hit}$, James knows the forbidden column $c_r$ and can safely move to any other column in $C_{hit}$. Thus, once $|C_{hit}| \ge 2$, James can weave between safe columns through all rows.
- Falsification check: Let $m=2$. James hits $(r_1, 1)$ and $(r_2, 2)$. Columns 1 and 2 are cleared for all other rows. James moves down col 1 to $r_1-1$, switches to col 2 in row $r_1$ (avoiding $(r_1,1)$), moves down col 2 to $r_2-1$, switches to col 1 in row $r_2$ (avoiding $(r_2,2)$), and continues. This path is guaranteed safe with only 2 penalties, directly contradicting B's claim that 3000 are necessary.

## Decision
Winner: A
Reason: Proof A correctly identifies the problem's scale (a small constant number of penalties) and proposes a viable testing framework, though its specific 3-penalty path construction contains a local safety gap. Proof B's sufficiency argument is trivially correct but its necessity argument contains a critical conceptual flaw: it ignores that hitting a column clears it for all other rows, and misses that column switching can be safely performed in known rows. This leads B to a grossly incorrect lower bound ($n=3001$ vs actual $n=3$). A's defect is a repairable construction error in an overcomplicated route, while B's defect invalidates its entire minimax claim. A is mathematically stronger and closer to the true solution.