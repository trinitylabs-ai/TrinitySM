# Problem

IMO 2026 Problem 4. Shan-Yu and Mulan are playing a game. Let theta be an angle with 0 degrees < theta < 180 degrees, known to both players. Initially, Shan-Yu makes a paper triangle T with measurements of his choice. Then they repeatedly perform the following steps. If T has at least one angle measuring exactly theta, the game stops and Mulan wins. Otherwise, Mulan chooses a point P on the perimeter of T, different from its three vertices, and makes a straight cut from P to the opposite vertex of T, splitting it into two triangles. Shan-Yu discards one of the two triangles; the remaining triangle becomes the new T. For which real values of theta can Mulan guarantee victory in finitely many steps, no matter how Shan-Yu plays?

# Proof A

1: To determine for which real values of $\theta \in (0^\circ, 180^\circ)$ Mulan can guarantee victory, we analyze the conditions under which she can force an angle of exactly $\theta$ to appear in the triangle $T$.
2: 
3: Let the angles of the current triangle $T$ be $\alpha, \beta, \gamma$. Suppose Mulan cuts from vertex $C$ to a point $P$ on the opposite side $AB$. Let $\psi = \angle BPC$. The two resulting triangles $T_1$ and $T_2$ have angles:
4: - $T_1: \{\beta, \psi, 180^\circ - \beta - \psi\}$
5: - $T_2: \{\alpha, 180^\circ - \psi, \psi - \alpha\}$
6: Since $P$ is on the segment $AB$ and different from the vertices, $\psi$ can be any value in the open interval $(\alpha, 180^\circ - \beta)$. The length of this interval is $(180^\circ - \beta) - \alpha = \gamma$.
7: 
8: Let $W = \{k\theta \mid k \in \mathbb{Z}^+, k\theta < 180^\circ\}$ be the set of "winning angles". If $T$ contains an angle $\phi \in W$, Mulan can eventually force an angle $\theta$. Specifically, if $T$ has an angle $\phi = k\theta$ with $k > 1$, Mulan can cut from the vertex with angle $\phi$ such that the cut divides $\phi$ into $\theta$ and $(k-1)\theta$. The resulting triangles $T_1$ and $T_2$ will then contain angles $\theta$ and $(k-1)\theta$ respectively. Both are in $W$. No matter which triangle Shan-Yu discards, the new $T$ will have an angle in $W$ with a smaller multiplier. By induction, Mulan will force an angle $\theta$ in finitely many steps.
9: 
10: Now we determine when Mulan can force the game into $W$ if $T$ starts with no angles in $W$. Mulan can do this if she can choose a vertex and a cut angle $\psi$ such that both $T_1$ and $T_2$ have an angle in $W$. Since the original angles $\alpha, \beta, \gamma \notin W$, this requires:
11: $(\psi \in W \text{ or } 180^\circ - \beta - \psi \in W) \text{ AND } (180^\circ - \psi \in W \text{ or } \psi - \alpha \in W)$.
12: 
13: Case 1: $\theta = 180^\circ/n$ for some integer $n \geq 2$.
14: In this case, $W = \{\theta, 2\theta, \dots, (n-1)\theta\}$, and $\phi \in W \iff 180^\circ - \phi \in W$.
15: If $T$ has no angles in $W$, let its angles be $\alpha \leq \beta \leq \gamma$. Mulan cuts from the vertex with the largest angle $\gamma$. The interval for $\psi$ is $(\alpha, 180^\circ - \beta)$, and its length is $\gamma \geq 60^\circ$.
16: If $n=2$, $\theta = 90^\circ$. Since $T$ is not right-angled, $\alpha < 90^\circ$ and $180^\circ - \beta = \alpha + \gamma > 90^\circ$ (since $\beta < 90^\circ$ if no angle is $90^\circ$). Thus $\psi = 90^\circ \in (\alpha, 180^\circ - \beta)$. Then $T_1$ has $\psi = 90^\circ$ and $T_2$ has $180^\circ - \psi = 90^\circ$.
17: If $n \geq 3$, $\theta \leq 60^\circ$. Since the interval $(\alpha, 180^\circ - \beta)$ has length $\gamma \geq 60^\circ \geq \theta$, it must contain a multiple of $\theta$ unless $\alpha$ is a multiple of $\theta$. But $\alpha \notin W$, so there exists $k\theta \in (\alpha, 180^\circ - \beta)$. Picking $\psi = k\theta$ ensures $T_1$ has $\psi \in W$ and $T_2$ has $180^\circ - \psi = (n-k)\theta \in W$.
18: In both cases, Mulan forces the game into $W$ and thus wins.
19: 
20: Case 2: $\theta \neq 180^\circ/n$ for any integer $n \geq 2$.
21: If $\theta \neq 180^\circ/n$, then for any $\psi \in W$, $180^\circ - \psi \notin W$.
22: Suppose $T$ has no angles in $W$. For any cut $\psi$ from vertex $C$, Mulan wins if:
23: $(\psi \in W \lor 180^\circ - \beta - \psi \in W) \land (180^\circ - \psi \in W \lor \psi - \alpha \in W)$.
24: We check the four possible combinations:
25: 1. $\psi \in W$ and $180^\circ - \psi \in W$: Impossible as $\theta \neq 180^\circ/n$.
26: 2. $\psi \in W$ and $\psi - \alpha \in W$: This implies $\alpha = \psi - (\psi - \alpha) \in W - W$. Since $\psi = k\theta$ and $\psi - \alpha = m\theta$, $\alpha = (k-m)\theta \in W$, which contradicts $\alpha \notin W$.
27: 3. $180^\circ - \beta - \psi \in W$ and $180^\circ - \psi \in W$: This implies $\beta = (180^\circ - \psi) - (180^\circ - \beta - \psi) \in W - W$. Since $180^\circ - \psi = m\theta$ and $180^\circ - \beta - \psi = k\theta$, $\beta = (m-k)\theta \in W$, which contradicts $\beta \notin W$.
28: 4. $180^\circ - \beta - \psi \in W$ and $\psi - \alpha \in W$: This implies $180^\circ - \beta - \alpha = (180^\circ - \beta - \psi) + (\psi - \alpha) \in W + W$. Since $180^\circ - \beta - \alpha = \gamma$, this implies $\gamma = m\theta + k\theta \in W$, which contradicts $\gamma \notin W$.
29: Thus, if $T$ has no angles in $W$, Mulan cannot force both resulting triangles to have an angle in $W$. Shan-Yu can always choose the triangle that does not contain an angle in $W$. Since Shan-Yu can choose an initial $T$ with no angles in $W$ (as $W$ is finite), Mulan cannot guarantee victory.
30: 
31: Mulan can guarantee victory if and only if $\theta = 180^\circ/n$ for some integer $n \in \{2, 3, 4, \dots\}$.

# Proof B

1: Let $\theta$ be the given angle with $0^\circ < \theta < 180^\circ$. Let $S = \{k\theta \mid k \in \mathbb{N}, k\theta < 180^\circ\}$. We say a triangle is a winning triangle if at least one of its angles is in $S$. If a triangle has an angle $k\theta \in S$, Mulan can force a win in at most $k$ steps: if $k=1$, she wins immediately; if $k > 1$, she splits the angle $k\theta$ into $\theta$ and $(k-1)\theta$. The two resulting triangles will have angles $\theta$ and $(k-1)\theta$ respectively. Since both are in $S$, Shan-Yu must choose one, and Mulan continues the process until an angle of $\theta$ is produced.
2: 
3: We claim that Mulan can guarantee victory if and only if $\theta = \frac{180^\circ}{n}$ for some integer $n \ge 2$.
4: 
5: First, suppose $\theta = \frac{180^\circ}{n}$ for some integer $n \ge 2$. Let the angles of the current triangle $T$ be $a, b, c$. If any angle is in $S$, Mulan wins as shown above. Suppose $a, b, c \notin S$. Mulan can win in one move if she can split one angle, say $a$, into $\alpha_1$ and $\alpha_2$ such that both resulting triangles $T_1 = (\alpha_1, b, 180^\circ - \alpha_1 - b)$ and $T_2 = (\alpha_2, c, 180^\circ - \alpha_2 - c)$ have an angle in $S$.
6: Mulan attempts to make $180^\circ - \alpha_1 - b = k_1\theta$ and $180^\circ - \alpha_2 - c = k_2\theta$ for some $k_1, k_2 \in \{1, \dots, n-1\}$. This requires:
7: $\alpha_1 = 180^\circ - b - k_1\theta$ and $\alpha_2 = 180^\circ - c - k_2\theta$.
8: For the cut to be valid, we need $\alpha_1 + \alpha_2 = a$, which implies:
9: $360^\circ - (b + c) - (k_1 + k_2)\theta = a \implies 360^\circ - (180^\circ - a) - (k_1 + k_2)\theta = a \implies (k_1 + k_2)\theta = 180^\circ$.
10: Since $\theta = 180^\circ/n$, this is satisfied if $k_1 + k_2 = n$. We also need $\alpha_1 > 0$ and $\alpha_2 > 0$:
11: $\alpha_1 > 0 \iff k_1\theta < 180^\circ - b \iff k_1 < n - \frac{b}{\theta}$
12: $\alpha_2 > 0 \iff k_2\theta < 180^\circ - c \iff k_2 < n - \frac{c}{\theta} \iff n - k_1 < n - \frac{c}{\theta} \iff k_1 > \frac{c}{\theta}$
13: Thus, Mulan wins in one move if there exists an integer $k_1$ in the interval $(\frac{c}{\theta}, n - \frac{b}{\theta})$. The length of this interval is $n - \frac{b+c}{\theta} = n - \frac{180^\circ - a}{\theta} = \frac{a}{\theta}$.
14: If $a > \theta$, the length is greater than 1, so such an integer $k_1$ always exists. Since $a+b+c=180^\circ=n\theta$, at least one angle must be $\ge \theta$. If any angle is exactly $\theta$, Mulan wins. If all angles are $\neq \theta$, then at least one angle must be $>\theta$ (unless $n=2$ and $a, b, c < 90^\circ$, in which case $a/\theta < 1$, but Mulan can still pick $k_1=1$ since $c/90 < 1 < 2 - b/90$ is equivalent to $c < 90$ and $b < 90$, which is true). Thus, Mulan can always force a win in at most one move.
15: 
16: Conversely, suppose $\theta \neq \frac{180^\circ}{n}$ for any integer $n \ge 2$. We show that if $T$ has no angle in $S$, then for any cut Mulan makes, Shan-Yu can choose a resulting triangle that also has no angle in $S$.
17: Suppose Mulan cuts $\alpha$ into $\alpha_1, \alpha_2$. $T_1 = (\alpha_1, \beta, 180^\circ - \alpha_1 - \beta)$ and $T_2 = (\alpha_2, \gamma, 180^\circ - \alpha_2 - \gamma)$. For both $T_1$ and $T_2$ to have angles in $S$, given $\beta, \gamma \notin S$, we must have:
18: $(\alpha_1 \in S \text{ or } 180^\circ - \alpha_1 - \beta \in S)$ AND $(\alpha_2 \in S \text{ or } 180^\circ - \alpha_2 - \gamma \in S)$.
19: We check the four possibilities:
20: 1. $\alpha_1 = n_1\theta$ and $\alpha_2 = n_2\theta \implies \alpha = (n_1+n_2)\theta \in S$.
21: 2. $\alpha_1 = n_1\theta$ and $180^\circ - \alpha_2 - \gamma = n_2\theta \implies \alpha_2 = 180^\circ - \gamma - n_2\theta \implies \alpha = n_1\theta + 180^\circ - \gamma - n_2\theta \implies \alpha + \gamma = 180^\circ + (n_1-n_2)\theta \implies 180^\circ - \beta = 180^\circ + (n_1-n_2)\theta \implies \beta = (n_2-n_1)\theta \in S$.
22: 3. $180^\circ - \alpha_1 - \beta = n_1\theta$ and $\alpha_2 = n_2\theta \implies \alpha_1 = 180^\circ - \beta - n_1\theta \implies \alpha = 180^\circ - \beta - n_1\theta + n_2\theta \implies \alpha + \beta = 180^\circ + (n_2-n_1)\theta \implies 180^\circ - \gamma = 180^\circ + (n_2-n_1)\theta \implies \gamma = (n_1-n_2)\theta \in S$.
23: 4. $180^\circ - \alpha_1 - \beta = n_1\theta$ and $180^\circ - \alpha_2 - \gamma = n_2\theta \implies \alpha = 360^\circ - (\beta + \gamma) - (n_1+n_2)\theta = 180^\circ + \alpha - (n_1+n_2)\theta \implies (n_1+n_2)\theta = 180^\circ$.
24: Since $T$ has no angle in $S$ and $\theta \neq 180^\circ/n$, none of these are possible. Thus, at least one of $T_1, T_2$ must have no angle in $S$. Shan-Yu can start with $T = (60^\circ, 60^\circ, 60^\circ)$. Since $\theta \neq 180^\circ/n$, $60^\circ$ cannot be a multiple of $\theta$ (otherwise $180^\circ = 3 \cdot 60^\circ$ would be a multiple of $\theta$). Thus $T$ has no angle in $S$, and Shan-Yu can avoid $\theta$ indefinitely.
25: 
26: Mulan can guarantee victory if and only if $\theta = \frac{180^\circ}{n}$ for some integer $n \ge 2$.
