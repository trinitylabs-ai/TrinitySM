Consider a positive integer $n$. We define $f(n)$ as the number of pairs of paths on an $n \times n$ grid that:

 (1) Both paths start at $(0, 0)$ (bottom left corner) and end at $(n, n)$ (top right corner).

 (2) Both paths allow only right or up movements (one unit each).

 (3) The $y$ coordinate of the first path never exceeds the y coordinate of the second path at any timestep.

 For example, when $n = 2$, consider the following pair of paths:

 The first path: $(0,0) \rightarrow (1,0) \rightarrow (1,1) \rightarrow (2,1) \rightarrow (2,2)$
 The second path: $(0,0) \rightarrow (1,0) \rightarrow (2,0) \rightarrow (2,1) \rightarrow(2,2)$
 The example is invalid because after 2 steps, the y coordinate of the first path (1) is larger than the y coordinate of the second path (0).

 However, the following example is valid,

 The first path: $(0,0) \rightarrow (1,0) \rightarrow (2,0) \rightarrow (2,1) \rightarrow (2,2)$
 The second path: $(0,0) \rightarrow (1,0) \rightarrow (1,1) \rightarrow (2,1) \rightarrow (2,2)$

 since the y coordinate of the first path is never larger than the second path. Find $f(10)$.
