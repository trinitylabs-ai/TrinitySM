# TrinitySM environment and reproduction record

For executable setup, local model serving and proof generation without Codex or
hosted inference, use [the reproduction guide](docs/local_reproduction.md).
[Model downloads](docs/models.md) use the exact revisions recorded below.
Machine paths in historical records are sanitized; see
[public-copy provenance](docs/reproduction/sanitization.md).

This document describes the **historical Advanced experiment**, run ID
`advanced001_030_v263_v290_frozen_run01`. It started at
**2026-09-13 01:56:17.958785 UTC**. The environment observation was collected at
**2026-09-13 04:44:55.507057 UTC**, during the run; earlier launch records are
identified separately. It is not a complete start-time snapshot reconstructed
after the fact.

The [experiment ENVIRONMENT.md](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/ENVIRONMENT.md)
contains the detailed tables and links to the
[machine-readable snapshot](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/environment.json).
Historical Basic and IMO 2026 experiments retain their own saved manifests;
this recorded configuration must not be assigned to other runs. New runs default
to [B 1.12.0](harnesses/imo_proof_pipeline/releases/1.12.0/profile.json);
its current settings, including expansion at 0.4, are documented in the
[local reproduction guide](docs/local_reproduction.md).

## Hardware and system

| Item | Recorded value |
|---|---|
| GPUs | 2 × NVIDIA RTX PRO 6000 Blackwell Workstation Edition |
| VRAM | 97,887 MiB per GPU, as reported by NVIDIA |
| CPU | Intel Core i9-7920X, 12 cores / 24 threads, nominal 2.90 GHz |
| RAM | 131,568,460 KiB reported by Linux, approximately 125.47 GiB |
| NUMA | One NUMA node; both GPUs have CPU affinity 0–23 |
| GPU interconnect | `NODE`: PCIe through host bridges within the same NUMA node; no NVLink link reported |
| PCI bus IDs | GPU0 `0000:19:00.0`; GPU1 `0000:68:00.0` |
| OS / kernel | Ubuntu 22.04.5 LTS; Linux `6.8.0-110-generic`, x86_64 |
| NVIDIA driver | `595.71.05` |
| CUDA build / runtime package | PyTorch CUDA build `13.0`; installed `nvidia-cuda-runtime==13.0.96` |
| cuDNN package | `nvidia-cudnn-cu13==9.19.0.56` |
| Container | Host Conda processes; container detection reports `none`. No container image or image digest was used/recorded. |

[PCI link observations](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/recorded_launch/pci_link_observation.json)
also record negotiated width and instantaneous speed. Both links reported x8;
instantaneous speed varies with GPU power state and should not be interpreted
as the GPU's maximum link capability.

## Software: serving and harness environments are different

| Process | Python environment | Python | vLLM | PyTorch | Transformers |
|---|---|---|---|---|---|
| Gemma server | `miniconda3/envs/gemma4-vllm024` | 3.11.15 | **0.24.0** | 2.11.0+cu130 | 5.12.1 |
| Qwen server | `miniconda3/envs/gemma4-vllm024` | 3.11.15 | **0.24.0** | 2.11.0+cu130 | 5.12.1 |
| Solver HTTP client | `miniconda3/envs/math` | 3.11.15 | 0.20.1 installed; does not serve these models | 2.11.0+cu130 installed | 5.8.0 |
| Independent grading watcher | Advanced scorer's separate `.venv` | 3.13.12 | Not installed | Not installed | Not installed |

Serving vLLM reports build commit **`gee0da84ab`**. PyTorch reports source commit
`70d99e998b4955e0049d13a98d77ae1b14db1f45`. Tokenizers is `0.22.2` in both
generation environments. The observed Codex client is `0.153.4`; this observation
does not establish its version on every older grading date.

Installed-version dependency locks and build metadata:

- [Gemma server lock](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/software/gemma/requirements.freeze.txt)
- [Qwen server lock](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/software/qwen/requirements.freeze.txt)
- [Solver lock](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/software/solver/requirements.freeze.txt)
- [Grading watcher lock](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/software/grader/requirements.freeze.txt)

These pin installed distribution versions, with build constants separately in
each `packages.json`. They are not a wheel-hash lock or a container image.
For example, PyTorch's distribution metadata says `2.11.0`, while its installed
build identifies itself as `2.11.0+cu130`; both facts are preserved.

Both servers use the captured
[sitecustomize compatibility patch](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/vllm_sitecustomize.py)
via `PYTHONPATH`. It patches excluded tied output-head quantization handling and
loopback TCPStore setup. Preserve its bytes and the recorded environment
variables when reproducing the serving setup.

## Checkpoints, tokenizers and chat templates

| Role | Repository | Revision |
|---|---|---|
| Gemma | `google/gemma-4-31B-it` | `842da3794eaa0b77d5f08bae87a17459d91ff475` |
| Gemma MTP assistant | `google/gemma-4-31B-it-assistant` | `627c5ec1458b9086b841a91e0512fd31fd2fbbf1` |
| Qwen | `Qwen/Qwen3.6-27B` | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` |

The servers load explicit local Hugging Face snapshot paths. Each uses its
snapshot's tokenizer and `chat_template.jinja`, with
`{"enable_thinking": true}`. There is no tokenizer or chat-template path override
in the recorded launch commands. Configs, generation defaults and chat templates
are copied under [models/](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/models).
Tokenizer files have SHA-256 inventories. Weight files are identified by pinned
repository revision, filenames, sizes and HF cache LFS blob IDs; the large
weights were not reread for hashing during the active experiment.

## Serving: Gemma and Qwen run concurrently on separate GPUs

| Setting | Gemma | Qwen |
|---|---|---|
| Physical GPU | GPU0 exclusively for this model server | GPU1 exclusively for this model server |
| Endpoint | `http://127.0.0.1:8030/v1` | `http://127.0.0.1:8027/v1` |
| Weight precision / quantization | BF16 / none | BF16 / none |
| Attention KV-cache dtype | BF16 | BF16 |
| Recurrent-state cache | Not applicable to this recorded Gemma cache | **FP32**, requested by checkpoint `mamba_ssm_dtype` |
| Tensor / pipeline / data parallel sizes | 1 / 1 / 1 | 1 / 1 / 1 |
| Maximum context | 262,144 tokens | 196,608 tokens |
| Maximum scheduled sequences | 8 | 4 |
| Maximum batched tokens | 8,192 | 8,192 |
| GPU memory utilization setting | 0.95 | 0.90 |
| Prefix caching, resolved | **Enabled** | **Disabled** |
| Speculative decoding | MTP, 4 tokens, separate Gemma assistant checkpoint | MTP, 4 tokens, Qwen's own MTP layers |
| Reasoning parser | `gemma4` | `qwen3` |
| Thinking / async scheduling | Enabled / enabled | Enabled / enabled |

Both servers stay loaded simultaneously. Each pipeline problem has four lanes
and four workers per endpoint; calls to the two models can overlap across lanes.
During Gemma-only raw generation, Qwen can be idle. This is not a single model
split across two GPUs. CPU, RAM and storage are shared.

Qwen's prefix caching is disabled by vLLM 0.24.0's default for hybrid
attention/recurrent architectures: support is marked experimental. The launcher
does not explicitly disable it. Its FP32 recurrent-state cache stores a running
state for the recurrent layers; it is separate from the BF16 attention KV cache.
There is no `BF32` cache setting here.

Exact observed commands, including environment variables:

- [Gemma launch](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/launch_gemma.sh)
- [Qwen launch](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/observed_20260913/launch_qwen.sh)
- [Original Advanced solver launch](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/recorded_launch/launch_solver.sh)
- [Original independent grading launch](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/recorded_launch/launch_scoring.sh)
- [Qwen startup configuration](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/recorded_launch/qwen_startup_config.txt)

These are historical launch records with sanitized output paths.
Use a fresh run ID through the experiment launcher below for a new experiment.

## Harness, generation settings and stopping criteria

The recorded run used the Workshop Draft and Workshop Refine implementations
preserved in the historical [A 1.7.0 release inventory](harnesses/imo_proof_pipeline/releases/1.7.0/release.json).
The [official controller](harnesses/proof_workshop/README.md) runs all three
refinement passes automatically. Saved Advanced run manifests retain their
original identities; that run was not restarted through the public controller.

| Stage | Model | Temperature | top-p / top-k | Primary output cap |
|---|---|---|---|---|
| Four raw drafts | Gemma | 1.0, 1.0, 0.7, 0.7 | 0.95 / 64 | 65,536 |
| Lazy check | Gemma | 0.1 | 0.95 / 64 | 16,384 |
| Conditional in-place expansion | Gemma | 0.7 | See actual request metadata | 65,536 |
| Reviewer 1 and trace/gap selection | Gemma | 0.1 | 1.0 / -1 | 32,768 |
| Reviewer 2 | Qwen | 0.2 | 1.0 / -1 | 49,152 |
| Reviewer 3 | Gemma | 0.2 | 1.0 / -1 | 32,768 |
| Fusion / Resolver 1 | Gemma | 0.4 | 1.0 / -1 | 32,768 |
| Fusion acceptance / repair-brief audit | Qwen | 0.2 | 1.0 / -1 | 49,152 |

The [profile](harnesses/imo_proof_pipeline/releases/1.7.0/profile.json) records
base seeds `2360094352`, `2367214500`, `3233582896`, `220229344`. The native
harness derives actual call seeds. Use the same problem IDs, namespace
`v263-v290:problem-only`, raw seed offset `0`, source and candidate settings;
do not substitute base seeds for derived request seeds. The archived
[generation request records](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/environment/recorded_launch/generation_requests.jsonl)
preserve actual seeds, sampling settings, prompt hashes, token usage and timings
for the two completed problems at documentation time.

Extended reasoning is mandatory: one semantic continuation supplies a complete
replacement response, including after an initial stop. Raw temperature 1.0
continues at 0.7; the continuation cap floor is 32,768. Raw/lazy cap recovery and
format recovery follow the frozen engine. Qwen requests are capped at 49,152
tokens, with no output-cap retry. Thinking is enabled; request metadata records
any stage-specific reasoning-effort value.

The pipeline performs raw generation, lazy checking, conditional refinement,
then **Refinement 1, Refinement 2 and Refinement 3**, each comprising review,
fusion, audit and revision. The official public script stops after the third pass. Acceptance reconsideration and brief rewrites have the
recorded two-round limits. Rejected mathematical briefs can proceed as advisory
context after the configured rewrites; mechanical/provenance errors remain failures.
The global repetition fresh-retry policy is absent; original review/trace
repetition checks remain. Failed lanes retain their actual checkpoints while
surviving lanes continue; a wholly failed problem pauses the queue for its
existing explicit validated skip policy. Grading never controls generation.

## External grading API

The [grading API record](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/grading/external_api.json)
and [saved per-attempt commands](benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/grading/api_requests)
record:

| Item | Value |
|---|---|
| Provider | OpenAI / Codex hosted service, using the default client provider; raw HTTP routing was not captured |
| Exact requested model ID | `gpt-5.6-sol` |
| Reasoning effort | `xhigh` |
| Interface | `codex exec`, independent isolated call per proof; tool use disabled |
| Local grader concurrency | 4 |
| Request timeout / attempts | 1,200 seconds / at most 2 attempts |
| Temperature, top-p, seed, output token cap | Not explicitly set; resolved provider defaults were not recorded |
| Current Advanced evaluation date | 2026-09-13 UTC; exact attempt timestamps and reuse chains are retained |
| Provider hardware / underlying checkpoint revision | Unavailable / not exposed |

The Advanced grader uses the published IMOBench ProofAutoGrader policy
`imobench-proof-autograder-b5-v1`, scores **0/1/6/7**, and official per-problem
guidelines/reference answers. Rubric, problem/reference/guideline hashes and full
grading prompts are archived. Historical strict Olympiad grades use their
separate 0–7 policy; they are not relabeled as IMOBench grades.

Scoring runs outside the harness, with GPUs hidden, after each entire problem
worker exits. Only the raw draft before lazy checking and the final refinement output are selected. Reused grades retain
the originating API call rather than treating the archive date as an evaluation
date. The external model identifier does not guarantee a fixed provider backend
or identical future grades.

## Runtime measurement and reproducibility limits

Use wall time from problem/worker start to its terminal state, including model
requests, extended reasoning, retries and pipeline orchestration. Server startup,
model loading, environment capture and independent grading are separate timings.
The new experiment launcher explicitly records worker wall time and its boundaries.
Native request metadata records latency and token usage; primary and continuation
records must be distinguished to avoid double counting, and overlapping requests
cannot be summed into wall time.

Servers are persistent. Prefix caches, compilation caches, scheduling and GPU
power states can affect runtime. Gemma was already running before Advanced;
Qwen was restarted for Advanced. The exact start-time cache contents were not
recorded or reset. The observation captures resolved cache settings, not those
earlier contents. Matching seeds and configuration supports controlled comparisons
but does not establish bitwise deterministic scheduling, decoding or external grading.

## Automatic snapshots for future experiments

The official command is documented in [local reproduction](docs/local_reproduction.md).
For explicit environment capture options, use [benchmarks/run_experiment.py](benchmarks/run_experiment.py):

```bash
python -B benchmarks/run_experiment.py \
  --benchmark imo-proofbench/advanced \
  --run-id workshop_advanced_001 \
  --release 1.12.0 \
  --solver-python .venv-solver/bin/python \
  --grader-python /path/to/separate/grading/environment/bin/python \
  --execute-models
```

The launcher creates `benchmarks/<benchmark>/results/<run_id>/`, saves a
human-readable `ENVIRONMENT.md`, package locks, checkpoint/template inventories,
server commands, code/profile hashes and experiment identity **before starting
the complete public pipeline**. Snapshot failure prevents generation. A dry run
uses `--dry-run`; it records the local system/software while leaving server
settings explicitly unobserved. Supply `--container-image` and
`--container-digest` when running in a known container.

Every indexed artifact gets the same run ID, a stable path-based artifact ID,
content hash and category in `artifact_index.jsonl`. Proof, score, verification
and timing files are associated through this sidecar without rewriting native
harness or grader records. The index is written when the generation worker
exits. After separately publishing new scores under `grades/`, refresh it with:

```bash
python -B benchmarks/run_experiment.py \
  --benchmark imo-proofbench/advanced \
  --run-id workshop_advanced_001 \
  --index-only
```

It excludes live grading work, symlink targets and active generation output.
Keep grading request/provider/date records beside the published grades. Existing
historical runs retain their original paths and resume commands. The new launcher
creates fresh experiments; resume the native recorded command with its existing
`--resume` contract and capture any changed environment separately.
