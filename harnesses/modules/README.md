# TrinitySM modules

The public names describe the modules' roles. Historical package names identify
the exact implementations used in saved experiments and remain unchanged.

## Workshop Draft

Draft produces the initial proof portfolio from a statement. The released
configuration uses four Gemma candidate lanes, followed by lazy checking and
conditional proof expansion. Its output is the actual saved candidate proofs
handed to the refinement module.

The composite's recorded frontend is `0.3.263`. It executes that frontend only
through generation and lazy refinement; the original standalone package has a
broader historical workflow. See the
[recorded source documentation](../imo_proof_pipeline/releases/1.7.0/engine/source/cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905/README.md).

## Workshop Refine

Refine consumes the saved candidates. Each cycle collects reviews, fuses their
findings, audits the decision or repair brief, and revises the proof. Candidate
lanes remain independent. Later cycles read the preceding cycle's proof, and
saved checkpoints retain the proof and its provenance.

The recorded backend is `0.3.290+goldfree.1`, packaged with the policy of the
selected composite release. The official controller runs three refinement
passes automatically using Harness B implementation 1.12.0 and its final-pass driver. See the
[recorded source documentation](../imo_proof_pipeline/releases/1.7.0/engine/source/cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906/README.md)
and the [current release profile](../imo_proof_pipeline/releases/1.12.0/profile.json).

The final R2/R3 selector retains R3 only on four unanimous Gemma/Qwen decisions; the cross-lane selector then chooses one of the four lane finals by 24 pooled pairwise votes. See [B 1.12.0 selection](../../docs/harness_b_selection.md).

B uses [role-specific continuation cues](../../docs/harness_b.md); A 1.7.0 remains available.

## Workshop Tools — experimental

Tools is an optional extension for selected proof claims. It uses model calls
to identify and formalize a claim, applies an exact backend where supported,
then supplies checked evidence to proof rewriting. Formalization can fail;
a certificate establishes its specified claim, not the whole submitted proof.

The recorded implementations include geometry, algebraic, real-root and
discrete tools. Historical version numbers remain necessary for reproduction.
See [experimental status, commands and validation](../../experiments/workshop_tools/README.md).

## Workshop Pipeline

The [composite harness](../proof_workshop/README.md) connects Draft to Refine and
manages their four-lane problem workflow. The public module names are a naming
and documentation layer over the recorded code. They are not new independently
versioned Python packages or a claim that every internal stage has a standalone
command. Use the official composite entry point for the complete workflow.

Evaluation is separate from all solver modules. References, grading guidelines
and external scores stay outside the statement-only generation inputs.
