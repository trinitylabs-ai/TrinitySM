# B 1.11.0: choose a final proof across audited lanes

After the unchanged R2/R3 preservation audit, compare every pair of available
lane finals independently in both presentation orders with both Gemma and Qwen.
Four lanes use 24 logical calls: twelve concurrent calls per model. Use the tested
Markdown prompt, original reasoning-plus-answer chat BF, temperature 0.2 and
original role caps/recovery. Every valid call chooses A or B; pool votes and
break total-score ties using the candidate order recorded before inference.

Keep all lane proofs. Export a separate winning proof only with a complete valid
vote set. Save prompts, reasoning, responses, BF, source bindings, the complete
vote table and order-disagreement rates. Collection revalidates actual responses;
resume never repeats completed or interrupted comparisons. Missing calls yield
an incomplete selection, never a fabricated winner. One available lane wins
without calls; two or three lanes use the corresponding complete round robin.
No grades or reference solutions enter solver inputs.

B 1.10.0 generation, draft temperature 0.4, refinement and R2/R3 audit settings
remain. All prior immutable releases are retained byte-for-byte. This minor
release records the new source/profile behavior; integration uses scripted tests.
