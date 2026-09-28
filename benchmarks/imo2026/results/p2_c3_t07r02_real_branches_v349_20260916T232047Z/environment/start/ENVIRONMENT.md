# Environment — p2_c3_t07r02_real_branches_v349_20260916T232047Z

Captured **2026-09-16T23:22:54.276522+00:00**; phase **before_generation**.

[Full configuration](environment.json) · [Launch scripts](./) · [Dependency locks](software) · [Hashes](SHA256SUMS.json)

## Hardware and system

- OS: Ubuntu 22.04.5 LTS; kernel: `Linux jihun-System-Product-Name 6.8.0-110-generic #110~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar 27 12:43:08 UTC  x86_64 x86_64 x86_64 GNU/Linux`.
- CPU: Intel(R) Core(TM) i9-7920X CPU @ 2.90GHz; 24 logical CPUs.
- RAM: 125.47 GiB as reported by Linux.
- Container detection: `none`; image: `None`; digest: `None`. Missing values are not inferred.

GPU index, model, UUID, VRAM (MiB), NVIDIA driver, PCI bus:

```text
0, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, GPU-26a733fc-0175-46d2-eaa7-e8a57ef90515, 97887 MiB, 595.71.05, 00000000:19:00.0
1, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, GPU-c7164293-2ae3-639e-d08c-a0ecec50faad, 97887 MiB, 595.71.05, 00000000:68:00.0
```

GPU interconnect/topology:

```text
GPU0	GPU1	CPU Affinity	NUMA Affinity	GPU NUMA ID
GPU0	 X 	NODE	0-23	0		N/A
GPU1	NODE	 X 	0-23	0		N/A

Legend:

  X    = Self
  SYS  = Connection traversing PCIe as well as the SMP interconnect between NUMA nodes (e.g., QPI/UPI)
  NODE = Connection traversing PCIe as well as the interconnect between PCIe Host Bridges within a NUMA node
  PHB  = Connection traversing PCIe as well as a PCIe Host Bridge (typically the CPU)
  PXB  = Connection traversing multiple PCIe bridges (without traversing the PCIe Host Bridge)
  PIX  = Connection traversing at most a single PCIe bridge
  NV#  = Connection traversing a bonded set of # NVLinks
```

## Software

| Environment | Python | PyTorch | vLLM | Transformers |
|---|---|---|---|---|
| gemma | 3.11.15 | 2.11.0+cu130 | 0.24.0 | 5.12.1 |
| qwen | 3.11.15 | 2.11.0+cu130 | 0.24.0 | 5.12.1 |
| solver | 3.11.15 | 2.11.0+cu130 | 0.20.1 | 5.8.0 |
| grader | 3.10.12 | 2.10.0+cu128 | 0.17.1 | 4.57.6 |

Build commits and CUDA runtime package versions are in each `software/<role>/packages.json`. `requirements.freeze.txt` pins installed distribution versions; it does not contain wheel hashes, system driver packages, or a container image. The model weights are separately identified by repository revisions and HF cache blob IDs, without rereading all weights during a live run.

## Separate serving configurations

### gemma

| Setting | Value |
|---|---|
| GPU visibility | `0` |
| Model | `google/gemma-4-31B-it` |
| Weight dtype | `bfloat16` |
| Weight quantization CLI | `unset; inspect pinned model config` |
| KV-cache dtype | `bfloat16` |
| Recurrent-state dtype | `auto` |
| Maximum context | `262144` |
| Maximum sequences | `8` |
| Batched token limit | `8192` |
| Prefix caching | `True` |
| Parallelism | `{'tensor_parallel_size': 1, 'pipeline_parallel_size': 1, 'data_parallel_size': 1}` |
| Speculative decoding | `{'method': 'mtp', 'model': '/home/user/.cache/huggingface/hub/models--google--gemma-4-31B-it-assistant/snapshots/627c5ec1458b9086b841a91e0512fd31fd2fbbf1', 'num_speculative_tokens': 4}` |
| Chat template kwargs | `{'enable_thinking': True}` |
| Asynchronous scheduling | `True` |

[Exact launch command](launch_gemma.sh).

### qwen

| Setting | Value |
|---|---|
| GPU visibility | `1` |
| Model | `Qwen/Qwen3.6-27B` |
| Weight dtype | `bfloat16` |
| Weight quantization CLI | `unset; inspect pinned model config` |
| KV-cache dtype | `bfloat16` |
| Recurrent-state dtype | `float32` |
| Maximum context | `196608` |
| Maximum sequences | `4` |
| Batched token limit | `8192` |
| Prefix caching | `False` |
| Parallelism | `{'tensor_parallel_size': 1, 'pipeline_parallel_size': 1, 'data_parallel_size': 1}` |
| Speculative decoding | `{'method': 'mtp', 'num_speculative_tokens': 4}` |
| Chat template kwargs | `{'enable_thinking': True}` |
| Asynchronous scheduling | `True` |

[Exact launch command](launch_qwen.sh).

Both recorded servers coexist. Compare their GPU visibility values to determine whether they share GPUs; concurrency varies by pipeline stage. Their prefix caches and compilation state are not reset by capture.

## Model and tokenizer revisions

| Role | Repository | Revision |
|---|---|---|
| gemma | google/gemma-4-31B-it | `842da3794eaa0b77d5f08bae87a17459d91ff475` |
| gemma_mtp_assistant | google/gemma-4-31B-it-assistant | `627c5ec1458b9086b841a91e0512fd31fd2fbbf1` |
| qwen | Qwen/Qwen3.6-27B | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` |

Tokenizer/chat-template file hashes, generation defaults, and checkpoint file inventories are in `environment.json` and `models/`. Explicit tokenizer/template overrides appear in server argv.

## Harness and generation policy

Release: **1.7.0**, digest `1374943fba9e8a39a734160565b926a5b3c869d79ea0b80ed8e5deebd34685b2`. The pinned `profile.json` records model roles, temperatures, base seeds, caps, budget forcing, three R1 cycles and stopping policies; `release.json` hashes the complete source/prompt inventory. Actual derived seeds and per-request settings remain in native generation metadata.

## External grading and runtime

Record the actual grading provider, model ID, parameters and evaluation timestamps under the experiment’s `grading/` directory. Local GPU details do not describe external provider hardware. The environment observation time is not a grading date.

Measure solver wall time from worker launch to worker exit, excluding environment capture and grading. Native request metadata separates call latency, usage, and budget-forcing continuation; parallel call latencies cannot simply be summed to obtain experiment wall time. Historical or retrospective snapshots do not establish the cache state or package state at an earlier launch.
