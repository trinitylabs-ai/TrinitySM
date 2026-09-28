# Problem

IMO 2026 Problem 4. Shan-Yu and Mulan are playing a game. Let theta be an angle with 0 degrees < theta < 180 degrees, known to both players. Initially, Shan-Yu makes a paper triangle T with measurements of his choice. Then they repeatedly perform the following steps. If T has at least one angle measuring exactly theta, the game stops and Mulan wins. Otherwise, Mulan chooses a point P on the perimeter of T, different from its three vertices, and makes a straight cut from P to the opposite vertex of T, splitting it into two triangles. Shan-Yu discards one of the two triangles; the remaining triangle becomes the new T. For which real values of theta can Mulan guarantee victory in finitely many steps, no matter how Shan-Yu plays?

# Proof A

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
