# IMO Proof Pipeline 1.6.0

Reduce each limit-recovery request from 600 to 300 seconds for both Gemma and Qwen, following either a token cap or timeout in primary or budget-forcing calls. Primary physical requests retain their 600-second wall deadline.

Keep the one-retry limit, 65,536-token recovery cap, phase-aware clean-prefix/fresh-input behavior, completed-primary fallback rules, and fail-closed validation. The recovery policy identity records the new allowance. All problems follow this policy; no problem-specific behavior is added.

Generation ends at R1-C2 as in 1.5.0. The Advanced experiment selects this release for P17–P30 after P16 completes under 1.4.0. P16 is unchanged, as explicitly requested. Release 1.5.0 was validated but its pending launch was superseded before activation.
