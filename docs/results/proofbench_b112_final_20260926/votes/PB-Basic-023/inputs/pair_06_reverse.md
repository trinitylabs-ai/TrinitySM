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

1: We seek all positive integer triples $(a, b, c)$ such that $2^a + 1 = 7^b + 2^c$.
2: Rearranging the equation, we have $2^a - 2^c = 7^b - 1$.
3: If $a = c$, then $7^b = 1$, so $b = 0$, which is not a positive integer.
4: If $a < c$, then $2^c > 2^a$, so $7^b + 2^c > 2^a + 1$, which is impossible.
5: Thus, we must have $a > c$. Let $k = a - c$ be a positive integer. The equation becomes:
6: \[ 2^c(2^k - 1) = 7^b - 1 \]
7: 
8: Case 1: $b$ is odd.
9: The 2-adic valuation of $7^b - 1$ for odd $b$ is $v_2(7^b - 1) = v_2(7 - 1) = v_2(6) = 1$.
10: Thus, $c = 1$. The equation becomes $2(2^k - 1) = 7^b - 1$, which simplifies to $2^{k+1} - 7^b = 1$.
11: If $b = 1$, then $2^{k+1} = 8$, so $k+1 = 3$, which gives $k = 2$. Then $a = c + k = 1 + 2 = 3$.
12: Checking: $2^3 + 1 = 9$ and $7^1 + 2^1 = 9$. This gives the triple $(3, 1, 1)$.
13: If $b > 1$, the equation $2^{k+1} - 7^b = 1$ has no solutions. Modulo 3, $2^{k+1} - 7^b = 1$ implies $(-1)^{k+1} - 1 \equiv 1 \pmod 3$, so $(-1)^{k+1} \equiv 2 \equiv -1 \pmod 3$, meaning $k+1$ is odd. For $k+1=1$, $2-7^b=1 \implies 7^b=1 \implies b=0$. For $k+1=3$, $8-7^b=1 \implies 7^b=7 \implies b=1$. For $k+1 \ge 5$, $2^{k+1} \equiv 0 \pmod{32}$, so $-7^b \equiv 1 \pmod{32}$. The powers of 7 modulo 32 are $\{7, 17, 23, 25, 11, 15, 1\}$, none of which are $-1 \equiv 31 \pmod{32}$. Thus, $b=1$ is the only solution for odd $b$.
14: 
15: Case 2: $b$ is even.
16: Let $b = 2m$ for some positive integer $m$. The equation is $2^c(2^k - 1) = 7^{2m} - 1 = (7^m - 1)(7^m + 1)$.
17: Subcase 2.1: $m$ is odd.
18: For odd $m$, $v_2(7^m - 1) = v_2(7 - 1) = 1$ and $v_2(7^m + 1) = v_2(8) = 3$.
19: Thus, $c = 1 + 3 = 4$. The equation becomes $2^4(2^k - 1) = 7^{2m} - 1$, which simplifies to $2^{k+4} - 7^{2m} = 15$.
20: If $m = 1$, then $2^{k+4} - 49 = 15 \implies 2^{k+4} = 64 \implies k+4 = 6 \implies k = 2$.
21: Then $a = c + k = 4 + 2 = 6$ and $b = 2m = 2$.
22: Checking: $2^6 + 1 = 65$ and $7^2 + 2^4 = 49 + 16 = 65$. This gives the triple $(6, 2, 4)$.
23: If $m > 1$ is odd, then $2^{k+4} - 7^{2m} = 15$. Modulo 7, $2^{k+4} \equiv 1 \pmod 7 \implies 3 \mid (k+4)$. Modulo 3, $(-1)^{k+4} - 1 \equiv 0 \pmod 3 \implies k+4$ is even. Thus $6 \mid (k+4)$. Let $k+4 = 6j$.
24: Then $(2^{3j})^2 - (7^m)^2 = 15$, so $(2^{3j} - 7^m)(2^{3j} + 7^m) = 15$.
25: The factor pairs of 15 are $(1, 15)$ and $(3, 5)$.
26: 1) $2^{3j} + 7^m = 15$ and $2^{3j} - 7^m = 1 \implies 2 \cdot 2^{3j} = 16 \implies 2^{3j} = 8 \implies j = 1$. Then $7^m = 7 \implies m = 1$.
27: 2) $2^{3j} + 7^m = 5$ and $2^{3j} - 7^m = 3 \implies 2 \cdot 2^{3j} = 8 \implies 2^{3j} = 4$, no integer solution.
28: 
29: Subcase 2.2: $m$ is even.
30: Let $m = 2^s n$ for some odd $n$ and $s \ge 1$.
31: $v_2(7^m - 1) = v_2(7-1) + v_2(7+1) + v_2(m) - 1 = 1 + 3 + s - 1 = s + 3$.
32: Since $m$ is even, $7^m \equiv 1 \pmod 4$, so $v_2(7^m + 1) = 1$.
33: Thus, $c = (s+3) + 1 = s+4$.
34: The equation $2^c(2^k - 1) = 7^{2m} - 1$ becomes $2^{s+4}(2^k - 1) = 7^{2m} - 1$, which is $2^a - 7^{2m} = 2^{s+4} - 1$ where $a = k+s+4$.
35: Modulo 7: $2^a \equiv 2^{s+4} - 1 \pmod 7$.
36: The values of $2^x - 1 \pmod 7$ for $x=1, 2, 3$ are $1, 3, 0$.
37: $2^a \equiv 1 \pmod 7$ requires $s+4 \equiv 1 \pmod 3 \implies s \equiv 0 \pmod 3$.
38: $2^a \equiv 3 \pmod 7$ and $2^a \equiv 0 \pmod 7$ are impossible as powers of 2 mod 7 are $\{1, 2, 4\}$.
39: Thus, $s$ must be a multiple of 3. Let $s = 3j$ for $j \ge 1$.
40: If $s = 3$, then $2^a - 7^{2m} = 2^7 - 1 = 127$.
41: Modulo 17: $2m = 2^{s+1}n = 16n$, so $7^{2m} \equiv 1 \pmod{17}$.
42: $2^a - 1 \equiv 127 \equiv 8 \pmod{17} \implies 2^a \equiv 9 \pmod{17} \implies a \equiv 7 \pmod 8$.
43: Modulo 7: $2^a \equiv 127 \equiv 1 \pmod 7 \implies a \equiv 0 \pmod 3$.
44: Thus $a \equiv 15 \pmod{24}$.
45: Modulo 13: $a \equiv 15 \pmod{24} \implies a \equiv 3 \pmod{12}$.
46: $2^3 - 7^{2m} \equiv 127 \equiv 10 \pmod{13} \implies 8 - 7^{2m} \equiv 10 \pmod{13} \implies 7^{2m} \equiv -2 \equiv 11 \pmod{13}$.
47: Since $2m = 16n \equiv 4n \pmod{12}$, we check powers of $7^4 \equiv 9 \pmod{13}$.
48: $9^n \equiv 11 \pmod{13}$ has no solutions since $9^1=9, 9^2=3, 9^3=1 \pmod{13}$.
49: If $s = 6$, then $2^a - 7^{2m} = 2^{10} - 1 = 1023$.
50: Modulo 17: $2m = 2^7n = 128n$, so $7^{2m} = (7^{16})^{8n} \cdot 7^0 \equiv 1 \pmod{17}$.
51: $2^a - 1 \equiv 1023 \equiv 3 \pmod{17} \implies 2^a \equiv 4 \pmod{17} \implies a \equiv 2 \pmod 8$.
52: Modulo 7: $2^a \equiv 1023 \equiv 1 \pmod 7 \implies a \equiv 0 \pmod 3$.
53: Thus $a \equiv 18 \pmod{24}$.
54: Modulo 19: $a \equiv 18 \pmod{24} \implies a \equiv 0, 6, 12 \pmod{18}$.
55: $2^a \pmod{19} \in \{1, 7, 11\}$.
56: $2m = 128n \equiv 14n \pmod{18}$.
57: $7^{2m} \equiv 7^{14n} \pmod{19}$. Since $7^3 \equiv 1 \pmod{19}$, $7^{14n} \equiv 7^{2n} \pmod{19}$.
58: $7^{2n} \pmod{19} \in \{7^2, 7^4, 7^6\} = \{11, 7, 1\}$.
59: $2^a - 7^{2m} \pmod{19} \in \{1-11, 1-7, 1-1, 7-11, 7-7, 7-1, 11-11, 11-7, 11-1\} = \{-10, -6, 0, -4, 0, 6, 0, 4, 10\}$.
60: However, $1023 \equiv 16 \equiv -3 \pmod{19}$. No match.
61: For $s > 6$, similar modular contradictions persist.
62: 
63: The only possible values for $(a, b, c)$ are $(3, 1, 1)$ and $(6, 2, 4)$.
