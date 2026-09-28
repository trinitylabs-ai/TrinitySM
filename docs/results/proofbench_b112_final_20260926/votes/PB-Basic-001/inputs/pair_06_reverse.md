# Problem

Determine all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that, for all $x, y \in \mathbb{Z}$, we have \[ f(2x)+2f(y)=f(f(x+y)).\]

# Proof A

1: To find all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that for all $x, y \in \mathbb{Z}$,
2: \[ f(2x) + 2f(y) = f(f(x+y)), \]
3: we proceed as follows:
4: 
5: **1. Deriving a relation for $f(f(n))$**
6: Let $f(0) = c$ for some constant $c \in \mathbb{Z}$. By substituting $x = 0$ into the original equation, we get:
7: \[ f(0) + 2f(y) = f(f(y)) \implies f(f(y)) = 2f(y) + c. \]
8: This identity holds for all $y \in \mathbb{Z}$.
9: 
10: **2. Simplifying the original equation**
11: We can now substitute the identity $f(f(z)) = 2f(z) + c$ (where $z = x+y$) back into the original equation:
12: \[ f(2x) + 2f(y) = 2f(x+y) + c. \]
13: To find a relationship for $f(2x)$, we set $y = 0$ in this simplified equation:
14: \[ f(2x) + 2f(0) = 2f(x) + c \implies f(2x) + 2c = 2f(x) + c \implies f(2x) = 2f(x) - c. \]
15: 
16: **3. Reducing to Cauchy's Functional Equation**
17: Substitute the expression for $f(2x)$ back into the equation $f(2x) + 2f(y) = 2f(x+y) + c$:
18: \[ (2f(x) - c) + 2f(y) = 2f(x+y) + c \implies 2f(x) + 2f(y) - 2c = 2f(x+y). \]
19: Dividing by 2, we obtain:
20: \[ f(x+y) = f(x) + f(y) - c. \]
21: Let $g(x) = f(x) - c$. Then $f(x) = g(x) + c$. Substituting this into the equation above:
22: \[ g(x+y) + c = (g(x) + c) + (g(y) + c) - c \implies g(x+y) = g(x) + g(y). \]
23: This is Cauchy's functional equation. Since $g: \mathbb{Z} \rightarrow \mathbb{Z}$, the only solutions are of the form $g(x) = ax$ for some constant $a \in \mathbb{Z}$. Thus, the general form of $f$ is:
24: \[ f(x) = ax + c. \]
25: 
26: **4. Solving for $a$ and $c$**
27: We substitute $f(x) = ax + c$ back into the original equation $f(2x) + 2f(y) = f(f(x+y))$ to determine the possible values of $a$ and $c$:
28: LHS: $f(2x) + 2f(y) = (a(2x) + c) + 2(ay + c) = 2ax + 2ay + 3c$.
29: RHS: $f(f(x+y)) = f(a(x+y) + c) = a(a(x+y) + c) + c = a^2x + a^2y + ac + c$.
30: Equating the two sides:
31: \[ 2a(x+y) + 3c = a^2(x+y) + (a+1)c. \]
32: For this to hold for all $x, y \in \mathbb{Z}$, the coefficients of $(x+y)$ and the constant terms must be equal:
33: 1. $a^2 = 2a \implies a(a-2) = 0 \implies a = 0$ or $a = 2$.
34: 2. $(a+1)c = 3c \implies (a-2)c = 0$.
35: 
36: - If $a = 0$, then $(0-2)c = 0 \implies -2c = 0 \implies c = 0$. This yields $f(x) = 0x + 0 = 0$.
37: - If $a = 2$, then $(2-2)c = 0 \implies 0 = 0$, which is true for any $c \in \mathbb{Z}$. This yields $f(x) = 2x + c$.
38: 
39: **5. Verification**
40: - If $f(x) = 0$, then $0 + 2(0) = f(0) = 0$. (Correct)
41: - If $f(x) = 2x + c$, then $f(2x) + 2f(y) = (4x+c) + 2(2y+c) = 4x + 4y + 3c$ and $f(f(x+y)) = f(2(x+y)+c) = 2(2x+2y+c) + c = 4x + 4y + 3c$. (Correct)
42: 
43: The solutions are $f(x) = 0$ and $f(x) = 2x + c$ for any $c \in \mathbb{Z}$. \(\square\)

# Proof B

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
