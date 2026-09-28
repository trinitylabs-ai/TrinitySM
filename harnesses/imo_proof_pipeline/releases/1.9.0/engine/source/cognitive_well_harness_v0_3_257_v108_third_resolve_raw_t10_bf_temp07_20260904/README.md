# Cognitive Well v0.3.257

This preserves v0.3.249's v0.3.108-through-third-resolve experiment while changing
one sampling rule: a raw cold proof-generation call sampled at temperature `1.0`
receives its mandatory budget-forcing continuation at temperature `0.7`.

Raw calls already sampled at `0.7` remain at `0.7`. All review and resolver calls
retain their primary temperature during budget forcing. Model, token cap, schema,
seed, and all other sampling fields remain unchanged.

The original response is preserved, and the forced response remains canonical.
No gold solution, score, Codex feedback, or reference proof is model-visible.

