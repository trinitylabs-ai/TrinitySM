# Problem

IMO 2026 Problem 4. Shan-Yu and Mulan are playing a game. Let theta be an angle with 0 degrees < theta < 180 degrees, known to both players. Initially, Shan-Yu makes a paper triangle T with measurements of his choice. Then they repeatedly perform the following steps. If T has at least one angle measuring exactly theta, the game stops and Mulan wins. Otherwise, Mulan chooses a point P on the perimeter of T, different from its three vertices, and makes a straight cut from P to the opposite vertex of T, splitting it into two triangles. Shan-Yu discards one of the two triangles; the remaining triangle becomes the new T. For which real values of theta can Mulan guarantee victory in finitely many steps, no matter how Shan-Yu plays?

# Proof A

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

# Proof B

1: We seek to determine all $\theta \in (0^\circ, 180^\circ)$ such that Mulan can guarantee victory in finitely many steps. Let $W = \{n\theta \mid n \in \mathbb{N}, n\theta < 180^\circ\}$ be the set of angles that are positive integer multiples of $\theta$.
2: 
3: First, we show that if a triangle $T$ has an angle $\phi \in W$, Mulan can force a win. If $\phi = \theta$, Mulan wins immediately. If $\phi = n\theta$ for $n > 1$, Mulan can cut the vertex with angle $\phi$ into two angles $\theta$ and $(n-1)\theta$. The resulting triangles $T_1$ and $T_2$ then have angles $\theta$ and $(n-1)\theta$ respectively. Regardless of which triangle Shan-Yu keeps, the new triangle possesses an angle in $W$ with a strictly smaller coefficient of $\theta$. Thus, the game must terminate in at most $n$ steps.
4: 
5: Next, we show that if $\theta = 180^\circ/k$ for some integer $k \ge 2$, Mulan can always force a win. Let the angles of $T$ be $A, B, C$. If any angle is in $W$, Mulan wins as shown above. Suppose no angle is in $W$. Mulan can win in one step if she can choose a vertex (say $A$) and a cut $\alpha \in (0, A)$ such that both resulting triangles $T_1$ (angles $\alpha, B, 180^\circ - B - \alpha$) and $T_2$ (angles $A-\alpha, C, B+\alpha$) have an angle in $W$.
6: If Mulan picks $\alpha$ such that $B+\alpha = n\theta$ for some $n \in \{1, \dots, k-1\}$, then $T_2$ has angle $n\theta \in W$ and $T_1$ has angle $180^\circ - (B+\alpha) = 180^\circ - n\theta = (k-n)\theta \in W$. This is possible if there exists $n$ such that $B < n\theta < B+A$.
7: The length of the interval $(B, B+A)$ is $A$. If $A > \theta$, the interval must contain a multiple of $\theta$.
8: If $A, B, C \le \theta$, then $A+B+C \le 3\theta$. Since $A+B+C = 180^\circ = k\theta$, we have $k\theta \le 3\theta$, so $k \le 3$.
9: If $k=3$, then $A=B=C=\theta$, which contradicts the assumption that no angle is in $W$.
10: If $k=2$, then $\theta = 90^\circ$. Since no angle is in $W$, $A, B, C < 90^\circ$. Then $B < 90^\circ$ and $B+A = 180^\circ - C > 90^\circ$, so $n=1$ satisfies $B < 1\cdot 90^\circ < B+A$.
11: Thus, for any $k \ge 2$, Mulan can force the game into $W$ in at most one step, and then win in finitely many steps.
12: 
13: Finally, we show that if $\theta \neq 180^\circ/k$ for any $k \in \mathbb{N}$, Shan-Yu can prevent Mulan from winning. Shan-Yu chooses an initial triangle $T$ such that none of its angles $A, B, C$ are in $W$. Since $W$ is a finite set, such a triangle always exists.
14: Suppose $T$ has no angle in $W$. Mulan chooses a vertex (say $A$) and a cut $\alpha \in (0, A)$. The resulting triangles are $T_1$ (angles $\alpha, B, 180^\circ - B - \alpha$) and $T_2$ (angles $A-\alpha, C, B+\alpha$).
15: Mulan wins if she can force both $T_1$ and $T_2$ to have an angle in $W$. Since $B, C \notin W$, $T_1$ has an angle in $W$ if and only if $\alpha \in W$ or $180^\circ - B - \alpha \in W$. Similarly, $T_2$ has an angle in $W$ if and only if $A-\alpha \in W$ or $B+\alpha \in W$.
16: We check all possible pairs of conditions for both $T_1$ and $T_2$ to have an angle in $W$:
17: 1. $\alpha = n\theta$ and $A-\alpha = m\theta \implies A = (n+m)\theta \in W$.
18: 2. $\alpha = n\theta$ and $B+\alpha = m\theta \implies B = (m-n)\theta \in W$.
19: 3. $180^\circ - B - \alpha = n\theta$ and $A-\alpha = m\theta \implies 180^\circ - B - A = (n-m)\theta \implies C = (n-m)\theta \in W$.
20: 4. $180^\circ - B - \alpha = n\theta$ and $B+\alpha = m\theta \implies 180^\circ = (n+m)\theta$.
21: Since $A, B, C \notin W$ and $180^\circ$ is not a multiple of $\theta$ (because $\theta \neq 180^\circ/k$), none of these conditions can be satisfied. Thus, for any cut Mulan makes, at least one of the resulting triangles must have no angle in $W$. Shan-Yu discards the other triangle, maintaining the "safe state" where $T$ has no angle in $W$. Consequently, Mulan can never produce a triangle with an angle $\theta$.
22: 
23: The values of $\theta$ for which Mulan can guarantee victory are $\theta = \frac{180^\circ}{k}$ for $k \in \{2, 3, 4, \dots\}$.
