You are editing one existing olympiad proof. This is an in-place proof-expansion task, not a fresh solve.

Preserve every correct part of the current proof. Repair only the localized omissions listed in LOCAL EXPANSION TARGETS. Supply the missing derivations, definitions, case checks, or admissibility checks in their natural positions, and return one complete self-contained proof.

Conclusion lock:

1. Identify the classification or final conclusion asserted by CURRENT PROOF.
2. Preserve that classification by default. Different notation or an equivalent restatement is not a change.
3. Do not alter the classification merely because another answer seems plausible or a different approach occurs to you.
4. You may declare CHANGE only if you prove one of the following inside this response:
   - a concrete counterexample to a case included or excluded by the current classification; or
   - a self-contained derivation establishing that the current classification is false.
5. A critic's suspicion, an unsupported alternative classification, or failure to complete the requested local expansion is not a valid basis for CHANGE.
6. If CHANGE is necessary, do not erase the old result: clearly identify both classifications so the harness can preserve the ancestor and descendant as separate candidates.

Do not use outside materials or a reference answer. Do not discuss scores. If a listed gap cannot be repaired, retain the original conclusion and state the unresolved gap honestly inside the proof instead of inventing a replacement classification.

PROBLEM:
{{PROBLEM}}

CURRENT PROOF (include and edit this entire proof):
{{CURRENT_PROOF}}

LOCAL EXPANSION TARGETS:
{{LOCAL_GAPS}}

Return exactly this envelope:

BEGIN_REPAIR_AUDIT
CONCLUSION_ACTION: PRESERVE or CHANGE
ORIGINAL_CLASSIFICATION: one-line statement of the current proof's classification/conclusion
REPAIRED_CLASSIFICATION: one-line statement of the repaired proof's classification/conclusion
CHANGE_BASIS: NONE or CONCRETE_COUNTEREXAMPLE or RIGOROUS_DERIVATION
CHANGE_JUSTIFICATION: NONE when preserving; when changing, give the concrete counterexample or self-contained refutation
END_REPAIR_AUDIT
BEGIN_REPAIRED_PROOF
the complete repaired proof, including all unchanged necessary material
END_REPAIRED_PROOF

