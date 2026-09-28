The most difficult part of this problem is to observe that $(B, T, P, C)$ are concyclic. If this holds, let $Y$ be the intersection of $TP$ and $BC$. Then $YH \cdot YM = YT \cdot YP = YB \cdot YC$,
 which means that $Y$ is the point such that $(B, H, C, Y)$ is a harmonic division. This is a fixed point. Thus, $T$ lies on the inversion of $AC$ with respect to the circle centered at $Y$ with radius $\sqrt{YB \cdot YC}$. This is a fixed circle.

 \textbf{Claim:} $(B, T, P, C)$ are concyclic. This means that the circumcircles of $\triangle BPC$, $\triangle PHM$, and $\triangle KPQ$ are coaxial. We will use the following well-known Lemma: For two circles, the locus of points where the ratio of the powers with respect to the two circles is constant is a circle coaxial with the two circles.
 Now, using the Lemma, we see that it suffices to show that: The ratio of the powers of $B$ and $C$ with respect to the circumcircles of $\triangle PHM$ and $\triangle KPQ$ are the same.

 1) The ratio of powers of $B$ and $C$ with respect to the circumcircle of $\triangle PHM$ is $\frac{BH \cdot BM}{CH \cdot CM} = \frac{BH}{CH}$.

 2) Let's compute the ratio of powers of $B$ and $C$ with respect to the circumcircle of $\triangle KPQ$. Let $H_2$ be the foot of the perpendicular from $Q$ to $AC$, and let $L$ be the reflection of $A$ across $H_2$. Since $\angle QKP = \angle QLP = 180^\circ - \angle A$, $(K, L, P, Q)$ are concyclic. The power of $B$ is $BK \cdot BQ$, and the power of $C$ is $CL \cdot CP$. We want to show that $\frac{CL \cdot CP}{BK \cdot BQ} = \frac{CH}{BH}$.

 Let $D, E$ be the intersection of the Euler line of $\triangle ABC$ with $AB, AC$ respectively. Let $R$ be the intersection of $AX$ and $BC$.
 By Ceva's theorem, $\frac{CP}{BQ} = \frac{AP}{AQ} \times \frac{CR}{BR}$. $BK = BA - KA = BA - 2AP \cos A$, $CL = CA - LA = CA - 2AQ \cos A$.
 Thus $\frac{CL \cdot CP}{BK \cdot BQ} = \frac{CA - 2AQ \cos A}{BA - 2AP \cos A} \times \frac{AP}{AQ} \times \frac{CR}{BR} = \frac{\frac{CA}{AQ} - 2 \cos A}{\frac{BA}{AP} - 2 \cos A} \times \frac{CR}{BR}$.

 Let $\frac{XE}{DX} = \lambda$.
 $\frac{CR}{BR} = \frac{AC \sin \angle CAR}{AB \sin \angle BAR} = \frac{AC}{AB} \cdot \frac{AD}{AE} \cdot \frac{XE}{DX} = \frac{AC \cdot AD}{AB \cdot AE} \lambda$.
 By Menelaus' theorem on $\triangle ADE$ and line $CXQ$,
 $\frac{AQ}{QD} \cdot \frac{CE}{AC} \cdot \frac{DX}{EX} = 1$. Thus, $\frac{AQ}{QD} = \frac{AC}{CE} \lambda$, so $AQ = \frac{1}{1 + \frac{AC}{CE} \lambda} AD = \frac{AD}{1+\lambda \frac{AC}{CE}}.$
 Similarly, $AP = \frac{1}{1 + \frac{1}{\lambda} \frac{AB}{BD}} AE$.
 Thus $\frac{CL \cdot CP}{BK \cdot BQ} = \frac{\frac{CA}{AQ} - 2 \cos A}{\frac{BA}{AP} - 2 \cos A} \times \frac{CR}{BR}$ has the form $\frac{(\text{linear in } \lambda)}{(\text{linear in } \lambda)}$. That is, if it is $\frac{CH}{BH}$ for two values of $\lambda$, then it is $\frac{CH}{BH}$ for all $\lambda$.

 Case 1) $X = H$.
 In this case, $P, Q$ are the feet of the altitudes from $B, C$ respectively. Thus $KL \parallel BC$. Thus $\frac{CL \cdot CP}{BK \cdot BQ} = \frac{CH \cdot CB}{BH \cdot BC} = \frac{CH}{BH}$.

 Case 2) $X = G$.
 In this case, $P, Q$ are the midpoints of $AC, AB$, and $K, L$ are the feet of altitudes from $C, B$ respectively. Thus $\frac{CL \cdot CP}{BK \cdot BQ} = \frac{CH \cdot \frac{CB}{2}}{BH \cdot \frac{BC}{2}} = \frac{CH}{BH}$.
 Since $H \neq G$ due to scalene condition, we have two different values of $\lambda$, completing the proof.