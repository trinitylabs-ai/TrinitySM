# Basic queue attempts

The repetition-stop/fresh-retry policy was removed on 2026-09-12. New queues
use the original model-call, budget-forcing, and recovery behavior. Neither
Gemma nor Qwen requests receive an automatic repetition detector or
repetition-triggered replacement seed. Old policy run artifacts are retained;
resuming those manifests is rejected to avoid mixing inference policies.

Frontend lane failures remain isolated. A failed raw/check/expansion stage
closes only that candidate; surviving candidates continue through three R1
cycles. The terminal handoff records each actual checkpoint: lazy-checked
proof, raw draft, or no saved proof. Failed checks are never promoted to passes.
A missing proof is unscorable.

For an independent solve attempt, `--raw-seed-offset N` changes the four raw
base seeds by a recorded uint32 offset. Zero preserves the original seeds.
The offset is frozen in the queue manifest. Use a new `--seed-namespace` for
downstream random streams. These settings do not change prompts or include
earlier proofs, scores, or reference feedback.
