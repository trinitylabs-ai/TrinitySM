Bound token-cap recovery and resume from a clean repetition prefix.

Gemma cap retries double the capped physical request's allowance, up to 65,536
output tokens. A raw request already at 65,536 retries at 65,536. A lazy request
whose budget-forcing pass capped at 32,768 retries at 65,536. Later Gemma recovery
rungs are 32,768 → 65,536 → 65,536, within the inherited attempt limits.
Qwen retains its 49,152 output cap and disabled output-cap retry.

After a length stop, inspect reasoning before final content for a terminal exact
word-period loop: at least four copies, at least 256 repeated characters, periods
up to 256 whitespace-separated words. One incomplete trailing word is allowed
only when it is a strict prefix of the expected word. Whitespace differences are
ignored for detection. This catches exact periodic tails, not every semantic or
irregular repetition. No problem-specific strings, answer data or live stopper.

Keep output only through the newline before the first repeated block. A loop in
reasoning also discards final content occurring after it. Feed the original task
plus this prefix to recovery and to the existing mandatory budget-forcing pass.
When no prefix remains, frontend recovery uses the original task alone. Non-loop
raw cap recovery retains its partial output; non-loop lazy recovery retains the
inherited full restart. This does not reintroduce the retired global fresh-retry
policy or change repetition_penalty, MTP, ordinary prompts, primary seeds, model
roles, or the terminal R1-C3 checkpoint.

Physical responses remain intact for audit. Trim offsets, hashes and retry caps
are saved separately and in metadata; capped results expose the clean prefix to
inherited recovery callers. The original immutable 1.0.0 snapshot is retained.
New experiments capture current environment and launch parameters before starting.
The copied upstream environment inventory describes its historical capture only.
