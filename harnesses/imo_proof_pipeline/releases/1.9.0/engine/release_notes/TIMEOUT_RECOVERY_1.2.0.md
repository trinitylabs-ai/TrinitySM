# Timeout recovery in IMO Proof Pipeline 1.2.0

Capture streamed text and token IDs for all physical inference calls. Enforce a
600-second wall deadline (or a shorter explicitly configured timeout), including
when tokens continue to arrive. Preserve partial streams and hashes on timeout.

On timeout, inspect reasoning before final content for a terminal repetition.
Use the inherited word-period detector plus a character-period detector that
catches unseparated loops such as repeated `!`: at least eight periods spanning
128 characters, with periods up to 512 characters. Keep only output through the
last newline before the repetition starts; a reasoning loop discards later final
content. Retry once with the complete original input conversation plus that clean
output prefix. With an empty prefix, retry the original input conversation alone.
Keep the original seed, sampling settings, and token allowance. A second timeout
with repetition fails closed. This adds no early live stopper.

A timeout without repetition may use a completed, nonempty, nonrepetitive response
saved before budget forcing. The existing stage parser and schema remain required;
an invalid fallback fails closed. A capped or absent primary is ineligible.
Record this exception explicitly as `pre_budget_forcing_timeout_fallback`, retain
the original raw response, and bind it to the timed-out stream evidence. Never
label this exception as a successful forced response. If there is no eligible
primary, fail closed. Terminal timeout decisions bypass inherited generic retries.

Existing token-cap recovery, model roles, MTP=4, ordinary prompts, four candidates,
seed settings, and R1-C3 terminal stage are preserved. Streaming observations and
timeout recovery change execution behavior, requiring a new minor release.
The old 1.1.0 snapshot remains immutable. The Advanced queue transitions after P12:
P13–P30 use a new 1.2.0 experiment; previous proofs and grades retain their identity.
