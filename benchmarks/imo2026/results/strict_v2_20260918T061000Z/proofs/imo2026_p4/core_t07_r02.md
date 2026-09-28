To determine the values of $\theta \in (0^\circ, 180^\circ)$ for which Mulan can guarantee victory in finitely many steps, we define the set of "winning angles" $W = \{n\theta \mid n \in \mathbb{Z}^+, n\theta < 180^\circ\}$. A triangle is said to be in a winning state if at least one of its angles is in $W$.

### 1. Sufficiency of $\theta = 180^\circ/k$ for $k \in \{2, 3, \dots\}$
Suppose $\theta = 180^\circ/k$ for some integer $k \ge 2$. Then $W = \{\theta, 2\theta, \dots, (k-1)\theta\}$. Note that for any $\phi \in W$, the supplementary angle $180^\circ - \phi$ is also in $W$ because $180^\circ - n\theta = (k-n)\theta$, and $1 \le n < k$ implies $1 \le k-n < k$.

First, we show that if a triangle $T$ has an angle $\phi = n\theta \in W$, Mulan can force an angle $\theta$ in at most $n-1$ steps. If $n=1$, she has already won. If $n > 1$, she can cut the angle $n\theta$ into $\theta$ and $(n-1)\theta$. The two resulting triangles $T_1$ and $T_2$ will have angles $\theta$ and $(n-1)\theta$, respectively. Regardless of which triangle Shan-Yu keeps, the new triangle will have an angle in $W$ with a smaller multiple of $\theta$. By induction, she wins in finitely many steps.

Next, we show that Mulan can force a winning state from any triangle $T$ with angles $\alpha, \beta, \gamma$. Let $\alpha$ be the largest angle, so $\alpha \ge 60^\circ$. Mulan chooses a cut that splits $\alpha$ into $\alpha_1$ and $\alpha_2$ ($\alpha_1 + \alpha_2 = \alpha$). The resulting triangles $T_1$ and $T_2$ have angles $(\alpha_1, \beta, 180^\circ - \alpha_1 - \beta)$ and $(\alpha_2, \gamma, 180^\circ - \alpha_2 - \gamma)$.
Mulan can force a winning state if she can choose $\alpha_1 \in (0, \alpha)$ such that both $T_1$ and $T_2$ contain an angle in $W$. She can achieve this by picking $\alpha_1$ such that $180^\circ - \alpha_1 - \beta = \phi_1$ for some $\phi_1 \in W$. Then $T_1$ has an angle $\phi_1 \in W$. For $T_2$, the third angle is $180^\circ - \alpha_2 - \gamma = 180^\circ - (\alpha - \alpha_1) - \gamma = 180^\circ - \alpha + (180^\circ - \beta - \phi_1) - \gamma = 360^\circ - (\alpha + \beta + \gamma) - \phi_1 = 180^\circ - \phi_1$. Since $\phi_1 \in W \implies 180^\circ - \phi_1 \in W$, $T_2$ also has an angle in $W$.

This cut is valid if $0 < \alpha_1 < \alpha$, which simplifies to $0 < 180^\circ - \beta - \phi_1 < \alpha$.
The first inequality is $\phi_1 < 180^\circ - \beta = \alpha + \gamma$.
The second inequality is $\phi_1 > 180^\circ - \beta - \alpha = \gamma$.
Thus, Mulan needs to find $\phi_1 \in W$ such that $\gamma < \phi_1 < \alpha + \gamma$. The length of this interval is $\alpha$.
- If $k \ge 3$, then $\theta = 180^\circ/k \le 60^\circ \le \alpha$. Any interval of length at least $\theta$ contains a multiple of $\theta$. Since $\gamma > 0$ and $\alpha + \gamma < 180^\circ$, the multiple $\phi_1$ must be in $W$.
- If $k = 2$, then $\theta = 90^\circ$ and $W = \{90^\circ\}$. If the triangle already has a $90^\circ$ angle, Mulan wins. Otherwise, $\beta, \gamma < 90^\circ$, so $\gamma < 90^\circ < 180^\circ - \beta = \alpha + \gamma$. Thus $\phi_1 = 90^\circ$ is always in the interval.

In all cases, Mulan can force a winning state in one step and then force $\theta$ in finitely many steps.

### 2. Necessity of $\theta = 180^\circ/k$
Suppose $\theta \neq 180^\circ/k$ for any integer $k \ge 2$. Then $180^\circ$ is not a multiple of $\theta$, so $W$ contains no supplementary pairs (if $n\theta + m\theta = 180^\circ$, then $(n+m)\theta = 180^\circ$).
Shan-Yu can choose an initial triangle $T$ such that none of its angles are in $W$. For Mulan to guarantee a win, she must be able to force both $T_1$ and $T_2$ to have an angle in $W$ in every step.
Let $T$ have angles $\alpha, \beta, \gamma \notin W$. For any cut $\alpha_1 \in (0, \alpha)$, the conditions for $T_1$ and $T_2$ to have angles in $W$ are:
$(\alpha_1 \in W \text{ or } 180^\circ - \alpha_1 - \beta \in W)$ AND $(\alpha - \alpha_1 \in W \text{ or } 180^\circ - (\alpha - \alpha_1) - \gamma \in W)$.
We analyze the four possible combinations:
1. $\alpha_1 \in W$ and $\alpha - \alpha_1 \in W \implies \alpha = \alpha_1 + (\alpha - \alpha_1) \in W$ (since $W$ is closed under addition as long as the sum $< 180^\circ$).
2. $\alpha_1 \in W$ and $180^\circ - (\alpha - \alpha_1) - \gamma \in W \implies 180^\circ - \alpha - \gamma + \alpha_1 = \beta + \alpha_1 \in W$. Since $\alpha_1 \in W$, this implies $\beta \in W$ unless $\beta + \alpha_1 \ge 180^\circ$, which is impossible.
3. $180^\circ - \alpha_1 - \beta \in W$ and $\alpha - \alpha_1 \in W \implies 180^\circ - \beta - (\alpha - \alpha_1) - \alpha_1 = \gamma + (\alpha - \alpha_1) \in W$. Similarly, this implies $\gamma \in W$.
4. $180^\circ - \alpha_1 - \beta \in W$ and $180^\circ - (\alpha - \alpha_1) - \gamma \in W \implies (180^\circ - \alpha_1 - \beta) + (180^\circ - \alpha + \alpha_1 - \gamma) = 360^\circ - (\alpha + \beta + \gamma) = 180^\circ$. This requires $W$ to contain a supplementary pair, which contradicts our assumption.

Thus, if $T$ has no angle in $W$, Mulan cannot force both $T_1$ and $T_2$ to have an angle in $W$. Shan-Yu can always choose the triangle that does not contain an angle in $W$, preventing Mulan from ever winning.

The real values of $\theta$ for which Mulan can guarantee victory are $\theta = \frac{180^\circ}{k}$ for $k = 2, 3, 4, \dots$.