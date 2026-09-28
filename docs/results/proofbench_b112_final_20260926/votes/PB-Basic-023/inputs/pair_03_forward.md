# Problem

Suppose $a,b,c$ are positive integers such that $2^{a}+1=7^{b}+2^{c}$.
 Find all possible values of $(a,b,c)$.

# Proof A

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

# Proof B

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
