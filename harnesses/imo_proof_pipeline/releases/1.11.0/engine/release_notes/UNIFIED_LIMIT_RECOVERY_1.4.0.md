# Unified limit recovery in IMO Proof Pipeline 1.4.0

Gemma and Qwen share one policy for both output-token exhaustion
(`finish_reason=length`) and the 600-second wall timeout. Initial stage token
allowances remain unchanged: Qwen starts at 49,152; Gemma keeps its existing
initial stage allowances. The first limit stop is handled by request phase:

| First limit stop | Action |
|---|---|
| Repetition, in either phase | One retry with the complete original input plus the clean output prefix |
| No repetition, primary/pre-budget-forcing | One fresh request with the original input only |
| No repetition, budget forcing, completed eligible primary available | Use the primary, subject to existing stage validation |
| No repetition, budget forcing, no eligible primary | Fail closed |

Both recovery types receive 65,536 new output tokens and a 600-second wall
allowance. Preserve the original seed and sampling settings. Fresh means a new
request with no output from the limited attempt added to its input; it does not
change the seed. Clean-prefix recovery preserves the entire original input
conversation and only output through the last newline before repetition starts.
A reasoning loop discards later final content. With an empty clean prefix, retry
the original input alone. Detection uses the existing word/character-period rules.

**If the recovery request hits either limit, fail closed immediately.** This rule
holds even without repetition and even if a completed primary exists. No third
request, fallback, or reset of the retry allowance is permitted after that stop.
A transport or format failure during recovery also fails closed. Each original
physical request has its own one-recovery allowance: the primary phase and the
normal budget-forcing phase remain separate. A successful recovered primary
proceeds to the normal budget-forcing request; it does not itself skip that phase.

A fallback primary must have completed with `finish_reason=stop`, contain a
nonempty, nonrepetitive final response, and pass the existing stage parser/schema.
A parseable truncated response is insufficient. Record a fallback explicitly as
`pre_budget_forcing_limit_fallback`; never label it a completed forced response.

The shared transport intercepts all token-limit stops before the old Gemma and
Qwen cap ladders. Those stage-specific cap recovery branches no longer handle
live limited responses. Ordinary non-limit protocol recovery remains unchanged.
Both limits share the one retry allowance. No early live repetition stopper is
added. Partial streams, token IDs, original configurations, decisions, retry
prefixes and response hashes are retained and validated by producer checks.
Recovery evidence is kept separately for primary and budget-forcing phases.

Release 1.3.0 was registered but never activated. This release supersedes its
separate Qwen cap policy. The Advanced handoff remains explicitly held at the
user's request: P13 continues under 1.2.0, and P14 must not launch until released
by the user. Registering this release does not authorize that handoff.
