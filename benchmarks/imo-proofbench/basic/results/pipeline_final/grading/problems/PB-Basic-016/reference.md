Let $A$ be the number of indices $i$ where $i$th stone is blue and $i+1$th stone is white (we define the order in mod 101). Similarly, let $C$ be the number of white stones followed by blue stones. In the initial state, we have $A = 1$ and $C = 0$, and in the final state, we have $A = 0$ and $C = 1$.

 We claim that $A - C$ is invariant. Indeed, consider all possible colorings of three consecutive stones, and let us enumerate what color the middle side can be changed to. Writing $R, W, B$ to represent red, white, and blue, we have the following possibilities:
 \[ RBR \to RWR, \qquad RWR \to RBR, \]
 \[ BWB \to BRB, \qquad BRB \to BWB, \]
 \[ WBW \to WRW, \qquad WRW \to WBW. \]
 In each case, we find that the quantity $A - C$ doesn't change. However, the initial state has $A - C = 1$, and the final state has $A - C = -1$, so it is not possible to reach the final state.
