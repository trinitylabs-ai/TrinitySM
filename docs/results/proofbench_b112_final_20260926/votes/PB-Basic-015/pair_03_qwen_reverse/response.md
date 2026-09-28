# Proof comparison

## Proof A
Established theorem: The procedure terminates after at most $n(n-1)/2$ swaps. In any terminal state, the car with maximum width occupies position $n$. By induction on $n$, any terminal state reached from a length-sorted initial configuration is sorted in increasing order of width.
Claim gap: Minor implicit assumption in the inductive step (lines 25-27) that the final relative ordering of the $n-1$ cars constitutes a valid terminal state for the isolated $n-1$ car process. The proof asserts this without explicitly justifying that interleaved swaps with $C_W$ do not restrict or alter the set of reachable terminal configurations for the remaining cars.
Qualifications and supplied repairs: Supplied explicit justification that (1) swaps involving $C_W$ only move $C_W$ rightward and never change the relative order of any two cars among the remaining $n-1$, and (2) adjacency blocking by $C_W$ cannot permanently prevent a valid swap between two other cars from eventually occurring, so the final relative order is indeed a terminal state for the isolated system. This is routine but was omitted in the text.
Decisive checks: 
- Termination (lines 5-7): Verified. Each swap places a larger length to the left of a smaller length, strictly increasing length inversions from $0$ to at most $n(n-1)/2$. Bounded monotonic integer guarantees termination.
- Widest car position (lines 10-20): Verified. $C_W$ cannot move left (swap requires $W_{left} > W_{right}$). Invariant that cars to the right of $C_W$ have $L > L_W$ holds initially and is preserved under swaps. Terminal condition forces $C_W$ to position $n$.
- Induction (lines 23-28): Verified after supplying the minor justification above. The restricted sequence is terminal for the $n-1$ cars, started length-sorted, so IH applies. Conclusion follows.

## Proof B
Established theorem: The procedure terminates after at most $\text{Inv}(W)$ swaps. In any terminal state, the sequence of widths is strictly increasing. The proof holds for any sequence of valid swap choices.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Termination (lines 4-10): Verified. Each swap requires $W_{left} > W_{right}$, so swapping them fixes exactly one width inversion while preserving all others. $\text{Inv}(W)$ decreases by exactly $1$ per step, bounded below by $0$. Termination is guaranteed independently of swap choices.
- Final order (lines 13-27): Verified. Termination implies $\forall i, (W'_i > W'_{i+1} \implies L'_i > L'_{i+1})$. Assuming a width inversion exists at $i, i+1$ yields cars $C_a, C_b$ with $L_a > L_b$ and $W_a > W_b$. Initial length sorting implies $b < a$, so $C_b$ started left of $C_a$. Lines 24-25 correctly verify that neither ordering $(C_b, C_a)$ nor $(C_a, C_b)$ satisfies the swap condition ($L_{left} < L_{right} \land W_{left} > W_{right}$). Thus their relative order is invariant. The final state places $C_a$ left of $C_b$, contradicting the invariant. Hence no width inversion exists, and the final state is width-sorted.

## Decision
Winner: B
Reason: Both proofs are mathematically correct and fully establish termination and the final width-sorted state. Proof B is preferred because its argument for the final configuration is direct, self-contained, and avoids induction. By proving that pairs with $L_a > L_b$ and $W_a > W_b$ can never swap, B establishes an invariant relative order that immediately contradicts the existence of any width inversion in a terminal state. Proof A's induction is valid but relies on an implicit (though easily justified) claim that the presence of the widest car does not alter the set of reachable terminal states for the remaining $n-1$ cars. B's contradiction argument handles the "no matter how Adrian chooses" condition more transparently and requires fewer auxiliary lemmas, making it the stronger justified solution as written.