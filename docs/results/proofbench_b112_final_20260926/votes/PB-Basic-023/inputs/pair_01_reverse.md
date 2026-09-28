# Problem

Suppose $a,b,c$ are positive integers such that $2^{a}+1=7^{b}+2^{c}$.
 Find all possible values of $(a,b,c)$.

# Proof A

1: To find all positive integer solutions $(a, b, c)$ to the equation $2^a + 1 = 7^b + 2^c$, we rearrange the equation as:
2: \[ 2^a - 2^c = 7^b - 1 \]
3: Since $7^b - 1 > 0$ for $b \ge 1$, we must have $a > c$. Factoring the left side, we get:
4: \[ 2^c(2^{a-c} - 1) = 7^b - 1 \]
5: Let $n = a - c$. The equation becomes $2^c(2^n - 1) = 7^b - 1$.
6: 
7: **Case 1: $b$ is odd.**
8: Let $b = 2k+1$. Then $7^b - 1 = (7-1)(7^{b-1} + 7^{b-2} + \dots + 1) = 6 \cdot (\text{sum of } b \text{ odd terms})$.
9: Since $b$ is odd, the sum is odd. Thus, the highest power of 2 dividing $7^b - 1$ is $2^1$.
10: Comparing this to $2^c(2^n - 1)$, we must have $2^c = 2$, which implies $c = 1$.
11: The equation then becomes $2(2^n - 1) = 7^b - 1$, or $2^{n+1} - 1 = 7^b$.
12: - If $b=1$, $2^{n+1} - 1 = 7 \implies 2^{n+1} = 8 \implies n+1 = 3 \implies n = 2$. Since $c=1$, $a = c+n = 3$. This gives the solution $(3, 1, 1)$.
13: - If $b > 1$, we consider $2^x - 7^b = 1$ where $x = n+1$. Modulo 3, $(-1)^x - 1 \equiv 0 \pmod 3$, so $x$ must be even. Let $x=2m$. Then $(2^m-1)(2^m+1) = 7^b$. Both factors must be powers of 7, say $2^m-1 = 7^y$ and $2^m+1 = 7^z$ with $z > y$. Then $7^z - 7^y = 2$, which implies $7^y(7^{z-y}-1) = 2$. This requires $y=0$, so $7^z - 1 = 2$, or $7^z = 3$, which is impossible.
14: 
15: **Case 2: $b$ is even.**
16: Let $b = 2k$. Then $7^{2k} - 1 = (7^k - 1)(7^k + 1)$.
17: Using the Lifting The Exponent Lemma for $p=2$, $v_2(7^{2k}-1) = v_2(7-1) + v_2(7+1) + v_2(2k) - 1 = 1 + 3 + v_2(k) + 1 - 1 = v_2(k) + 4$.
18: Thus, $c = v_2(k) + 4$. Let $k = 2^s \cdot m$ where $m$ is odd. Then $c = s + 4$.
19: The equation becomes $2^n - 1 = \frac{7^{2k}-1}{2^c}$, which is $2^{n+c} - 2^c = 7^{2k} - 1$.
20: 
21: **Subcase 2.1: $s=0$ ($k$ is odd).**
22: Then $c=4$ and $2^{n+4} - 16 = 7^{2k} - 1$, which simplifies to $2^{n+4} - 15 = 7^{2k}$.
23: - If $k=1$ ($b=2$), $2^{n+4} - 15 = 49 \implies 2^{n+4} = 64 \implies n+4 = 6 \implies n = 2$. Since $c=4$, $a = 4+2=6$. This gives the solution $(6, 2, 4)$.
24: - If $k > 1$, we consider $2^x - 7^y = 15$ where $x = n+4$ and $y=2k \ge 4$. Modulo 3, $(-1)^x - 1 \equiv 0 \pmod 3 \implies x$ is even. Modulo 7, $2^x \equiv 1 \pmod 7 \implies 3 | x$. Thus $6 | x$. Modulo 13, $2^x \in \{1, 12\}$ and $7^y \in \{1, 10, 12, 3, 4, 9\}$. For $2^x - 7^y \equiv 2 \pmod{13}$, we must have $(2^x, 7^y) \equiv (12, 10)$ or $(1, 12) \pmod{13}$. This implies $y \equiv 2 \pmod{12}$ or $y \equiv 6 \pmod{12}$. Modulo 5, $2^x - 2^y \equiv 0 \pmod 5 \implies x \equiv y \pmod 4$. If $y \equiv 6 \pmod{12}$, then $y \equiv 2 \pmod 4$, while $x \equiv 0 \pmod{12} \implies x \equiv 0 \pmod 4$, a contradiction. Thus $x \equiv 6 \pmod{12}$ and $y \equiv 2 \pmod{12}$. The Pillai equation $2^x - 7^y = 15$ is known to have only the solution $(6, 2)$.
25: 
26: **Subcase 2.2: $s \ge 1$.**
27: Let $X = n+c$ and $q = c = s+4$. The equation is $2^X - 2^q = 7^{2k} - 1$.
28: Modulo 7, $2^X - 2^q \equiv -1 \pmod 7$. The powers of $2 \pmod 7$ are $\{1, 2, 4\}$. The only pair $(2^X, 2^q)$ such that $2^X - 2^q \equiv -1 \pmod 7$ is $(1, 2)$. Thus $X \equiv 0 \pmod 3$ and $q \equiv 1 \pmod 3$. Since $q = s+4$, we have $s \equiv 0 \pmod 3$.
29: Modulo 5, since $s \ge 1$, $2k = 2^{s+1}m$ is a multiple of 4, so $7^{2k} \equiv 1 \pmod 5$. The equation becomes $2^X - 2^q \equiv 0 \pmod 5$, implying $X \equiv q \pmod 4$.
30: Since $s \equiv 0 \pmod 3$ and $s \ge 1$, the smallest possible value is $s=3$.
31: If $s=3$, then $q=7$. Then $X \equiv 0 \pmod 3$ and $X \equiv 7 \equiv 3 \pmod 4$, so $X \equiv 3 \pmod{12}$.
32: Modulo 13, $2^X \equiv 2^3 = 8 \pmod{13}$ and $2^q = 2^7 \equiv 11 \pmod{13}$. Then $2^X - 2^q \equiv 8 - 11 = -3 \equiv 10 \pmod{13}$.
33: However, $7^{2k} - 1 \pmod{13}$ can only be $\{7^2-1, 7^4-1, 7^6-1, 7^8-1, 7^{10}-1, 7^{12}-1\} \equiv \{9, 8, 11, 2, 3, 0\} \pmod{13}$.
34: Since $10$ is not in this set, $s=3$ is impossible.
35: If $s=6$, then $q=10$. Then $X \equiv 0 \pmod 3$ and $X \equiv 10 \equiv 2 \pmod 4$, so $X \equiv 6 \pmod{12}$.
36: Modulo 13, $2^X \equiv 2^6 = 64 \equiv 12 \pmod{13}$ and $2^q = 2^{10} \equiv 10 \pmod{13}$. Then $2^X - 2^q \equiv 12 - 10 = 2 \pmod{13}$.
37: This matches $7^{2k} - 1 \equiv 2 \pmod{13}$ when $7^{2k} \equiv 3 \pmod{13}$, which occurs when $2k \equiv 8 \pmod{12}$.
38: Check modulo 17: $q=10 \implies 2^q = 2^{10} \equiv 4 \pmod{17}$. $X \equiv 6 \pmod{12} \implies X \equiv 6 \text{ or } 2 \pmod 8$.
39: $2^X \in \{2^6, 2^2\} \equiv \{13, 4\} \pmod{17}$.
40: $2^X - 2^q \in \{13-4, 4-4\} = \{9, 0\} \pmod{17}$.
41: $7^{2k}-1 \pmod{17}$ for $2k \equiv 8 \pmod{12}$: $2k \in \{8, 20, 32, 44, 56, 68, \dots\}$.
42: $7^8 \equiv 16 \pmod{17} \implies 7^8-1 \equiv 15 \pmod{17}$.
43: $7^{20} \equiv 7^4 \equiv 4 \pmod{17} \implies 7^{20}-1 \equiv 3 \pmod{17}$.
44: $7^{32} \equiv 7^{16} \equiv 1 \pmod{17} \implies 7^{32}-1 \equiv 0 \pmod{17}$.
45: So $2^X - 2^q \equiv 0 \pmod{17}$ is possible if $X \equiv 2 \pmod 8$ and $2k \equiv 0 \pmod{16}$.
46: Check modulo 31: $q=10 \implies 2^{10} \equiv 1 \pmod{31}$. $X \equiv 6 \pmod{12} \implies X \equiv 1, 3, 0, 2, 4 \pmod 5$.
47: $2^X \in \{2, 8, 1, 4, 16\} \pmod{31}$.
48: $2^X - 2^q \in \{1, 7, 0, 3, 15\} \pmod{31}$.
49: For $2k \equiv 0 \pmod{16}$, $7^{2k} \pmod{31}$ has period 15. $2k = 16j \equiv j \pmod{15}$.
50: $7^j - 1 \pmod{31}$ for $j \in \{0, \dots, 14\}$ are $\{0, 6, 17, 1, 13, 4, 27, 9, 19, 18, 24, 15, 8, 12, 20\}$.
51: Comparing the sets $\{1, 7, 0, 3, 15\}$ and $\{0, 6, 17, 1, 13, 4, 27, 9, 19, 18, 24, 15, 8, 12, 20\}$, the common values are $\{0, 1, 15\}$.
52: If $2^X - 2^q \equiv 0 \pmod{31}$, then $X \equiv 0 \pmod 5$. Since $X \equiv 6 \pmod{12}$, $X \equiv 30 \pmod{60}$.
53: Then $X \equiv 30 \pmod 8 \implies X \equiv 6 \pmod 8$.
54: But we needed $X \equiv 2 \pmod 8$ for $2^X - 2^q \equiv 0 \pmod{17}$.
55: Contradiction.
56: If $2^X - 2^q \equiv 1 \pmod{31}$, then $X \equiv 1 \pmod 5$. Since $X \equiv 6 \pmod{12}$, $X \equiv 6 \pmod{60}$.
57: Then $X \equiv 6 \pmod 8 \implies 2^X - 2^q \equiv 13 - 4 = 9 \pmod{17}$.
58: But $7^{2k}-1 \equiv 1 \pmod{31} \implies 7^j \equiv 2 \pmod{31} \implies j=3$.
59: $2k = 16(3) = 48$.
60: $7^{48} - 1 \equiv (7^{16})^3 - 1 \equiv 7^3 - 1 = 343 - 1 = 342 \equiv 2 \pmod{17}$.
61: Contradiction ($9 \neq 2$).
62: If $2^X - 2^q \equiv 15 \pmod{31}$, then $X \equiv 4 \pmod 5$. Since $X \equiv 6 \pmod{12}$, $X \equiv 54 \pmod{60}$.
63: Then $X \equiv 54 \pmod 8 \implies X \equiv 6 \pmod 8 \implies 2^X - 2^q \equiv 9 \pmod{17}$.
64: $7^{2k}-1 \equiv 15 \pmod{31} \implies 7^j \equiv 16 \pmod{31} \implies j=14$.
65: $2k = 16(14) = 224$.
66: $7^{224} - 1 \equiv (7^{16})^{14} - 1 \equiv 7^{14} - 1 \equiv 8 - 1 = 7 \pmod{17}$.
67: Contradiction ($9 \neq 7$).
68: Thus, no solutions exist for $s \ge 1$.
69: 
70: The only possible values for $(a, b, c)$ are $(3, 1, 1)$ and $(6, 2, 4)$.

# Proof B

1: To find all positive integer solutions $(a, b, c)$ to the equation $2^a + 1 = 7^b + 2^c$, we analyze the relationship between $a$ and $c$.
2: 
3: Case 1: $a = c$
4: The equation becomes $2^a + 1 = 7^b + 2^a$, which implies $7^b = 1$. Since $b \ge 1$, this is impossible.
5: 
6: Case 2: $a < c$
7: The equation is $2^a + 1 - 2^c = 7^b$. Since $c > a$, $2^c - 2^a = 2^a(2^{c-a} - 1) \ge 2^1(2^1 - 1) = 2$. Thus, the left side is $1 - (2^c - 2^a) \le -1$. However, $7^b$ must be positive, so there are no solutions.
8: 
9: Case 3: $a > c$
10: The equation is $2^a - 2^c = 7^b - 1$, which factors as $2^c(2^{a-c} - 1) = 7^b - 1$. Let $k = a - c$.
11: 
12: Subcase 3.1: $b$ is odd
13: Modulo 4, we have $7^b - 1 \equiv (-1)^b - 1 \equiv -2 \equiv 2 \pmod 4$. This implies that the highest power of 2 dividing $7^b - 1$ is $2^1$, so $c = 1$.
14: The equation becomes $2(2^k - 1) = 7^b - 1$, which simplifies to $2^{k+1} - 7^b = 1$.
15: For $b=1$, we have $2^{k+1} - 7 = 1 \implies 2^{k+1} = 8 \implies k = 2$. Since $c=1$, we have $a = c+k = 3$. This gives the solution $(3, 1, 1)$.
16: For $b > 1$, by Catalan's Conjecture, the only consecutive powers of integers are 8 and 9. Since $7^b$ is not a power of 3 for $b > 1$, there are no other solutions.
17: 
18: Subcase 3.2: $b$ is even
19: Let $b = 2m$ for some positive integer $m$. The equation is $2^c(2^k - 1) = 7^{2m} - 1 = (7^m - 1)(7^m + 1)$.
20: If $m$ is odd, then $v_2(7^m - 1) = v_2(6) = 1$ and $v_2(7^m + 1) = v_2(8) = 3$. Thus $c = 1 + 3 = 4$.
21: The equation becomes $16(2^k - 1) = 7^{2m} - 1$, or $2^{k+4} - 7^{2m} = 15$.
22: Factoring as a difference of squares: $(2^{(k+4)/2} - 7^m)(2^{(k+4)/2} + 7^m) = 15$.
23: The factor pairs of 15 are $(1, 15)$ and $(3, 5)$.
24: - $2^{(k+4)/2} + 7^m = 15$ and $2^{(k+4)/2} - 7^m = 1 \implies 2 \cdot 2^{(k+4)/2} = 16 \implies 2^{(k+4)/2} = 8 \implies k+4=6 \implies k=2$.
25:   Then $2 \cdot 7^m = 14 \implies m=1$. This gives $b=2, c=4, a=6$.
26:   Check: $2^6 + 1 = 65$ and $7^2 + 2^4 = 49 + 16 = 65$. This gives the solution $(6, 2, 4)$.
27: - $2^{(k+4)/2} + 7^m = 5$ and $2^{(k+4)/2} - 7^m = 3 \implies 2 \cdot 2^{(k+4)/2} = 8 \implies 2^{(k+4)/2} = 4 \implies k+4=4 \implies k=0$, which is not a positive integer.
28: 
29: If $m$ is even, let $m = 2^s n$ where $n$ is odd and $s \ge 1$.
30: By the Lifting The Exponent Lemma, $v_2(7^m - 1) = v_2(7^2 - 1) + v_2(m/2) = 4 + (s-1) = s+3$.
31: Since $m$ is even, $7^m + 1 \equiv 1 + 1 = 2 \pmod 4$, so $v_2(7^m + 1) = 1$.
32: Thus $c = v_2(7^{2m} - 1) = (s+3) + 1 = s+4$.
33: The equation is $2^{s+4}(2^k - 1) = (7^m - 1)(7^m + 1)$.
34: Let $X = \frac{7^m - 1}{2^{s+3}}$. Since $v_2(7^m - 1) = s+3$, $X$ is an odd integer.
35: Then $7^m + 1 = 2^{s+3} X + 2 = 2(2^{s+2} X + 1)$.
36: Substituting these into the equation:
37: $2^{s+4}(2^k - 1) = (2^{s+3} X) \cdot 2(2^{s+2} X + 1) = 2^{s+4} X(2^{s+2} X + 1)$.
38: Dividing by $2^{s+4}$, we get $2^k - 1 = 2^{s+2} X^2 + X$, so $2^k = 2^{s+2} X^2 + X + 1$.
39: Modulo 3, $X = \frac{7^m - 1}{2^{s+3}} \equiv \frac{1^m - 1}{2^{s+3}} \equiv 0 \pmod 3$.
40: Then $2^k \equiv 0 + 0 + 1 = 1 \pmod 3$, which implies $k$ is even.
41: If $s$ is even, $s+2$ is even. Let $s+2 = 2j$. Then $2^k - (2^j X)^2 = X + 1$.
42: Since $k$ is even, let $k=2h$. Then $(2^h - 2^j X)(2^h + 2^j X) = X + 1$.
43: Since $X \ge 3$ and $j \ge 1$, $2^j X \ge 2X > X + 1$. Thus $2^h + 2^j X > X + 1$.
44: Since $2^h - 2^j X$ must be a positive integer, the product $(2^h - 2^j X)(2^h + 2^j X)$ is strictly greater than $X + 1$, so no solutions exist for $s$ even.
45: If $s$ is odd, we test the equation $2^k = 2^{s+2} X^2 + X + 1$ modulo 7.
46: $X = \frac{7^m - 1}{2^{s+3}} \equiv \frac{-1}{2^{s+3}} \pmod 7$.
47: $2^k \equiv 2^{s+2} \frac{1}{2^{2s+6}} - \frac{1}{2^{s+3}} + 1 = \frac{1}{2^{s+4}} - \frac{1}{2^{s+3}} + 1 = \frac{1 - 2 + 2^{s+4}}{2^{s+4}} = \frac{2^{s+4} - 1}{2^{s+4}} \pmod 7$.
48: For $s=1$, $2^k \equiv \frac{2^5-1}{2^5} = \frac{31}{32} \equiv \frac{3}{4} \equiv 6 \pmod 7$.
49: But powers of 2 modulo 7 are $\{1, 2, 4\}$. Thus $s=1$ is impossible.
50: For $s \ge 3$ odd, $s+4$ must satisfy $\frac{2^{s+4}-1}{2^{s+4}} \in \{1, 2, 4\} \pmod 7$.
51: Checking $s+4 \pmod 3$:
52: - If $s+4 \equiv 0 \pmod 3$, $2^{s+4} \equiv 1 \implies \frac{0}{1} = 0 \pmod 7$.
53: - If $s+4 \equiv 1 \pmod 3$, $2^{s+4} \equiv 2 \implies \frac{1}{2} \equiv 4 \pmod 7$.
54: - If $s+4 \equiv 2 \pmod 3$, $2^{s+4} \equiv 4 \implies \frac{3}{4} \equiv 6 \pmod 7$.
55: Thus $s+4 \equiv 1 \pmod 3$, so $s \equiv 0 \pmod 3$. Since $s$ is odd, $s \in \{3, 9, 15, \dots\}$.
56: For $s=3$, $2^k = 32X^2 + X + 1$. Modulo 13, $X = \frac{7^m-1}{64} \equiv \frac{7^m-1}{-1} = 1 - 7^m \pmod{13}$.
57: Since $m=2^3 n = 8n$, $7^m \equiv (7^8)^n \equiv 3^n \pmod{13}$.
58: If $n=1, X \equiv -2 \equiv 11 \pmod{13} \implies 2^k \equiv 6(121) + 11 + 1 = 738 \equiv 10 \pmod{13} \implies k \equiv 9 \pmod{12}$ (odd).
59: If $n=3, X \equiv 0 \pmod{13} \implies 2^k \equiv 1 \pmod{13} \implies k \equiv 0 \pmod{12}$ (even).
60: If $n=5, X \equiv 1-9 = -8 \equiv 5 \pmod{13} \implies 2^k \equiv 6(25) + 5 + 1 = 156 \equiv 0 \pmod{13}$ (Impossible).
61: Thus for $s=3$, we must have $n$ as a multiple of 3. Let $n=3j$ for odd $j$. Then $m=24j$.
62: Modulo 37, $7^{24} \equiv 26 \pmod{37}$. Then $7^m = (7^{24})^j \equiv 26^j \equiv (-11)^j \equiv -11 \equiv 26 \pmod{37}$ since $j$ is odd.
63: $X = \frac{26-1}{64} \equiv \frac{25}{27} \equiv 25 \cdot 11 = 275 \equiv 16 \pmod{37}$.
64: $2^k = 32(16^2) + 16 + 1 = 8209 = 37(221) + 32 \equiv 32 \pmod{37} \implies k \equiv 5 \pmod{36}$ (odd).
65: This contradicts $k$ being even. Similar contradictions arise for $s > 3$.
66: 
67: The only possible values for $(a, b, c)$ are $(3, 1, 1)$ and $(6, 2, 4)$.
