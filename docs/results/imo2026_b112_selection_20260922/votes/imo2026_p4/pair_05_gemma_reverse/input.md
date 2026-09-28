# Problem

IMO 2026 Problem 4. Shan-Yu and Mulan are playing a game. Let theta be an angle with 0 degrees < theta < 180 degrees, known to both players. Initially, Shan-Yu makes a paper triangle T with measurements of his choice. Then they repeatedly perform the following steps. If T has at least one angle measuring exactly theta, the game stops and Mulan wins. Otherwise, Mulan chooses a point P on the perimeter of T, different from its three vertices, and makes a straight cut from P to the opposite vertex of T, splitting it into two triangles. Shan-Yu discards one of the two triangles; the remaining triangle becomes the new T. For which real values of theta can Mulan guarantee victory in finitely many steps, no matter how Shan-Yu plays?

# Proof A

1: To determine for which real values of $\theta \in (0^\circ, 180^\circ)$ Mulan can guarantee victory, we analyze the conditions under which she can force an angle of exactly $\theta$ to appear in the triangle $T$.
2: 
3: Let the angles of the current triangle $T$ be $\alpha, \beta, \gamma$. Suppose Mulan cuts from vertex $B$ to a point $P$ on the opposite side $AC$. Let $\psi = \angle BPA$. The two resulting triangles $T_1$ and $T_2$ have angles:
4: - $T_1: \{\alpha, \psi, 180^\circ - \alpha - \psi\}$
5: - $T_2: \{\gamma, 180^\circ - \psi, \psi - \gamma\}$
6: Since $P$ is on the segment $AC$ and different from the vertices, $\psi$ can be any value in the open interval $(\gamma, 180^\circ - \alpha)$. Since $\alpha + \beta + \gamma = 180^\circ$, this interval is $(\gamma, \beta + \gamma)$.
7: 
8: Let $W = \{k\theta \mid k \in \mathbb{Z}^+, k\theta < 180^\circ\}$ be the set of "winning angles". If $T$ contains an angle $\phi \in W$, Mulan can eventually force an angle $\theta$. Specifically, if $T$ has an angle $\phi = k\theta$ with $k > 1$, Mulan can cut from the vertex with angle $\phi$ such that the cut divides $\phi$ into $\theta$ and $(k-1)\theta$. The resulting triangles $T_1$ and $T_2$ will then contain angles $\theta$ and $(k-1)\theta$ respectively. Both are in $W$. No matter which triangle Shan-Yu discards, the new $T$ will have an angle in $W$ with a smaller multiplier. By induction, Mulan will force an angle $\theta$ in finitely many steps.
9: 
10: Now we determine when Mulan can force the game into $W$ if $T$ starts with no angles in $W$. Mulan can do this if she can choose a vertex and a cut angle $\psi$ such that both $T_1$ and $T_2$ have an angle in $W$. Since the original angles $\alpha, \beta, \gamma \notin W$, this requires:
11: $(\psi \in W \text{ or } 180^\circ - \alpha - \psi \in W) \text{ AND } (180^\circ - \psi \in W \text{ or } \psi - \gamma \in W)$.
12: 
13: Case 1: $\theta = 180^\circ/n$ for some integer $n \geq 2$.
14: In this case, $W = \{\theta, 2\theta, \dots, (n-1)\theta\}$, and $\phi \in W \iff 180^\circ - \phi \in W$.
15: If $T$ has no angles in $W$, let its angles be $\alpha \leq \beta \leq \gamma$. Mulan cuts from the vertex with the smallest angle $\alpha$. The interval for $\psi$ is $(\beta, \gamma + \beta)$. The length of this interval is $\gamma \geq 60^\circ$.
16: If $n=2$, $\theta = 90^\circ$. Since $T$ is not right-angled, $\beta < 90^\circ$ and $\gamma + \beta = 180^\circ - \alpha > 90^\circ$. Thus $\psi = 90^\circ \in (\beta, \gamma + \beta)$. Then $T_1$ has $\psi = 90^\circ$ and $T_2$ has $180^\circ - \psi = 90^\circ$.
17: If $n \geq 3$, $\theta \leq 60^\circ$. Since the interval $(\beta, \gamma + \beta)$ has length $\gamma \geq 60^\circ \geq \theta$, it must contain a multiple of $\theta$ unless $\beta$ is a multiple of $\theta$. But $\beta \notin W$, so there exists $k\theta \in (\beta, \gamma + \beta)$. Picking $\psi = k\theta$ ensures $T_1$ has $\psi \in W$ and $T_2$ has $180^\circ - \psi = (n-k)\theta \in W$.
18: In both cases, Mulan forces the game into $W$ and thus wins.
19: 
20: Case 2: $\theta \neq 180^\circ/n$ for any integer $n \geq 2$.
21: If $\theta \neq 180^\circ/n$, then for any $\psi \in W$, $180^\circ - \psi \notin W$.
22: Suppose $T$ has no angles in $W$. For any cut $\psi$, Mulan wins if:
23: $(\psi \in W \lor 180^\circ - \alpha - \psi \in W) \land (180^\circ - \psi \in W \lor \psi - \gamma \in W)$.
24: We check the four possible combinations:
25: 1. $\psi \in W$ and $180^\circ - \psi \in W$: Impossible as $\theta \neq 180^\circ/n$.
26: 2. $\psi \in W$ and $\psi - \gamma \in W$: This implies $\gamma = \psi - (\psi - \gamma) \in W$, which contradicts $\gamma \notin W$.
27: 3. $180^\circ - \alpha - \psi \in W$ and $180^\circ - \psi \in W$: This implies $\alpha = (180^\circ - \psi) - (180^\circ - \alpha - \psi) \in W$, which contradicts $\alpha \notin W$.
28: 4. $180^\circ - \alpha - \psi \in W$ and $\psi - \gamma \in W$: This implies $180^\circ - \alpha - \gamma = (180^\circ - \alpha - \psi) + (\psi - \gamma) \in W$. Since $180^\circ - \alpha - \gamma = \beta$, this contradicts $\beta \notin W$.
29: Thus, if $T$ has no angles in $W$, Mulan cannot force both resulting triangles to have an angle in $W$. Shan-Yu can always choose the triangle that does not contain an angle in $W$. Since Shan-Yu can choose an initial $T$ with no angles in $W$ (as $W$ is finite), Mulan cannot guarantee victory.
30: 
31: Mulan can guarantee victory if and only if $\theta = 180^\circ/n$ for some integer $n \in \{2, 3, 4, \dots\}$.

# Proof B

1: To determine the real values of $\theta \in (0, 180^\circ)$ for which Mulan can guarantee victory in finitely many steps, we analyze the game's dynamics on the space of triangle angles $(\alpha, \beta, \gamma)$ where $\alpha + \beta + \gamma = 180^\circ$.
2: 
3: First, we show that if $\theta$ is not a rational multiple of $180^\circ$, Shan-Yu can avoid $\theta$ indefinitely. Let $S = \{ n\theta + m 180^\circ \mid n, m \in \mathbb{Z} \}$. Since $\theta/180^\circ \notin \mathbb{Q}$, $S$ is a dense subgroup of $\mathbb{R}$ modulo $180^\circ$. Shan-Yu chooses an initial triangle $T_0$ such that none of its angles $\alpha, \beta, \gamma$ are in $S$.
4: Suppose the current triangle $T = (\alpha, \beta, \gamma)$ has no angles in $S$. Mulan splits $\alpha$ into $\alpha_1, \alpha_2$ ($\alpha_1 + \alpha_2 = \alpha$). The resulting triangles are $T_1 = (\alpha_1, \beta, 180^\circ - \beta - \alpha_1)$ and $T_2 = (\alpha_2, \gamma, 180^\circ - \gamma - \alpha_2)$.
5: If Mulan chooses $\alpha_1 \in S$, then $T_1$ has an angle in $S$. However, $\alpha_2 = \alpha - \alpha_1 \notin S$ (since $\alpha \notin S$), $\gamma \notin S$, and $180^\circ - \gamma - \alpha_2 = \beta + \alpha_1 \notin S$ (since $\beta \notin S$ and $\alpha_1 \in S$). Thus, $T_2$ has no angles in $S$.
6: If Mulan chooses $\alpha_1 \notin S$, then $T_1$ has no angle in $S$ unless $180^\circ - \beta - \alpha_1 \in S$. If $180^\circ - \beta - \alpha_1 = s \in S$, then $180^\circ - \gamma - \alpha_2 = \beta + \alpha_1 = 180^\circ - s \in S$. In this case, both $T_1$ and $T_2$ have angles in $S$. However, for Mulan to win, a triangle must have an angle exactly $\theta$. If $T_1$ has an angle $\theta$, then $\alpha_1 = \theta$ or $180^\circ - \beta - \alpha_1 = \theta$. In the first case, $T_2$ has angles $(\alpha - \theta, \gamma, \beta + \theta)$, none of which are $\theta$ because $\alpha, \gamma, \beta \notin S$. In the second case, $T_2$ has angles $(\beta + \theta - \gamma, \gamma, 180^\circ - \theta)$. None of these are $\theta$ because $\beta + \theta - \gamma = \theta \implies \beta = \gamma$ (which Shan-Yu can avoid by choosing $T_0$ with distinct angles), $\gamma = \theta \in S$, and $180^\circ - \theta = \theta \implies \theta = 90^\circ \in \mathbb{Q} \cdot 180^\circ$.
7: Thus, if $\theta/180^\circ \notin \mathbb{Q}$, Shan-Yu can avoid $\theta$ indefinitely.
8: 
9: Next, we consider $\theta \in \mathbb{Q} \cdot 180^\circ$. Let $\theta = \frac{p}{q} 180^\circ$.
10: If $\theta \ge 120^\circ$, Shan-Yu can guarantee a draw by choosing $T_0$ to be an equilateral triangle $(60^\circ, 60^\circ, 60^\circ)$. Any cut of an angle $\alpha = 60^\circ$ into $\alpha_1, \alpha_2$ results in triangles with angles $(\alpha_1, 60^\circ, 120^\circ - \alpha_1)$ and $(\alpha_2, 60^\circ, 120^\circ - \alpha_2)$. Since $0 < \alpha_1 < 60^\circ$, the maximum angle in either triangle is $120^\circ - \alpha_1 < 120^\circ$. Thus, no angle can ever reach $\theta \ge 120^\circ$. Even if Mulan creates a triangle with an angle larger than $60^\circ$, say $T = (10^\circ, 60^\circ, 110^\circ)$, any cut that creates an angle $\theta \ge 120^\circ$ in $T_1$ will result in $T_2$ returning to a state where all angles are $< 120^\circ$ (e.g., cutting $110^\circ$ to get $120^\circ$ in $T_1$ forces $T_2$ to be $(60^\circ, 60^\circ, 60^\circ)$).
11: 
12: If $\theta < 120^\circ$ and $\theta \in \mathbb{Q} \cdot 180^\circ$, Mulan can guarantee victory. Let $G = \{ n\theta + m 180^\circ \mid n, m \in \mathbb{Z} \}$. Since $\theta/180^\circ \in \mathbb{Q}$, $G$ is a discrete subgroup $G = \{ k\delta \mid k \in \mathbb{Z} \}$ where $\delta = \gcd(\theta, 180^\circ)$.
13: Mulan first forces the triangle to have at least one angle in $G$. She picks a vertex $\alpha$ and cuts it such that $T_1$ has an angle $\theta$ (possible if $\gamma < \theta$ by picking $\alpha_1 = 180^\circ - \beta - \theta$). If Shan-Yu keeps $T_1$, Mulan wins. If he keeps $T_2$, $T_2$ has angles $(\theta - \gamma, \gamma, 180^\circ - \theta)$. The angle $180^\circ - \theta$ is in $G$.
14: Once $T$ has one angle $\gamma \in G$, Mulan again cuts a vertex to create an angle $\theta$ in $T_1$. If Shan-Yu keeps $T_2$, Mulan can choose the cut such that the resulting triangle $T_2$ has all angles in $G$. For example, if $T = (\alpha, \beta, \gamma)$ with $\gamma \in G$, Mulan cuts $\alpha$ into $\alpha_1 = 180^\circ - \beta - \theta$ and $\alpha_2 = \theta - \gamma$. Then $T_2 = (\theta - \gamma, \gamma, 180^\circ - \theta)$. Since $\gamma, \theta, 180^\circ \in G$, all angles of $T_2$ are now in $G$.
15: The state of the game is now a triple of integers $(n_1, n_2, n_3)$ such that $n_1 + n_2 + n_3 = N = 180^\circ/\delta$, where each angle is $n_i \delta$. Mulan wins if any $n_i = m = \theta/\delta$.
16: In the finite state space of triples, Mulan can always choose a cut $k\delta$ to either create an angle $m\delta$ in $T_1$ or force the state to a different triple in $G$. Because the state space is finite and Mulan can choose from multiple values of $k$ to avoid cycles, she can force the state to $(m, n_2, n_3)$. Specifically, if $\theta < 120^\circ$, the winning state is reachable from any state in $G$ because Mulan can always force the maximum angle to change until it equals $m\delta$.
17: 
18: Thus, Mulan can guarantee victory if and only if $\theta$ is a rational multiple of $180^\circ$ and $\theta < 120^\circ$.
19: 
20: The real values of $\theta$ are $\theta \in \{ \frac{p}{q} 180^\circ \mid p, q \in \mathbb{Z}^+, \frac{p}{q} < \frac{2}{3} \}$.
