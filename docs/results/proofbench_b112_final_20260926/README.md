# Final ProofBench B 1.12.0 — 26 September 2026

Run: `proofbench_B_1_12_0_twice_20260923T032058Z`. Frozen release `1.12.0` (`e8d94232e00c0c3297fbbfa466df7634055ed6aa2876ba1786d94a87858041c9`).

All 60 selections are complete. There are 237 available proofs and 474 independent grading judgments. Three lanes remain missing; no fresh lane retries were launched.

Scores use IMOBench B.5 and gpt-5.6-sol/xhigh. Each available proof has two independent grades; its reported score is their mean. Average first averages the available lanes within each problem, then weights all problems equally. Missing lanes remain null and are excluded from the lane count; the three affected problems each average three proofs. Oracle@4 is the best available grade; Selector@1 is the externally graded, model-selected proof. Selection has no grade or reference access.

| Set | Problems | Graded lanes | Average | Oracle@4 | Selector@1 |
|---|---:|---:|---:|---:|---:|
| Basic | 30 | 119/120 | 78.13% | 82.62% | 81.90% |
| Advanced | 30 | 118/120 | 39.25% | 52.38% | 49.76% |
| Combined | 60 | 237/240 | 58.69% | 67.50% | 65.83% |

## Comparison with the previous run

Both rows of each comparison include all 60 problems and exclude missing lanes from each problem’s average. The previous snapshot has one missing lane and one grade per available proof. The current snapshot has three missing lanes and two grades per available proof. Every problem has equal weight, including those with three available lanes. These are different runs, not a controlled ablation. Previous cross-lane selected scores are unavailable.

| Set | Previous average | Current average | Previous oracle | Current oracle | Current selected |
|---|---:|---:|---:|---:|---:|
| Basic | 80.00% | 78.13% | 84.76% | 82.62% | 81.90% |
| Advanced | 39.29% | 39.25% | 48.10% | 52.38% | 49.76% |
| Combined | 59.64% | 58.69% | 66.43% | 67.50% | 65.83% |

This uses the same available-lane denominator as the historical README matrix. The historical data and table are preserved.

## Every problem and its final selection

Each lane cell shows grade pass 1 / pass 2. Missing means no submitted proof or grade, and is excluded from each problem’s lane average. All summary columns use the mean of the two grades per available proof.

| Problem | t07_r01 | t07_r02 | t10_r01 | t10_r02 | Average | Oracle@4 | Selected lane | Selector@1 |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| PB-Basic-001 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r02](proofs/PB-Basic-001/t07_r02.md) | 7 |
| PB-Basic-002 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r01](proofs/PB-Basic-002/t07_r01.md) | 7 |
| PB-Basic-003 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t10_r01](proofs/PB-Basic-003/t10_r01.md) | 7 |
| PB-Basic-004 | 7/7 | 7/7 | 6/6 | 7/7 | 6.75 | 7 | [t10_r02](proofs/PB-Basic-004/t10_r02.md) | 7 |
| PB-Basic-005 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r01](proofs/PB-Basic-005/t07_r01.md) | 7 |
| PB-Basic-006 | 1/1 | 7/1 | 7/7 | 0/0 | 3 | 7 | [t10_r01](proofs/PB-Basic-006/t10_r01.md) | 7 |
| PB-Basic-007 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | [t10_r01](proofs/PB-Basic-007/t10_r01.md) | 1 |
| PB-Basic-008 | 7/7 | 7/7 | 6/6 | 7/7 | 6.75 | 7 | [t07_r01](proofs/PB-Basic-008/t07_r01.md) | 7 |
| PB-Basic-009 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | [t10_r02](proofs/PB-Basic-009/t10_r02.md) | 1 |
| PB-Basic-010 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t10_r01](proofs/PB-Basic-010/t10_r01.md) | 7 |
| PB-Basic-011 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r02](proofs/PB-Basic-011/t07_r02.md) | 7 |
| PB-Basic-012 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t10_r02](proofs/PB-Basic-012/t10_r02.md) | 7 |
| PB-Basic-013 | 7/7 | 7/7 | 7/7 | 6/7 | 6.875 | 7 | [t10_r02](proofs/PB-Basic-013/t10_r02.md) | 6.5 |
| PB-Basic-014 | 6/7 | 7/7 | 7/7 | 7/7 | 6.875 | 7 | [t07_r02](proofs/PB-Basic-014/t07_r02.md) | 7 |
| PB-Basic-015 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t10_r01](proofs/PB-Basic-015/t10_r01.md) | 7 |
| PB-Basic-016 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r02](proofs/PB-Basic-016/t07_r02.md) | 7 |
| PB-Basic-017 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t10_r01](proofs/PB-Basic-017/t10_r01.md) | 7 |
| PB-Basic-018 | 7/7 | 7/6 | 6/6 | 7/7 | 6.625 | 7 | [t07_r02](proofs/PB-Basic-018/t07_r02.md) | 6.5 |
| PB-Basic-019 | 7/7 | 7/6 | 7/7 | 7/7 | 6.875 | 7 | [t10_r02](proofs/PB-Basic-019/t10_r02.md) | 7 |
| PB-Basic-020 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r02](proofs/PB-Basic-020/t07_r02.md) | 7 |
| PB-Basic-021 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r02](proofs/PB-Basic-021/t07_r02.md) | 7 |
| PB-Basic-022 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | [t10_r02](proofs/PB-Basic-022/t10_r02.md) | 1 |
| PB-Basic-023 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | [t07_r01](proofs/PB-Basic-023/t07_r01.md) | 1 |
| PB-Basic-024 | 7/7 | 1/1 | 7/7 | 6/6 | 5.25 | 7 | [t10_r01](proofs/PB-Basic-024/t10_r01.md) | 7 |
| PB-Basic-025 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r01](proofs/PB-Basic-025/t07_r01.md) | 7 |
| PB-Basic-026 | 0/0 | missing | 0/0 | 1/1 | 0.333333 | 1 | [t10_r02](proofs/PB-Basic-026/t10_r02.md) | 1 |
| PB-Basic-027 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t10_r01](proofs/PB-Basic-027/t10_r01.md) | 7 |
| PB-Basic-028 | 7/6 | 6/6 | 6/6 | 1/6 | 5.5 | 6.5 | [t07_r01](proofs/PB-Basic-028/t07_r01.md) | 6.5 |
| PB-Basic-029 | 0/0 | 1/1 | 1/1 | 0/0 | 0.5 | 1 | [t10_r01](proofs/PB-Basic-029/t10_r01.md) | 1 |
| PB-Basic-030 | 7/7 | 7/6 | 7/7 | 7/6 | 6.75 | 7 | [t10_r02](proofs/PB-Basic-030/t10_r02.md) | 6.5 |
| PB-Advanced-001 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t10_r01](proofs/PB-Advanced-001/t10_r01.md) | 7 |
| PB-Advanced-002 | 1/1 | 6/6 | 1/1 | 1/1 | 2.25 | 6 | [t07_r02](proofs/PB-Advanced-002/t07_r02.md) | 6 |
| PB-Advanced-003 | 1/1 | missing | 1/1 | 0/0 | 0.666667 | 1 | [t10_r01](proofs/PB-Advanced-003/t10_r01.md) | 1 |
| PB-Advanced-004 | 7/7 | 7/7 | 6/6 | 7/7 | 6.75 | 7 | [t07_r02](proofs/PB-Advanced-004/t07_r02.md) | 7 |
| PB-Advanced-005 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | [t07_r01](proofs/PB-Advanced-005/t07_r01.md) | 0 |
| PB-Advanced-006 | 1/0 | 0/0 | 0/0 | 0/0 | 0.125 | 0.5 | [t10_r02](proofs/PB-Advanced-006/t10_r02.md) | 0 |
| PB-Advanced-007 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r01](proofs/PB-Advanced-007/t07_r01.md) | 7 |
| PB-Advanced-008 | 1/1 | 1/1 | 7/7 | 7/6 | 3.875 | 7 | [t10_r02](proofs/PB-Advanced-008/t10_r02.md) | 6.5 |
| PB-Advanced-009 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | [t10_r01](proofs/PB-Advanced-009/t10_r01.md) | 0 |
| PB-Advanced-010 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | [t10_r01](proofs/PB-Advanced-010/t10_r01.md) | 0 |
| PB-Advanced-011 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | [t07_r01](proofs/PB-Advanced-011/t07_r01.md) | 0 |
| PB-Advanced-012 | 6/6 | 6/6 | 6/6 | 6/6 | 6 | 6 | [t07_r02](proofs/PB-Advanced-012/t07_r02.md) | 6 |
| PB-Advanced-013 | 7/7 | 0/0 | 1/1 | 1/1 | 2.25 | 7 | [t07_r01](proofs/PB-Advanced-013/t07_r01.md) | 7 |
| PB-Advanced-014 | 6/6 | 6/6 | 1/1 | 7/7 | 5 | 7 | [t10_r02](proofs/PB-Advanced-014/t10_r02.md) | 7 |
| PB-Advanced-015 | missing | 1/1 | 0/0 | 1/0 | 0.5 | 1 | [t10_r02](proofs/PB-Advanced-015/t10_r02.md) | 0.5 |
| PB-Advanced-016 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | [t07_r01](proofs/PB-Advanced-016/t07_r01.md) | 0 |
| PB-Advanced-017 | 6/6 | 6/7 | 7/7 | 7/7 | 6.625 | 7 | [t10_r01](proofs/PB-Advanced-017/t10_r01.md) | 7 |
| PB-Advanced-018 | 1/1 | 0/0 | 0/0 | 0/0 | 0.25 | 1 | [t07_r02](proofs/PB-Advanced-018/t07_r02.md) | 0 |
| PB-Advanced-019 | 7/7 | 7/6 | 7/7 | 7/7 | 6.875 | 7 | [t10_r02](proofs/PB-Advanced-019/t10_r02.md) | 7 |
| PB-Advanced-020 | 7/6 | 0/0 | 0/0 | 0/0 | 1.625 | 6.5 | [t07_r01](proofs/PB-Advanced-020/t07_r01.md) | 6.5 |
| PB-Advanced-021 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | [t10_r01](proofs/PB-Advanced-021/t10_r01.md) | 1 |
| PB-Advanced-022 | 7/7 | 1/1 | 7/7 | 7/7 | 5.5 | 7 | [t10_r02](proofs/PB-Advanced-022/t10_r02.md) | 7 |
| PB-Advanced-023 | 0/0 | 0/0 | 1/0 | 1/1 | 0.375 | 1 | [t07_r01](proofs/PB-Advanced-023/t07_r01.md) | 0 |
| PB-Advanced-024 | 1/1 | 0/0 | 1/1 | 0/0 | 0.5 | 1 | [t07_r02](proofs/PB-Advanced-024/t07_r02.md) | 0 |
| PB-Advanced-025 | 7/6 | 7/7 | 7/7 | 6/6 | 6.625 | 7 | [t10_r01](proofs/PB-Advanced-025/t10_r01.md) | 7 |
| PB-Advanced-026 | 0/0 | 1/1 | 1/1 | 1/0 | 0.625 | 1 | [t07_r01](proofs/PB-Advanced-026/t07_r01.md) | 0 |
| PB-Advanced-027 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | [t07_r01](proofs/PB-Advanced-027/t07_r01.md) | 0 |
| PB-Advanced-028 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | [t07_r02](proofs/PB-Advanced-028/t07_r02.md) | 7 |
| PB-Advanced-029 | 1/1 | 7/7 | 7/7 | 1/1 | 4 | 7 | [t10_r01](proofs/PB-Advanced-029/t10_r01.md) | 7 |
| PB-Advanced-030 | 0/0 | 0/0 | 0/0 | 0/0 | 0 | 0 | [t07_r02](proofs/PB-Advanced-030/t07_r02.md) | 0 |

## Selection recovery and quality

The selector chose a best-scoring available proof or tie on 50/60 problems. No selected 0–1 proof displaced an available 6–7 proof. Four misses selected 6.5 over 7; six misses were entirely within 0–1.

Basic-016: `Winner: Proof A` became `Winner: A` by deleting only the literal prefix. Advanced-003: the missing Decisive checks heading was restored by copying its existing line-cited checks verbatim; no mathematical text or winner was invented. Advanced-002: only the 12 Qwen comparisons that failed with connection refused were rerun; 12 valid Gemma votes were retained. Earlier saved-response formatting recoveries are also recorded per vote.

The [comparison recovery guide](../../comparison_format_recovery.md) documents all three saved-response format policies. The Advanced-003 receipt does not claim a hash binding to an unpublished repair script: `--verify` replays the recorded v2 operation from the original response using the same implementation as the current recovery monitor, and checks the normalized bytes and receipt. Frozen historical v1 sources remain unchanged.

Native failures and generation return codes are preserved in the scorecard. A completed final selection can use earlier eligible proofs where refinement failed. The three missing lanes failed before producing a proof. Advanced-003’s current selection is among three available proofs.

## Generation timing

`generation_minutes` is recorded elapsed wall-clock time, not active GPU compute time. The timer continued across the GPU pause for resumed problems; interrupted runs retain their partial elapsed time. These values are not comparable across problems and must not be averaged to estimate proof-generation cost. The scorecard records this limitation in `generation_timing`.

## Portable evidence and verification

[SCORECARD.json](SCORECARD.json) records each run, checkpoint, proof hash, both grades, every comparison, model/order presentation, deterministic tie order and source record hashes. [lanes.csv](lanes.csv) contains all 240 allocated lanes. `proofs/`, `grades/` and `votes/` contain the exact proof and response evidence; original external references remain outside the solver inputs.

```bash
python3 -B scripts/export_proofbench_final.py --verify
```

Verification uses published files and the Python standard library; it makes no model, network or grading calls.
