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
