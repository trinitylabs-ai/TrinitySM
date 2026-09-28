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
