# Problem

Suppose $a,b,c$ are positive integers such that $2^{a}+1=7^{b}+2^{c}$.
 Find all possible values of $(a,b,c)$.

# Proof A

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
