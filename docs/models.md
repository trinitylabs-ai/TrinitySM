# Models and downloads

TrinitySM distributes code, generated proofs and selected configuration
files. It distributes **no model weights**. Download the following revisions
directly from the providers when setting up local generation.

| Role | Official repository | Pinned revision |
|---|---|---|
| Proof generation, reviews and revisions | [google/gemma-4-31B-it](https://huggingface.co/google/gemma-4-31B-it) | `842da3794eaa0b77d5f08bae87a17459d91ff475` |
| Gemma MTP assistant | [google/gemma-4-31B-it-assistant](https://huggingface.co/google/gemma-4-31B-it-assistant) | `627c5ec1458b9086b841a91e0512fd31fd2fbbf1` |
| Additional reviews and audits | [Qwen/Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` |

These revisions come from [ENVIRONMENT.md](../ENVIRONMENT.md) and are recorded
for scripts in [workshop_models.json](../configs/workshop_models.json). Gemma's
assistant checkpoint is required by the recorded four-token MTP configuration.

## Model selection and contamination risk

We selected **Gemma 4 31B and Qwen3.6 27B primarily to reduce the risk of
training-data contamination on IMO 2026**: the possibility that a model had
already learned the competition's problems or solutions during training.
Their release timing was central to this choice:

| Model | Public release announcement |
|---|---|
| Gemma 4, including 31B | [2 April 2026 — Google](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) |
| Qwen3.6 27B | [21 April 2026 — Qwen](https://qwen.ai/blog?id=qwen3.6-27b) |

Both announcements preceded the IMO 2026 contest days, **15–16 July 2026**, as
listed in the [official annual regulations](https://www.imo-official.org/assets/documents/imo-annual-regulations.pdf).
We used this chronology as a precaution against exposure to subsequently
published contest material. Google's [Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4)
also reports a January 2025 **pre-training** data cutoff; that statement does
not establish a cutoff for every post-training stage. We do not assert a
training-data cutoff for Qwen.

Model release dates and repository revision dates are distinct. The pinned
Gemma revision above is a [20 July 2026 tokenizer-configuration update](https://huggingface.co/google/gemma-4-31B-it/commit/842da3794eaa0b77d5f08bae87a17459d91ff475).
Revision pins identify the files used for reproduction; they do not themselves
certify a training-data cutoff. We have not independently audited either model's
full training corpus. This selection rationale therefore reduces a potential
source of contamination risk without establishing that either IMO 2026 or
IMO-ProofBench is free of training-data overlap.

## Why combine Gemma and Qwen

Release timing informed the choice of checkpoints. **Different strengths in
diagnosis and repair, observed in small controlled tests, motivated combining
the models in the harness.** Gemma generates and revises proofs, while Qwen
contributes complementary reviews and audits. The
[mixed-model rationale](mixed_model_rationale.md) describes the experiments
behind this role assignment and the larger-scale ablation needed to assess it.

## Setup and download

On the Linux GPU machine where generation will run:

```bash
python3.11 scripts/setup_environment.py --install --download-models
```

The script creates separate solver and serving environments, then downloads
the pinned revisions using Hugging Face's `snapshot_download`. The default
cache is `.models/`, which Git ignores. Use `--model-dir /path/to/cache` for
another location and pass the same option to `scripts/serve_models.py`.
Running setup without flags only displays the repositories and revisions.

Model downloads require network access to Hugging Face, but use no hosted
inference. If provider authentication is required, use your own Hugging Face
login or `HF_TOKEN` environment variable. The scripts do not write tokens into
configuration files. See the provider's
[download documentation](https://huggingface.co/docs/huggingface_hub/guides/download).
Once models and dependencies are installed, serving and generation use local
files with offline model loading enabled.

## Terms and copied files

The three model repositories identify Apache License 2.0. Google's
[Gemma 4 license](https://ai.google.dev/gemma/apache_2) is separate from the
older Gemma Terms of Use. Qwen's pinned
[LICENSE](https://huggingface.co/Qwen/Qwen3.6-27B/blob/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/LICENSE)
is also included under `licenses/`.

The copied model configuration and chat-template files retain their upstream
licenses. They are excluded from the project's CC BY-NC 4.0 license; see [NOTICE](../NOTICE).
No separate upstream NOTICE file was found at any of the three pinned revisions;
the [license audit](reproduction/model_license_audit.json) records that check.

Historical external scores used `gpt-5.6-sol / xhigh`. That model is neither
downloaded nor invoked by the reproduction scripts. Offline report reproduction
checks saved grades; fresh local generation produces new, ungraded proofs.
