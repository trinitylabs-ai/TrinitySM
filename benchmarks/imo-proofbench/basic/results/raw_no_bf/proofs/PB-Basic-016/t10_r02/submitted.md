To prove that the target state is unreachable from the initial state, we use the concept of the winding number (or index) of a 3-coloring of a cycle graph.

### 1. Definition of the Winding Number
Let the three colors be represented by the set $\mathbb{Z}_3 = \{0, 1, 2\}$, where $0$ corresponds to Red (R), $1$ to White (W), and $2$ to Blue (B). For any two distinct colors $a, b \in \mathbb{Z}_3$, we define the directed difference $f(a, b)$ as:
\[ f(a, b) = \begin{cases} 1 & \text{if } b \equiv a + 1 \pmod 3 \\ -1 & \text{if } b \equiv a - 1 \pmod 3 \end{cases} \]
For a given coloring $C = (c_1, c_2, \dots, c_{101})$ of the stones, we define the total sum of differences around the circle as:
\[ S(C) = \sum_{i=1}^{100} f(c_i, c_{i+1}) + f(c_{101}, c_1) \]
The winding number is defined as $W(C) = \frac{1}{3} S(C)$. Since $f(a, b) \equiv b - a \pmod 3$, the sum $S(C) \equiv \sum (c_{i+1} - c_i) \equiv 0 \pmod 3$, ensuring that $W(C)$ is always an integer.

### 2. Invariance under Recoloring
We consider the effect of repainting a single stone $k$. For a stone to be repainted from color $c_k$ to $c_k'$, the adjacency constraint requires that $c_k$ and $c_k'$ must both be different from the colors of the neighbors $c_{k-1}$ and $c_{k+1}$ (with indices taken modulo 101). 
In a 3-coloring, if $c_{k-1} \neq c_{k+1}$, there is only one available color for stone $k$, making recoloring impossible. Thus, a stone can only be repainted if $c_{k-1} = c_{k+1}$. 

Let $c_{k-1} = c_{k+1} = a$. The contribution of stone $k$ to the sum $S(C)$ is $f(a, c_k) + f(c_k, a)$. Since $f(a, b) = -f(b, a)$ for all $a \neq b$, we have:
\[ f(a, c_k) + f(c_k, a) = 0 \]
When $c_k$ is changed to $c_k'$, the new contribution is $f(a, c_k') + f(c_k', a) = 0$. Consequently, the sum $S(C)$ and the winding number $W(C)$ remain unchanged by any valid modification.

### 3. Calculating $W(S_0)$ and $W(S_T)$
Assign $R=0, W=1, B=2$.
**Initial State $S_0$:** $c_{101} = 2$, $c_i = 1$ for $i$ odd, $c_i = 0$ for $i$ even.
- For $i \in \{1, 3, \dots, 99\}$, $f(c_i, c_{i+1}) = f(1, 0) = -1$ (50 terms).
- For $i \in \{2, 4, \dots, 98\}$, $f(c_i, c_{i+1}) = f(0, 1) = 1$ (49 terms).
- $f(c_{100}, c_{101}) = f(0, 2) = -1$.
- $f(c_{101}, c_1) = f(2, 1) = -1$.
$S(S_0) = 50(-1) + 49(1) - 1 - 1 = -50 + 49 - 2 = -3 \implies W(S_0) = -1$.

**Target State $S_T$:** $c_{101} = 2$, $c_i = 0$ for $i$ odd, $c_i = 1$ for $i$ even.
- For $i \in \{1, 3, \dots, 99\}$, $f(c_i, c_{i+1}) = f(0, 1) = 1$ (50 terms).
- For $i \in \{2, 4, \dots, 98\}$, $f(c_i, c_{i+1}) = f(1, 0) = -1$ (49 terms).
- $f(c_{100}, c_{101}) = f(1, 2) = 1$.
- $f(c_{101}, c_1) = f(2, 0) = 1$.
$S(S_T) = 50(1) + 49(-1) + 1 + 1 = 50 - 49 + 2 = 3 \implies W(S_T) = 1$.

### 4. Conclusion
Since the winding number is an invariant under the allowed modifications and $W(S_0) = -1 \neq 1 = W(S_T)$, it is impossible to reach state $S_T$ from state $S_0$.

\(\square\)
