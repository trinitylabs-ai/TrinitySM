# Problem

Determine all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that, for all $x, y \in \mathbb{Z}$, we have \[ f(2x)+2f(y)=f(f(x+y)).\]

# Proof A

1: To determine all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that for all $x, y \in \mathbb{Z}$,
2: \[ f(2x) + 2f(y) = f(f(x+y)), \]
3: we proceed as follows.
4: 
5: **1. Deriving a relationship for $f(f(n))$ and $f(2n)$**
6: Let $f(0) = b$. Setting $x=0$ in the original equation gives:
7: \[ f(0) + 2f(y) = f(f(y)) \implies f(f(y)) = 2f(y) + b. \tag{1} \]
8: Setting $y=0$ in the original equation gives:
9: \[ f(2x) + 2f(0) = f(f(x)) \implies f(2x) + 2b = f(f(x)). \tag{2} \]
10: Substituting the expression for $f(f(x))$ from (1) into (2), we have:
11: \[ f(2x) + 2b = 2f(x) + b \implies f(2x) = 2f(x) - b. \tag{3} \]
12: 
13: **2. Reducing to Cauchy's functional equation**
14: We now substitute (1) and (3) back into the original equation $f(2x) + 2f(y) = f(f(x+y))$:
15: \[ (2f(x) - b) + 2f(y) = 2f(x+y) + b. \]
16: Simplifying this expression:
17: \[ 2f(x) + 2f(y) - 2b = 2f(x+y) \implies f(x) + f(y) - b = f(x+y). \]
18: To solve this, we define a new function $g: \mathbb{Z} \rightarrow \mathbb{Z}$ by $g(n) = f(n) - b$. Substituting $f(n) = g(n) + b$ into the equation above:
19: \[ (g(x) + b) + (g(y) + b) - b = g(x+y) + b \implies g(x) + g(y) = g(x+y). \]
20: This is Cauchy's functional equation on the integers. For any such function $g: \mathbb{Z} \rightarrow \mathbb{Z}$, the solution is $g(n) = an$ for some constant $a = g(1) \in \mathbb{Z}$. Consequently, the general form of $f$ is:
21: \[ f(n) = an + b. \]
22: 
23: **3. Determining the constants $a$ and $b$**
24: We substitute $f(n) = an + b$ into the original equation to find the valid values of $a$ and $b$:
25: LHS: $f(2x) + 2f(y) = (a(2x) + b) + 2(ay + b) = 2ax + 2ay + 3b$.
26: RHS: $f(f(x+y)) = f(a(x+y) + b) = a(a(x+y) + b) + b = a^2(x+y) + ab + b$.
27: For the equation to hold for all $x, y \in \mathbb{Z}$, we must have:
28: \[ 2a(x+y) + 3b = a^2(x+y) + (a+1)b. \]
29: Comparing the coefficients of $(x+y)$ and the constant terms:
30: 1. $2a = a^2 \implies a(a-2) = 0 \implies a = 0$ or $a = 2$.
31: 2. $3b = (a+1)b \implies b(a-2) = 0$.
32: 
33: We analyze these cases:
34: - If $a = 0$, then the second condition becomes $b(0-2) = 0$, which implies $b = 0$. This gives the solution $f(n) = 0$.
35: - If $a = 2$, then the second condition becomes $b(2-2) = 0$, which is $0 = 0$. This is true for any $b \in \mathbb{Z}$. This gives the solution $f(n) = 2n + b$.
36: 
37: **4. Verification**
38: - For $f(n) = 0$: $f(2x) + 2f(y) = 0 + 0 = 0$ and $f(f(x+y)) = f(0) = 0$. This is a solution.
39: - For $f(n) = 2n + b$: $f(2x) + 2f(y) = (4x + b) + 2(2y + b) = 4x + 4y + 3b$.
40:   $f(f(x+y)) = f(2(x+y) + b) = 2(2x + 2y + b) + b = 4x + 4y + 3b$.
41:   This is a solution for any $b \in \mathbb{Z}$.
42: 
43: The functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ satisfying the given equation are $f(n) = 0$ and $f(n) = 2n + b$ for any $b \in \mathbb{Z}$.
44: 
45: \(\square\)

# Proof B

1: To determine all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that for all $x, y \in \mathbb{Z}$,
2: \[ f(2x) + 2f(y) = f(f(x+y)), \]
3: we proceed as follows:
4: 
5: **1. Deriving Functional Relations**
6: Let $f(0) = b$. We begin by substituting specific values for $x$ and $y$ to find relations between $f(x)$, $f(2x)$, and $f(f(x))$.
7: Substituting $x = 0$ into the original equation:
8: \[ f(0) + 2f(y) = f(f(y)) \implies b + 2f(y) = f(f(y)) \quad \text{for all } y \in \mathbb{Z}. \quad (1) \]
9: Substituting $y = 0$ into the original equation:
10: \[ f(2x) + 2f(0) = f(f(x)) \implies f(2x) + 2b = f(f(x)) \quad \text{for all } x \in \mathbb{Z}. \quad (2) \]
11: By substituting the expression for $f(f(x))$ from equation (1) into equation (2), we obtain:
12: \[ f(2x) + 2b = 2f(x) + b \implies f(2x) = 2f(x) - b \quad \text{for all } x \in \mathbb{Z}. \quad (3) \]
13: 
14: **2. Reducing to Cauchy's Functional Equation**
15: We now substitute the relations (1) and (3) back into the original equation:
16: \[ f(2x) + 2f(y) = f(f(x+y)) \]
17: \[ (2f(x) - b) + 2f(y) = 2f(x+y) + b \]
18: Rearranging the terms:
19: \[ 2f(x) + 2f(y) - 2b = 2f(x+y) \implies f(x+y) = f(x) + f(y) - b. \]
20: To solve this, we define a new function $g: \mathbb{Z} \rightarrow \mathbb{Z}$ by $g(x) = f(x) - b$. Substituting $f(x) = g(x) + b$ into the equation above:
21: \[ g(x+y) + b = (g(x) + b) + (g(y) + b) - b \]
22: \[ g(x+y) = g(x) + g(y). \]
23: This is Cauchy's functional equation on the integers. The general solution for $g: \mathbb{Z} \rightarrow \mathbb{Z}$ is $g(x) = ax$ for some constant $a \in \mathbb{Z}$. Therefore, the general form of $f$ is:
24: \[ f(x) = ax + b. \]
25: 
26: **3. Determining Valid Parameters $a$ and $b$**
27: We substitute $f(x) = ax + b$ into the original equation to find the constraints on $a$ and $b$:
28: \[ f(2x) + 2f(y) = (a(2x) + b) + 2(ay + b) = 2ax + 2ay + 3b. \]
29: \[ f(f(x+y)) = f(a(x+y) + b) = a(a(x+y) + b) + b = a^2x + a^2y + ab + b. \]
30: For the equality $2ax + 2ay + 3b = a^2x + a^2y + ab + b$ to hold for all $x, y \in \mathbb{Z}$, the coefficients of $x$ and $y$ must be equal, and the constant terms must be equal:
31: 1.  $2a = a^2 \implies a^2 - 2a = 0 \implies a(a-2) = 0$. Thus, $a = 0$ or $a = 2$.
32: 2.  $3b = ab + b \implies 2b = ab$.
33: 
34: **Case 1: $a = 0$.**
35: Substituting $a=0$ into $2b = ab$ gives $2b = 0$, which implies $b = 0$.
36: This yields the solution $f(n) = 0$.
37: 
38: **Case 2: $a = 2$.**
39: Substituting $a=2$ into $2b = ab$ gives $2b = 2b$, which is true for any integer $b$.
40: This yields the solution $f(n) = 2n + b$ for any $b \in \mathbb{Z}$.
41: 
42: **4. Verification**
43: - For $f(n) = 0$: $f(2x) + 2f(y) = 0 + 0 = 0$ and $f(f(x+y)) = f(0) = 0$. This is a solution.
44: - For $f(n) = 2n + b$: $f(2x) + 2f(y) = (4x + b) + 2(2y + b) = 4x + 4y + 3b$ and $f(f(x+y)) = f(2(x+y) + b) = 2(2x + 2y + b) + b = 4x + 4y + 3b$. This is a solution for any $b \in \mathbb{Z}$.
45: 
46: The functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ that satisfy the equation are $f(n) = 0$ and $f(n) = 2n + b$ for any $b \in \mathbb{Z}$.
47: 
48: \(\square\)
