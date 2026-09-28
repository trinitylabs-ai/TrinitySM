To prove that it is impossible to reach the target state from the initial state, we use a topological invariant known as the winding number (or index) of a 3-coloring of a cycle graph.

### 1. Formal Setup
Let the stones be vertices of a cycle graph $C_{101}$, with vertices $V = \{1, 2, \dots, 101\}$. Let the colors be represented by the elements of $\mathbb{Z}_3 = \{0, 1, 2\}$. We assign:
- Blue $\to 0$
- White $\to 1$
- Red $\to 2$

A coloring is a function $f: V \to \mathbb{Z}_3$. A coloring is proper if $f(i) \neq f(i+1)$ for all $i$ (with $102 \equiv 1$). The operation described is a single-vertex recoloring: changing $f(k)$ to $f'(k)$ such that the coloring remains proper.

### 2. The Winding Number Invariant
For any proper 3-coloring $f$, we define the difference between adjacent stones $i$ and $i+1$ as $d_i \in \{1, -1\}$, where:
\[ d_i = \begin{cases} 1 & \text{if } f(i+1) - f(i) \equiv 1 \pmod 3 \\ -1 & \text{if } f(i+1) - f(i) \equiv 2 \pmod 3 \end{cases} \]
The winding number $W$ of the coloring $f$ is defined as the sum of these differences:
\[ W(f) = \sum_{i=1}^{101} d_i \]
Note that $\sum_{i=1}^{101} d_i \equiv \sum_{i=1}^{101} (f(i+1) - f(i)) \equiv 0 \pmod 3$. Since $W(f)$ is the sum of 101 odd numbers, it must be an odd multiple of 3.

### 3. Invariance Under Recoloring
Suppose we change the color of stone $k$ from $f(k)$ to $f'(k)$. Only the differences $d_{k-1}$ and $d_k$ are affected. Let $x = f(k-1)$, $y = f(k)$, $z = f(k+1)$, and $y' = f'(k)$. The change in $W$ is:
\[ \Delta W = (d'_{k-1} - d_{k-1}) + (d'_k - d_k) \]
where $d_{k-1} = \text{sgn}(y-x)$, $d_k = \text{sgn}(z-y)$, $d'_{k-1} = \text{sgn}(y'-x)$, and $d'_k = \text{sgn}(z-y')$, with $\text{sgn}(a) = 1$ if $a \equiv 1 \pmod 3$ and $-1$ if $a \equiv 2 \pmod 3$.

- If $x \neq z$, then there is only one color in $\mathbb{Z}_3 \setminus \{x, z\}$. Thus, $y$ must equal $y'$, and $\Delta W = 0$.
- If $x = z$, then $y$ and $y'$ must be the two distinct colors in $\mathbb{Z}_3 \setminus \{x\}$. Let $x=0$. Then $\{y, y'\} = \{1, 2\}$.
  - If $y=1, y'=2$: $d_{k-1} = \text{sgn}(1-0)=1, d_k = \text{sgn}(0-1)=-1$. New values: $d'_{k-1} = \text{sgn}(2-0)=-1, d'_k = \text{sgn}(0-2)=1$.
    $\Delta W = (-1 - 1) + (1 - (-1)) = -2 + 2 = 0$.
  - If $y=2, y'=1$: $d_{k-1} = -1, d_k = 1$. New values: $d'_{k-1} = 1, d'_k = -1$.
    $\Delta W = (1 - (-1)) + (-1 - 1) = 2 - 2 = 0$.

In all cases, $\Delta W = 0$. Thus, $W$ is invariant under the allowed operations.

### 4. Calculation for Initial and Final States
**Initial State $C_0$:**
$f(101)=0$, $f(1)=1, f(2)=2, f(3)=1, f(4)=2, \dots, f(99)=1, f(100)=2$.
- For $i=1, \dots, 99$: $d_i = \text{sgn}(f(i+1)-f(i))$. This sequence is $1, -1, 1, -1, \dots, 1$.
  The sum $\sum_{i=1}^{99} d_i = 1$.
- $d_{100} = \text{sgn}(f(101)-f(100)) = \text{sgn}(0-2) = \text{sgn}(1) = 1$.
- $d_{101} = \text{sgn}(f(1)-f(101)) = \text{sgn}(1-0) = \text{sgn}(1) = 1$.
$W(C_0) = 1 + 1 + 1 = 3$.

**Target State $C_{final}$:**
$f(101)=0$, $f(1)=2, f(2)=1, f(3)=2, f(4)=1, \dots, f(99)=2, f(100)=1$.
- For $i=1, \dots, 99$: $d_i = \text{sgn}(f(i+1)-f(i))$. This sequence is $-1, 1, -1, 1, \dots, -1$.
  The sum $\sum_{i=1}^{99} d_i = -1$.
- $d_{100} = \text{sgn}(f(101)-f(100)) = \text{sgn}(0-1) = \text{sgn}(2) = -1$.
- $d_{101} = \text{sgn}(f(1)-f(101)) = \text{sgn}(2-0) = \text{sgn}(2) = -1$.
$W(C_{final}) = -1 - 1 - 1 = -3$.

Since $W(C_0) = 3$ and $W(C_{final}) = -3$, and $W$ is invariant, it is impossible to reach the target state. $\square$
