# IMO Proof Pipeline 1.7.0

Set each limit-recovery request to 450 seconds for Gemma and Qwen, following either a token cap or timeout in primary or budget-forcing calls. Initial physical requests retain their 600-second wall deadline.

Keep the one-retry limit, 65,536-token recovery cap, phase-aware clean-prefix/fresh-input behavior, completed-primary fallback rules, and fail-closed validation. Generation ends at R1-C2. No problem-specific behavior, prompts, seeds, or mathematical guidance are added.

The Advanced queue selects this release for P17–P30 after P16 completes under 1.4.0 with its original settings. Releases 1.5.0 and 1.6.0 were validated but superseded before activation.
