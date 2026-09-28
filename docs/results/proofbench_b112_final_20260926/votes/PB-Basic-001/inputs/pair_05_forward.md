# Problem

Determine all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that, for all $x, y \in \mathbb{Z}$, we have \[ f(2x)+2f(y)=f(f(x+y)).\]

# Proof A

1: To determine all functions $f: \mathbb{Z} \rightarrow \mathbb{Z}$ such that
2: \[ f(2x) + 2f(y) = f(f(x+y)) \quad \text{for all } x, y \in \mathbb{Z}, \]
3: we proceed by analyzing the functional equation through substitutions.
4: 
5: **1. Establishing a relation for $f(f(n))$**
6: Let $x = 0$ in the original equation. We obtain:
7: \[ f(0) + 2f(y) = f(f(y)) \]
8: for all $y \in \mathbb{Z}$. Let $f(0) = c$. Thus, we have the identity:
9: \[ f(f(y)) = 2f(y) + c \quad \text{(1)} \]
10: 
11: **2. Simplifying the original equation**
12: Substitute the identity (1) into the original equation $f(2x) + 2f(y) = f(f(x+y))$ by replacing $f(f(x+y))$ with $2f(x+y) + c$:
13: \[ f(2x) + 2f(y) = 2f(x+y) + c \quad \text{(2)} \]
14: 
15: **3. Finding a relation for $f(2x)$**
16: Set $y = 0$ in equation (2):
17: \[ f(2x) + 2f(0) = 2f(x) + c \]
18: Since $f(0) = c$, this becomes:
19: \[ f(2x) + 2c = 2f(x) + c \implies f(2x) = 2f(x) - c \quad \text{(3)} \]
20: 
21: **4. Reducing to Cauchy's Functional Equation**
22: Now substitute the expression for $f(2x)$ from (3) back into equation (2):
23: \[ (2f(x) - c) + 2f(y) = 2f(x+y) + c \]
24: \[ 2f(x) + 2f(y) = 2f(x+y) + 2c \]
25: Dividing the entire equation by 2, we get:
26: \[ f(x) + f(y) = f(x+y) + c \]
27: To solve this, we define a new function $g: \mathbb{Z} \to \mathbb{Z}$ such that $g(n) = f(n) - c$. Then $f(n) = g(n) + c$. Substituting this into the equation:
28: \[ (g(x) + c) + (g(y) + c) = (g(x+y) + c) + c \]
29: \[ g(x) + g(y) + 2c = g(x+y) + 2c \]
30: \[ g(x) + g(y) = g(x+y) \]
31: This is Cauchy's functional equation on the integers. The only solutions to $g(x+y) = g(x) + g(y)$ for $g: \mathbb{Z} \to \mathbb{Z}$ are linear functions of the form $g(x) = ax$ for some constant $a \in \mathbb{Z}$. Consequently:
32: \[ f(x) = ax + c \]
33: 
34: **5. Determining the constants $a$ and $c$**
35: We substitute $f(x) = ax + c$ back into the original equation $f(2x) + 2f(y) = f(f(x+y))$ to find all possible values for $a$ and $c$:
36: LHS: $f(2x) + 2f(y) = (a(2x) + c) + 2(ay + c) = 2ax + 2ay + 3c$
37: RHS: $f(f(x+y)) = f(a(x+y) + c) = a(a(x+y) + c) + c = a^2x + a^2y + ac + c$
38: 
39: For the equation to hold for all $x, y \in \mathbb{Z}$, the coefficients of $x$ and $y$ must be equal, and the constant terms must be equal:
40: 1. $a^2 = 2a \implies a(a-2) = 0 \implies a = 0$ or $a = 2$.
41: 2. $ac + c = 3c \implies c(a - 2) = 0$.
42: 
43: *   If $a = 0$, the second condition becomes $c(0 - 2) = 0 \implies -2c = 0 \implies c = 0$. This yields the function $f(x) = 0$.
44: *   If $a = 2$, the second condition becomes $c(2 - 2) = 0 \implies 0 = 0$, which is true for any $c \in \mathbb{Z}$. This yields the functions $f(x) = 2x + c$.
45: 
46: **6. Verification**
47: *   For $f(x) = 0$: $f(2x) + 2f(y) = 0 + 0 = 0$ and $f(f(x+y)) = f(0) = 0$. (Correct)
48: *   For $f(x) = 2x + c$: $f(2x) + 2f(y) = (4x + c) + 2(2y + c) = 4x + 4y + 3c$.
49:     $f(f(x+y)) = f(2(x+y) + c) = 2(2x + 2y + c) + c = 4x + 4y + 3c$. (Correct)
50: 
51: The functions that satisfy the given equation are $f(n) = 0$ and $f(n) = 2n + c$ for any constant $c \in \mathbb{Z}$. \(\square\)

# Proof B

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
