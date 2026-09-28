# Harness B 1.9.0: original expansion at 0.4 and R2/R3 audit

Derived from immutable B 1.8.0. Draft keeps its original lazy-check and whole-proof
expansion prompts and chat BF; lazy-check stays at 0.1, expansion and its BF use 0.4.
Raw generation, seeds, three refinement passes and B role-specific BF remain.
After R3, Gemma and Qwen each independently audit both presentation orders at 0.2.
Four logical calls run concurrently across eligible lanes. All four valid approvals
are required to adopt a changed R3 proof; otherwise export the completed R2 proof.
Identical proof text needs no calls. Mechanical V2 validation binds actual proof,
request and response bytes, with copied model hashes diagnostic only. Invalid or
interrupted audits retain R2. Collection revalidates saved calls without inference.
This audit is at the tested R2-to-R3 boundary only; it adds no repair-model calls.
All original proofs, model responses, audit votes, BF records and selected-stage
provenance are retained. Grades and references never enter audit inputs.
The five observed 0/1-vs-6/7 cases all selected the higher band; this small
retrospective diagnostic is not a fresh end-to-end performance claim.
A 1.7.0 and original B 1.8.0 remain unchanged and runnable.
