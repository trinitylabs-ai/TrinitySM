# Qwen token-cap recovery in IMO Proof Pipeline 1.3.0

Qwen's initial physical output allowance remains 49,152 tokens. A response that
stops with `finish_reason=length` now enters the same repetition/preserved-primary
decision used for timeouts. Inspect reasoning and final output using both word-
and character-period detectors. On repetition, retry once with the complete
original input conversation plus output through the last newline before the loop.
The retry allows 65,536 new output tokens; the preserved prefix is input. A loop
beginning before any newline retries the original input alone. A reasoning loop
discards any later final content. Seed and sampling parameters are preserved.

Without repetition, use only a completed, nonempty, nonrepetitive response saved
before budget forcing, subject to the existing stage parser/schema. A capped,
missing or malformed primary is ineligible. Otherwise fail closed. Capped primary
calls without repetition fail immediately because no completed pre-forcing
response exists yet. An eligible primary fallback is explicitly identified as
`pre_budget_forcing_token_cap_fallback`; it is never called a forced response.

Every physical request retains the 600-second wall deadline. Token-cap and timeout
repetition recovery share one retry allowance per physical request: crossing from
one limit to the other cannot reset it. A second repetitive limit stop fails closed.
A retry that stops at either limit without repetition may use an eligible saved
primary. Transport or format failure in token-cap recovery fails closed rather
than starting the generic format/transport retry loop. Primary and budget-forcing
requests have separate physical retry evidence directories.

Record capped physical responses, hashes, repetition offsets, clean-prefix hashes,
actual retry allowances, and fallback provenance. Existing producer checks validate
these artifacts before accepting the 65,536-token exception or a primary fallback.
The initial 49,152-token model override is retained; only the physical recovery
request gets the higher allowance. Existing Gemma cap recovery and ordinary
budget forcing remain in place. The old 1.2.0 release remains immutable.

The Advanced queue transitions after P13 to a new experiment for P14–P30. Grading
continues outside generation using the same official Advanced rubric/guidelines.
