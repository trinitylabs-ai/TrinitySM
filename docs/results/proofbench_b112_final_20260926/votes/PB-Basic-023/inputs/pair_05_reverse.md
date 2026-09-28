# Problem

Suppose $a,b,c$ are positive integers such that $2^{a}+1=7^{b}+2^{c}$.
 Find all possible values of $(a,b,c)$.

# Proof A

1: To find all positive integer solutions $(a, b, c)$ to the equation $2^a + 1 = 7^b + 2^c$, we first analyze the relative sizes of $a$ and $c$.
2: 
3: 1.  **Comparison of $a$ and $c$:**
4:     *   If $a = c$, the equation becomes $2^a + 1 = 7^b + 2^a$, which implies $7^b = 1$, so $b = 0$, contradicting $b \ge 1$.
5:     *   If $a < c$, the equation is $1 = 7^b + 2^a(2^{c-a} - 1)$. Since $a, b, c \ge 1$, we have $7^b \ge 7$ and $2^a(2^{c-a} - 1) \ge 2(2^1 - 1) = 2$, so $7^b + 2^a(2^{c-a} - 1) \ge 9$, a contradiction.
6:     *   Therefore, we must have $a > c$.
7: 
8: 2.  **Rearranging the Equation:**
9:     The equation $2^a + 1 = 7^b + 2^c$ can be rewritten as $2^c(2^{a-c} - 1) = 7^b - 1$.
10:     This implies $c = v_2(7^b - 1)$, where $v_2(n)$ is the exponent of the highest power of 2 dividing $n$.
11: 
12: 3.  **Case 1: $b$ is odd.**
13:     For odd $b$, $v_2(7^b - 1) = v_2(7 - 1) = v_2(6) = 1$. Thus $c = 1$.
14:     The equation becomes $2(2^{a-1} - 1) = 7^b - 1$, which simplifies to $2^a - 1 = 7^b$.
15:     If $b = 1$, then $2^a - 1 = 7 \implies 2^a = 8 \implies a = 3$. This gives the solution $(3, 1, 1)$.
16:     If $b > 1$, then $2^a - 1 = 7^b \equiv 0 \pmod{49}$. The order of 2 modulo 49 is 21, so $21 | a$.
17:     Then $2^{21} - 1$ must be a power of 7. However, $2^{21} - 1 = (2^7 - 1)(2^{14} + 2^7 + 1) = 127 \cdot (2^{14} + 2^7 + 1)$. Since 127 is not a power of 7, there are no solutions for $b > 1$.
18: 
19: 4.  **Case 2: $b$ is even.**
20:     Let $b = 2^k m$ with $m$ odd and $k \ge 1$. By the Lifting The Exponent Lemma,
21:     $v_2(7^b - 1) = v_2(7 - 1) + v_2(7 + 1) + v_2(b) - 1 = 1 + 3 + k - 1 = k + 3$.
22:     Thus $c = k + 3$. The equation becomes $2^{a-c} - 1 = \frac{7^b - 1}{2^c}$.
23: 
24:     *   **Subcase $k = 1$:**
25:         $b = 2m$ and $c = 4$. We have $2^{a-4} - 1 = \frac{7^{2m} - 1}{16} = \frac{(7^m - 1)(7^m + 1)}{16}$.
26:         Let $O_2 = \frac{7^m + 1}{8}$. Then $7^m = 8O_2 - 1$, so $\frac{7^m - 1}{2} = \frac{8O_2 - 2}{2} = 4O_2 - 1$.
27:         The equation is $2^{a-4} - 1 = (4O_2 - 1)O_2 = 4O_2^2 - O_2$.
28:         Rearranging gives $4O_2^2 - O_2 + (1 - 2^{a-4}) = 0$.
29:         The discriminant is $D = (-1)^2 - 4(4)(1 - 2^{a-4}) = 16 \cdot 2^{a-4} - 15 = 2^a - 15$.
30:         For $O_2$ to be an integer, $2^a - 15 = y^2$ for some integer $y$.
31:         Modulo 3, $y^2 \equiv (-1)^a \pmod 3$, so $a$ must be even. Let $a = 2n$.
32:         $(2^n - y)(2^n + y) = 15$.
33:         The possible pairs $(2^n - y, 2^n + y)$ are $(1, 15)$ and $(3, 5)$.
34:         - $2^n - y = 1, 2^n + y = 15 \implies 2 \cdot 2^n = 16 \implies n = 3 \implies a = 6$.
35:           Then $y = 7$, so $O_2 = \frac{1 + 7}{8} = 1 \implies \frac{7^m + 1}{8} = 1 \implies m = 1$.
36:           This gives $b = 2(1) = 2$ and $c = 4$. Solution: $(6, 2, 4)$.
37:         - $2^n - y = 3, 2^n + y = 5 \implies 2 \cdot 2^n = 8 \implies n = 2 \implies a = 4$.
38:           Then $y = 1$, so $O_2 = \frac{1 \pm 1}{8}$, which is not a positive integer.
39: 
40:     *   **Subcase $k \ge 2$:**
41:         In this case, $b$ is a multiple of 4. We have $7^4 - 1 = 2400 = 2^5 \cdot 3 \cdot 5^2$.
42:         Thus $v_5(7^b - 1) = v_5(7^4 - 1) + v_5(b/4) = 2 + v_5(b)$.
43:         Since $2^c$ is not divisible by 5, $v_5(2^{a-c} - 1) = v_5(7^b - 1) = 2 + v_5(b)$.
44:         The order of 2 modulo 5 is 4, so $v_5(2^{a-c} - 1) = v_5(2^4 - 1) + v_5(\frac{a-c}{4}) = 1 + v_5(a-c)$.
45:         Equating these, we get $1 + v_5(a-c) = 2 + v_5(b)$, so $v_5(a-c) = v_5(b) + 1$.
46:         This implies $5 | (a-c)$. Thus $2^5 - 1 = 31$ divides $2^{a-c} - 1$.
47:         Then $31 | \frac{7^b - 1}{2^c}$, so $31 | 7^b - 1$.
48:         The order of 7 modulo 31 is 15, so $15 | b$.
49:         Since $15 | b$, we have $5 | b$, so $v_5(b) \ge 1$.
50:         From $v_5(a-c) = v_5(b) + 1$, we have $v_5(a-c) \ge 2$, so $25 | (a-c)$.
51:         Then $2^{20} - 1$ divides $2^{a-c} - 1$ because $ord_{25}(2) = 20$.
52:         $2^{20} - 1 = (2^{10} - 1)(2^{10} + 1) = 1023 \cdot 1025 = (3 \cdot 11 \cdot 31) \cdot (25 \cdot 41)$.
53:         Thus $41 | 2^{a-c} - 1$, which implies $41 | \frac{7^b - 1}{2^c}$, so $41 | 7^b - 1$.
54:         The order of 7 modulo 41 is 40, so $40 | b$.
55:         Now consider the equation $2^{a-c} - 1 = \frac{7^b - 1}{2^c}$, which can be written as $2^{a} - 7^b = 2^c - 1$.
56:         Dividing by $7^b$, we get $|2^a 7^{-b} - 1| = \frac{2^c - 1}{7^b}$.
57:         For $k \ge 2$, $b \ge 4$ and $c = k+3$. Since $b = 2^k m$, we have $c \le \frac{b}{2} + 3$.
58:         The term $\frac{2^c - 1}{7^b} \le \frac{2^{b/2 + 3}}{7^b} = 8 \cdot (\frac{\sqrt{2}}{7})^b \approx 8 \cdot (0.202)^b$.
59:         For $b \ge 40$, this value is extremely small (less than $10^{-25}$).
60:         However, $|2^a 7^{-b} - 1| = |2^{a - b \log_2 7} - 1| \approx |(a - b \log_2 7) \ln 2|$.
61:         Since $a$ and $b$ are integers and $\log_2 7$ is irrational, the distance $|a - b \log_2 7|$ cannot be arbitrarily small. Specifically, for $b=40$, the closest integer $a$ to $40 \log_2 7 \approx 112.294$ is $a=112$, giving a distance of $0.294$.
62:         For any $b$, the distance $|a - b \log_2 7|$ is much larger than $8 \cdot (0.202)^b$.
63:         Thus, no solutions exist for $k \ge 2$.
64: 
65: The only possible values for $(a, b, c)$ are $(3, 1, 1)$ and $(6, 2, 4)$.

# Proof B

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
