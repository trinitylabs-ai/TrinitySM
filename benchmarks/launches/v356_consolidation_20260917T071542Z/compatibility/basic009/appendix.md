## Checked counting lemma D

For any 18 labeled real numbers with nonnegative total sum, at least 136 of their unordered 3-subsets have nonnegative sum.

Partition the labels into 6 unordered blocks of size 3. Every partition has at least one block of nonnegative sum: otherwise the total would be negative. The number of partitions is T = 18! / ((3!)^6 6!) = 190590400. A fixed block occurs in U = 15! / ((3!)^5 5!) = 1401400 partitions. These formulas follow by ordering all labels, then dividing by the permutations within each block and of the blocks. Count incidences between partitions and their nonnegative blocks. If A is the number of nonnegative blocks, then A U >= T, hence A >= T/U = 136. Labels distinguish equal weights. Blocks of sum zero qualify.