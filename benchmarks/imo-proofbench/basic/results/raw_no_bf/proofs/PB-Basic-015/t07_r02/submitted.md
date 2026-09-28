To prove that the procedure eventually terminates and results in the cars being sorted in increasing order of width, we proceed as follows.

### 1. Termination of the Procedure
Let the $n$ cars be denoted by $C_1, C_2, \dots, C_n$. Each car $C_i$ has a length $L_i$ and a width $W_i$. The cars are initially arranged such that $L_1 < L_2 < \dots < L_n$.
A swap occurs between two adjacent cars $C_{left}$ and $C_{right}$ if and only if $L_{left} < L_{right}$ and $W_{left} > W_{right}$.
Notice that after such a swap, the car $C_{right}$ is now to the left of $C_{left}$. Since $L_{right} > L_{left}$, the condition $L_{left} < L_{right}$ is no longer satisfied for this pair. Because the swap rule only allows swapping adjacent cars where the left car is shorter than the right car, this specific pair of cars can never be swapped again.
There are $\binom{n}{2}$ possible pairs of cars. Since each pair can be swapped at most once, the total number of swaps is bounded by $\binom{n}{2}$. Thus, the procedure must eventually terminate.

### 2. Final State is Sorted by Width
We prove by induction on $n$ that the final state is sorted in increasing order of width.
**Base Case:** For $n=2$, the cars are $C_1, C_2$ with $L_1 < L_2$.
- If $W_1 < W_2$, no swap is possible. The cars are sorted by width.
- If $W_1 > W_2$, they are swapped to $(C_2, C_1)$. Now $W_2 < W_1$, and they are sorted by width.

**Inductive Step:** Assume that for any set of $n-1$ cars, the procedure terminates and the final state is sorted by width. Consider $n$ cars. Let $C_{maxL}$ be the car with the maximum length $L_{maxL}$. Initially, $C_{maxL}$ is at the far right of the row.
- $C_{maxL}$ can only participate in a swap as the $C_{right}$ car, because for it to be the $C_{left}$ car, there would need to be a car to its right with a length greater than $L_{maxL}$, which is impossible.
- Therefore, $C_{maxL}$ only moves to the left. It swaps with an adjacent car $C_i$ to its left if and only if $W_i > W_{maxL}$.
- $C_{maxL}$ stops moving left if and only if the car immediately to its left has a width $W < W_{maxL}$.
- Once $C_{maxL}$ is to the left of all cars with $W > W_{maxL}$ and to the right of all cars with $W < W_{maxL}$, it can no longer move. Since it cannot move right, it will remain at this position.

Now consider the other $n-1$ cars. The swaps between any two cars $C_i, C_j$ (where neither is $C_{maxL}$) are independent of the position of $C_{maxL}$, except that $C_{maxL}$ may temporarily separate them. However, since $C_{maxL}$ only moves left, it will eventually move past any car it can swap with. By the inductive hypothesis, the $n-1$ cars will eventually be sorted in increasing order of width.
Once the $n-1$ cars are sorted as $C_{\pi(1)}, C_{\pi(2)}, \dots, C_{\pi(n-1)}$ such that $W_{\pi(1)} < W_{\pi(2)} < \dots < W_{\pi(n-1)}$, $C_{maxL}$ will continue to swap with the car to its left as long as that car has a width greater than $W_{maxL}$. It will eventually settle at the position $r+1$, where $r$ is the number of cars with $W < W_{maxL}$.
In this final configuration, $C_{maxL}$ is placed such that all cars to its left have smaller widths and all cars to its right have larger widths. Since the other $n-1$ cars are already sorted by width, the entire sequence of $n$ cars is sorted in increasing order of width.

By induction, the procedure always ends with the cars sorted by width. $\square$
