from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_33_terra_structural_phase1_refinement_20260819.contracts import (
    FINAL_CANDIDATE_FAMILIES,
    FRESH_CANDIDATES_PER_ITERATION,
    GUIDED_CANDIDATES_PER_ITERATION,
    MAX_CHILD_DEPTH,
    MAX_CONJECTURE_ITERATIONS,
    MAX_NEW_CHILDREN_GLOBAL,
    PHASE_ONE_CANDIDATE_COUNT,
    PHASE_ONE_FINALIST_COUNT,
    PHASE_ONE_FINALISTS_PER_ROUTE,
    PHASE_ONE_ROUTE_COUNT,
    PHASE_ONE_WIDTH,
    SCORING_BACKEND,
    SCORING_RESULT_KEYS,
    SIDE_AUDIT_EXTERNAL_FIELDS,
    SIDE_AUDIT_MODEL_FIELDS,
    TERRA_MODEL,
    TERRA_SUCCESS_CONFIRMATIONS,
    VALID_SCORES,
    validate_promoted_profile as validate_v0333_profile,
)


HARNESS_VERSION = (
    "full-cold-start-v0.3.35-cap-continuation-recovery-qwen36-three-block-"
    "fusion-repair-gemma4-phase1-rewriter-qwen36-final-proof-scoring-"
    "over-v0.3.34"
)
ARTIFACT_SCHEMA_VERSION = "v0.3.35"
PROMOTION_PROFILE = (
    "four-routes-x-four-qwen36-three-block-diagnosis-conditional-repair-"
    "gemma4-full-proof-rewrite-fresh-three-block-qwen36-final-scoring-"
    "quality-only-selection-one-shot-doubled-cap-continuation-recovery"
)

QWEN_MODEL = "Qwen/Qwen3.6-27B"
GEMMA_MODEL = "google/gemma-4-31B-it"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
DEFAULT_REVIEWER_CUDA_DEVICE = "1"
DEFAULT_QWEN_CONCURRENCY = 1
DEFAULT_REVIEWER_CTX_SIZE = 32_768
DEFAULT_OPC_PREDICT = 8_000
DEFAULT_GPTOSS_PREDICT = 16_000
DEFAULT_GPTOSS_RETRY_REASONING_BUDGET = 8_000
DEFAULT_QWEN_FUSION_MAX_TOKENS = 12_000
DEFAULT_QWEN_REPAIR_MAX_TOKENS = 12_000
DEFAULT_QWEN_REPAIR_RECOVERY_MAX_TOKENS = 24_000
DEFAULT_PROTOCOL_ATTEMPTS = 2
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 0.95
DEFAULT_TOP_K = 64

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DEFAULT_LLAMA_BINARY = REPO_ROOT / "third_party/llama.cpp/build/bin/llama-cli"
DEFAULT_OPC_MODEL = REPO_ROOT / ".models/OPC-R1-8B.Q4_K_M.gguf"
DEFAULT_GPTOSS_MODEL = REPO_ROOT / ".models/gpt-oss-20b-mxfp4.gguf"


@dataclass(frozen=True)
class PhaseOneFeedbackConfig:
    qwen_endpoint: str = DEFAULT_QWEN_ENDPOINT
    qwen_model: str = QWEN_MODEL
    reviewer_cuda_device: str = DEFAULT_REVIEWER_CUDA_DEVICE
    llama_binary: Path = DEFAULT_LLAMA_BINARY
    opc_model: Path = DEFAULT_OPC_MODEL
    gptoss_model: Path = DEFAULT_GPTOSS_MODEL
    reviewer_ctx_size: int = DEFAULT_REVIEWER_CTX_SIZE
    opc_predict: int = DEFAULT_OPC_PREDICT
    gptoss_predict: int = DEFAULT_GPTOSS_PREDICT
    gptoss_retry_reasoning_budget: int = (
        DEFAULT_GPTOSS_RETRY_REASONING_BUDGET
    )
    qwen_fusion_max_tokens: int = DEFAULT_QWEN_FUSION_MAX_TOKENS
    qwen_repair_max_tokens: int = DEFAULT_QWEN_REPAIR_MAX_TOKENS
    qwen_repair_recovery_max_tokens: int = (
        DEFAULT_QWEN_REPAIR_RECOVERY_MAX_TOKENS
    )
    qwen_concurrency: int = DEFAULT_QWEN_CONCURRENCY
    protocol_attempts: int = DEFAULT_PROTOCOL_ATTEMPTS

    def validate(self, *, require_files: bool) -> None:
        normalized = self.qwen_endpoint.rstrip("/")
        if normalized != DEFAULT_QWEN_ENDPOINT:
            raise ValueError(
                f"Qwen3.6 fusion/repair endpoint must be {DEFAULT_QWEN_ENDPOINT!r}"
            )
        if self.qwen_model != QWEN_MODEL:
            raise ValueError(f"Qwen fusion/repair model must be {QWEN_MODEL!r}")
        if self.reviewer_cuda_device != DEFAULT_REVIEWER_CUDA_DEVICE:
            raise ValueError(
                "v0.3.35 fixes OPC/GPT-OSS and Qwen to CUDA device "
                f"{DEFAULT_REVIEWER_CUDA_DEVICE}"
            )
        positive = {
            "reviewer_ctx_size": self.reviewer_ctx_size,
            "opc_predict": self.opc_predict,
            "gptoss_predict": self.gptoss_predict,
            "gptoss_retry_reasoning_budget": self.gptoss_retry_reasoning_budget,
            "qwen_fusion_max_tokens": self.qwen_fusion_max_tokens,
            "qwen_repair_max_tokens": self.qwen_repair_max_tokens,
            "qwen_repair_recovery_max_tokens": (
                self.qwen_repair_recovery_max_tokens
            ),
            "qwen_concurrency": self.qwen_concurrency,
            "protocol_attempts": self.protocol_attempts,
        }
        invalid = {key: value for key, value in positive.items() if int(value) < 1}
        if invalid:
            raise ValueError(f"Phase-1 feedback limits must be positive: {invalid}")
        expected = {
            "reviewer_ctx_size": DEFAULT_REVIEWER_CTX_SIZE,
            "opc_predict": DEFAULT_OPC_PREDICT,
            "gptoss_predict": DEFAULT_GPTOSS_PREDICT,
            "gptoss_retry_reasoning_budget": (
                DEFAULT_GPTOSS_RETRY_REASONING_BUDGET
            ),
            "qwen_fusion_max_tokens": DEFAULT_QWEN_FUSION_MAX_TOKENS,
            "qwen_repair_max_tokens": DEFAULT_QWEN_REPAIR_MAX_TOKENS,
            "qwen_repair_recovery_max_tokens": (
                DEFAULT_QWEN_REPAIR_RECOVERY_MAX_TOKENS
            ),
            "qwen_concurrency": DEFAULT_QWEN_CONCURRENCY,
            "protocol_attempts": DEFAULT_PROTOCOL_ATTEMPTS,
        }
        mismatched = {
            key: {"expected": expected[key], "observed": positive[key]}
            for key in expected
            if positive[key] != expected[key]
        }
        if mismatched:
            raise ValueError(
                "v0.3.35 feedback hyperparameters are frozen: "
                f"{mismatched}"
            )
        if require_files:
            for label, path in {
                "llama binary": self.llama_binary,
                "OPC model": self.opc_model,
                "gpt-oss model": self.gptoss_model,
            }.items():
                resolved = Path(path).resolve()
                if not resolved.is_file() or resolved.stat().st_size == 0:
                    raise FileNotFoundError(f"{label} is missing or empty: {resolved}")

    def manifest(self) -> dict[str, Any]:
        value = asdict(self)
        for key in ("llama_binary", "opc_model", "gptoss_model"):
            value[key] = str(Path(value[key]).resolve())
        value.update(
            {
                "review_layout": "split_gptoss_three_slot",
                "local_critic_model": "INSAIT-Institute/OPC-R1-8B",
                "whole_proof_and_adversarial_model": "openai/gpt-oss-20b",
                "fusion_author": QWEN_MODEL,
                "repair_architect": QWEN_MODEL,
                "proof_rewriter": "phase1_route_gemma4_bf16_mtp4",
                "proof_rewriter_model": GEMMA_MODEL,
                "rewrite_policy": "only_when_qwen_handoff_requires_repair",
                "post_rewrite_grade_call": False,
                "reference_solution_access": False,
                "qwen_and_gguf_gpu_execution": "serialized_by_shared_process_lock",
                "recommended_qwen_gpu_memory_utilization": 0.77,
                "reviewer_threads": 12,
                "reviewer_gpu_layers": 999,
                "reviewer_batch_size": 256,
                "reviewer_ubatch_size": 128,
                "gptoss_primary_reasoning_budget": None,
                "temperature": DEFAULT_TEMPERATURE,
                "top_p": DEFAULT_TOP_P,
                "top_k": DEFAULT_TOP_K,
                "cap_exhaustion_recovery": {
                    "policy": "reuse_partial_then_continue_once_at_double_cap",
                    "opc": {"primary": 8_000, "recovery": 16_000},
                    "gptoss": {"primary": 16_000, "recovery": 32_000},
                    "qwen_fusion": {"primary": 12_000, "recovery": 24_000},
                    "qwen_repair": {"primary": 12_000, "recovery": 24_000},
                    "gemma_draft_and_rewrite": {
                        "primary": 65_536,
                        "recovery": 131_072,
                    },
                    "gemma_lazy_check": {"primary": 8_192, "recovery": 16_384},
                    "maximum_continuations_per_capped_call": 1,
                },
            }
        )
        return value


def validate_promoted_profile() -> None:
    validate_v0333_profile()
    if PHASE_ONE_ROUTE_COUNT != 4 or PHASE_ONE_WIDTH != 4:
        raise RuntimeError("v0.3.35 requires four Phase-1 routes of width four")
    if PHASE_ONE_CANDIDATE_COUNT != 16:
        raise RuntimeError("v0.3.35 requires the fixed sixteen-proof Phase 1")


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "DEFAULT_GPTOSS_MODEL",
    "DEFAULT_LLAMA_BINARY",
    "DEFAULT_OPC_MODEL",
    "DEFAULT_QWEN_ENDPOINT",
    "GEMMA_MODEL",
    "HARNESS_VERSION",
    "PHASE_ONE_ROUTE_COUNT",
    "PHASE_ONE_WIDTH",
    "PROMOTION_PROFILE",
    "PhaseOneFeedbackConfig",
    "QWEN_MODEL",
    "TERRA_MODEL",
    "validate_promoted_profile",
]
