from __future__ import annotations

from experiments.local_math_verifier.timeout_recovery import require_valid_fallback

import fcntl
import json
import threading
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable, Iterator

from experiments.local_math_verifier.cap_recovery import (
    POLICY_ID, clean_capped_result, policy_manifest, recovery_limit, MAX_RETRY_TOKENS,
)

from experiments.local_math_verifier.runtime import (
    GenerationConfig,
    HTTPGenerationConfig,
    run_llama_generation,
    run_openai_chat_generation,
    utc_now,
    write_json,
)

from .protocol import (
    TwoBlockMaterials,
    canonicalize_component_review,
    fusion_user_prompt,
    independent_review_prompt,
    parse_component_review,
    parse_fusion_output,
    review_source,
    sha256_text,
)


GEMMA_MODEL = "google/gemma-4-31B-it"
DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8020/v1"
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LLAMA_BINARY = REPO_ROOT / "third_party/llama.cpp/build/bin/llama-cli"
DEFAULT_OPC_MODEL = REPO_ROOT / ".models/OPC-R1-8B.Q4_K_M.gguf"
DEFAULT_GPTOSS_MODEL = REPO_ROOT / ".models/gpt-oss-20b-mxfp4.gguf"


def merge_continuation(partial: str, continuation: str) -> str:
    partial, continuation = partial.strip(), continuation.strip()
    if not partial:
        return continuation
    if not continuation:
        return partial
    prefix = partial[: min(256, len(partial))]
    if len(prefix) >= 64 and continuation.startswith(prefix):
        return continuation
    maximum = min(len(partial), len(continuation), 8_192)
    for size in range(maximum, 31, -1):
        if partial[-size:] == continuation[:size]:
            return partial + continuation[size:]
    return partial + ("" if partial.endswith((" ", "\n")) else "\n") + continuation


def normalize_gptoss_boundary(report: str) -> str:
    value = report.strip()
    start, end = "[Start thinking]", "[End thinking]"
    if not value.startswith(start) or end not in value:
        return value
    last_end = value.rfind(end)
    reasoning = value[len(start) : last_end]
    final = value[last_end + len(end) :]
    reasoning = reasoning.replace(start, "[Start-thinking]").replace(
        end, "[End-thinking]"
    )
    return f"{start}{reasoning}{end}{final}".strip()


@contextmanager
def reviewer_gpu_lock(cuda_device: str) -> Iterator[None]:
    path = Path(f"/tmp/cognitive-well-local-fusion-gpu{cuda_device}.lock")
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@dataclass(frozen=True)
class RuntimeConfig:
    gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT
    gemma_model: str = GEMMA_MODEL
    reviewer_cuda_device: str = "1"
    llama_binary: Path = DEFAULT_LLAMA_BINARY
    opc_model: Path = DEFAULT_OPC_MODEL
    gptoss_model: Path = DEFAULT_GPTOSS_MODEL
    reviewer_ctx_size: int = 32_768
    opc_predict: int = 8_000
    gptoss_predict: int = 16_000
    gptoss_retry_reasoning_budget: int = 8_000
    fusion_max_tokens: int = 12_000
    rewrite_max_tokens: int = 65_536
    solver_max_tokens: int = 65_536
    lazy_max_tokens: int = 8_192
    protocol_attempts: int = 2

    def validate(self, *, require_files: bool = True) -> None:
        if self.gemma_endpoint.rstrip("/") != DEFAULT_GEMMA_ENDPOINT:
            raise ValueError(f"BF16/MTP4 Gemma endpoint must be {DEFAULT_GEMMA_ENDPOINT}")
        if self.gemma_model != GEMMA_MODEL:
            raise ValueError(f"Gemma model must be {GEMMA_MODEL}")
        positive = {
            "reviewer_ctx_size": self.reviewer_ctx_size,
            "opc_predict": self.opc_predict,
            "gptoss_predict": self.gptoss_predict,
            "gptoss_retry_reasoning_budget": self.gptoss_retry_reasoning_budget,
            "fusion_max_tokens": self.fusion_max_tokens,
            "rewrite_max_tokens": self.rewrite_max_tokens,
            "solver_max_tokens": self.solver_max_tokens,
            "lazy_max_tokens": self.lazy_max_tokens,
            "protocol_attempts": self.protocol_attempts,
        }
        if bad := {key: value for key, value in positive.items() if value < 1}:
            raise ValueError(f"runtime limits must be positive: {bad}")
        if require_files:
            for label, path in {
                "llama binary": self.llama_binary,
                "OPC model": self.opc_model,
                "GPT-OSS model": self.gptoss_model,
            }.items():
                if not path.resolve().is_file() or path.resolve().stat().st_size == 0:
                    raise FileNotFoundError(f"{label} missing: {path.resolve()}")

    def manifest(self) -> dict[str, Any]:
        result = asdict(self)
        for key in ("llama_binary", "opc_model", "gptoss_model"):
            result[key] = str(Path(result[key]).resolve())
        result.update(
            {
                "gemma_dtype": "bfloat16",
                "gemma_mtp_speculative_tokens": 4,
                "review_layout": "two_final_blocks_only",
                "gptoss_reasoning_in_fusion": False,
                "reviewers_may_score": False,
                "fusion_author": GEMMA_MODEL,
                "rewriter": GEMMA_MODEL,
                "temperature_top_p_top_k": [0.2, 0.95, 64],
                "cap_recovery": policy_manifest(),
            }
        )
        return result


class StageRuntime:
    def __init__(self, config: RuntimeConfig) -> None:
        config.validate(require_files=False)
        self.config = config
        self._gemma_slots = threading.BoundedSemaphore(2)

    @staticmethod
    def _read_cached(
        *, output_dir: Path, name: str, identity: dict[str, Any]
    ) -> dict[str, Any] | None:
        path = output_dir / f"{name}.result.json"
        if not path.is_file():
            return None
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("identity") != identity:
            return None
        return saved

    @staticmethod
    def _save_cached(
        *, output_dir: Path, name: str, identity: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any]:
        saved = {**result, "identity": identity, "completed_at": utc_now()}
        write_json(output_dir / f"{name}.result.json", saved)
        return saved

    @staticmethod
    def _reusable_http(result: dict[str, Any]) -> str:
        chunks = []
        reasoning = str(result.get("reasoning") or "").strip()
        final = str(result.get("text") or "").strip()
        if reasoning:
            chunks.append("[Preserved reasoning]\n" + reasoning)
        if final:
            chunks.append("[Preserved final response fragment]\n" + final)
        return "\n\n".join(chunks)

    def gemma_call(
        self,
        *,
        output_dir: Path,
        name: str,
        system_prompt: str,
        user_prompt: str,
        seed: int,
        temperature: float,
        max_tokens: int,
        parser: Callable[[str], dict[str, Any]],
    ) -> dict[str, Any]:
        output_dir.mkdir(parents=True, exist_ok=True)
        identity = {
            "endpoint": self.config.gemma_endpoint.rstrip("/"),
            "model": self.config.gemma_model,
            "system_prompt_sha256": sha256_text(system_prompt),
            "user_prompt_sha256": sha256_text(user_prompt),
            "seed": seed,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "cap_recovery_policy": POLICY_ID,
        }
        cached = self._read_cached(output_dir=output_dir, name=name, identity=identity)
        if cached is not None and parser(str(cached.get("text") or "")).get("valid"):
            return {**cached, "response_source": "saved"}

        errors: list[dict[str, Any]] = []
        for attempt in range(self.config.protocol_attempts):
            attempt_seed = (seed + attempt) & 0xFFFFFFFF
            config = HTTPGenerationConfig(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                top_k=64,
                seed=attempt_seed,
                thinking_token_budget=None,
                reasoning_effort=None,
                timeout_seconds=14_400,
            )
            with self._gemma_slots:
                first = run_openai_chat_generation(
                    endpoint=self.config.gemma_endpoint,
                    model=self.config.gemma_model,
                    prompt=system_prompt,
                    user_prompt=user_prompt,
                    output_dir=output_dir,
                    stage=f"{name}_attempt{attempt + 1}",
                    config=config,
                )
            text = str(first["text"]).strip()
            cap_recovery: dict[str, Any] = {"triggered": False}
            final_metadata = first["metadata"]
            if first["metadata"].get("finish_reason") == "length":
                cleaned, trimming = clean_capped_result(first)
                reusable = self._reusable_http(cleaned)
                text = str(cleaned.get("text") or "").strip()
                if not reusable and not trimming["detected"]:
                    raise RuntimeError(f"{name} hit cap with no reusable generation")
                recovery_config = replace(
                    config,
                    max_tokens=recovery_limit(first, max_tokens),
                    seed=(attempt_seed + 1_000_003) & 0xFFFFFFFF,
                )
                write_json(output_dir / f"{name}_attempt{attempt + 1}.cap_recovery_input.json", {
                    "policy": POLICY_ID, "trimming": trimming,
                    "recovery_max_tokens": recovery_config.max_tokens,
                    "prior_sha256": sha256_text(reusable),
                })
                with self._gemma_slots:
                    recovery = run_openai_chat_generation(
                        endpoint=self.config.gemma_endpoint,
                        model=self.config.gemma_model,
                        prompt=system_prompt,
                        user_prompt=user_prompt,
                        prior_generation=reusable or None,
                        output_dir=output_dir,
                        stage=f"{name}_attempt{attempt + 1}_cap_continuation",
                        config=recovery_config,
                    )
                continuation = str(recovery["text"]).strip()
                text = merge_continuation(text, continuation)
                final_metadata = recovery["metadata"]
                cap_recovery = {
                    "triggered": True,
                    "reused_partial_generation": bool(reusable),
                    "policy": POLICY_ID, "trimming": trimming,
                    "primary_max_tokens": max_tokens,
                    "recovery_max_tokens": recovery_config.max_tokens,
                    "partial_sha256": sha256_text(reusable),
                    "continuation_sha256": sha256_text(continuation),
                    "recovery_metadata": recovery["metadata"],
                }
                if recovery["metadata"].get("finish_reason") == "length":
                    errors.append({"attempt": attempt + 1, "error": "bounded cap recovery exhausted"})
                    break
            try:
                parsed = parser(text)
            except Exception:
                require_valid_fallback(final_metadata, {"valid": False})
                raise
            require_valid_fallback(final_metadata, parsed)
            if not parsed.get("valid"):
                errors.append({"attempt": attempt + 1, "errors": parsed.get("errors", [])})
                continue
            result = self._save_cached(
                output_dir=output_dir,
                name=name,
                identity=identity,
                result={
                    "text": text,
                    "parsed": parsed,
                    "generation": first["metadata"],
                    "final_generation": final_metadata,
                    "cap_recovery": cap_recovery,
                    "prior_errors": errors,
                    "response_source": "live",
                },
            )
            (output_dir / f"{name}.txt").write_text(text + "\n", encoding="utf-8")
            return result
        raise RuntimeError(f"{name} exhausted protocol attempts: {errors}")

    def _review_config(
        self, *, role: str, seed: int, bounded_retry: bool = False
    ) -> GenerationConfig:
        return GenerationConfig(
            ctx_size=self.config.reviewer_ctx_size,
            predict=self.config.opc_predict if role == "opc" else self.config.gptoss_predict,
            threads=12,
            gpu_layers=999,
            batch_size=256,
            ubatch_size=128,
            temperature=0.2,
            seed=seed,
            reasoning_budget=(
                self.config.gptoss_retry_reasoning_budget
                if role == "gptoss" and bounded_retry
                else None
            ),
            cuda_visible_devices=self.config.reviewer_cuda_device,
        )

    def component_review(
        self,
        *,
        role: str,
        source: str,
        output_dir: Path,
        seed: int,
    ) -> dict[str, Any]:
        output_dir.mkdir(parents=True, exist_ok=True)
        prompt = independent_review_prompt(role=role, source=source)
        model = self.config.opc_model if role == "opc" else self.config.gptoss_model
        identity = {
            "role": role,
            "prompt_sha256": sha256_text(prompt),
            "model": str(model.resolve()),
            "seed": seed,
        }
        cached = self._read_cached(output_dir=output_dir, name=role, identity=identity)
        if cached is not None:
            parsed = parse_component_review(role=role, report=str(cached.get("raw") or ""))
            if parsed["valid"]:
                return {**cached, "parsed": parsed, "response_source": "saved"}

        attempts = [(f"{role}_review", self._review_config(role=role, seed=seed))]
        if role == "gptoss":
            attempts.append(
                (
                    "gptoss_review_bounded_retry",
                    self._review_config(role=role, seed=(seed + 1) & 0xFFFFFFFF, bounded_retry=True),
                )
            )
        else:
            attempts.append(("opc_review_retry", self._review_config(role=role, seed=(seed + 1) & 0xFFFFFFFF)))

        errors: list[dict[str, Any]] = []
        for stage, config in attempts:
            with reviewer_gpu_lock(self.config.reviewer_cuda_device):
                first = run_llama_generation(
                    binary=str(self.config.llama_binary),
                    model=model,
                    prompt=prompt,
                    output_dir=output_dir,
                    stage=stage,
                    config=config,
                    detect_token_cap=True,
                )
            raw = str(first["text"]).strip()
            cap_recovery: dict[str, Any] = {"triggered": False}
            if first["metadata"].get("finish_reason") == "length":
                recovery_config = replace(
                    config,
                    ctx_size=config.ctx_size * 2,
                    predict=config.predict * 2,
                    seed=(config.seed + 1_000_003) & 0xFFFFFFFF,
                )
                continuation_prompt = (
                    prompt
                    + "\n\n## Preserved partial assistant generation\n"
                    + raw
                    + "\n\nContinue exactly where it stopped. Do not restart. Output only the missing continuation."
                )
                with reviewer_gpu_lock(self.config.reviewer_cuda_device):
                    recovery = run_llama_generation(
                        binary=str(self.config.llama_binary),
                        model=model,
                        prompt=continuation_prompt,
                        output_dir=output_dir,
                        stage=stage + "_cap_continuation",
                        config=recovery_config,
                        detect_token_cap=True,
                    )
                continuation = str(recovery["text"]).strip()
                raw = merge_continuation(raw, continuation)
                if role == "gptoss":
                    raw = normalize_gptoss_boundary(raw)
                cap_recovery = {
                    "triggered": True,
                    "reused_partial_generation": bool(reusable),
                    "policy": POLICY_ID, "trimming": trimming,
                    "primary_predict": config.predict,
                    "recovery_predict": recovery_config.predict,
                    "primary_ctx_size": config.ctx_size,
                    "recovery_ctx_size": recovery_config.ctx_size,
                    "partial_sha256": sha256_text(str(first["text"])),
                    "continuation_sha256": sha256_text(continuation),
                }
                if recovery["metadata"].get("finish_reason") == "length":
                    errors.append({"stage": stage, "error": "bounded cap recovery exhausted"})
                    break
            raw = canonicalize_component_review(role=role, report=raw)
            parsed = parse_component_review(role=role, report=raw)
            if not parsed["valid"]:
                errors.append({"stage": stage, "errors": parsed["errors"]})
                continue
            result = self._save_cached(
                output_dir=output_dir,
                name=role,
                identity=identity,
                result={
                    "raw": raw,
                    "final": parsed["final"],
                    "reasoning": parsed["reasoning"],
                    "parsed": parsed,
                    "generation": first["metadata"],
                    "cap_recovery": cap_recovery,
                    "prior_errors": errors,
                    "response_source": "live",
                },
            )
            (output_dir / f"{role}.final.txt").write_text(parsed["final"] + "\n", encoding="utf-8")
            if parsed["reasoning"]:
                (output_dir / f"{role}.reasoning.txt").write_text(parsed["reasoning"] + "\n", encoding="utf-8")
            return result
        raise RuntimeError(f"{role} exhausted review attempts: {errors}")

    def two_block_reviews(
        self,
        *,
        problem: str,
        proof: str,
        output_dir: Path,
        seed: int,
    ) -> TwoBlockMaterials:
        self.config.validate(require_files=True)
        source = review_source(problem=problem, proof=proof)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "review_source.md").write_text(source, encoding="utf-8")
        opc = self.component_review(
            role="opc", source=source, output_dir=output_dir / "opc", seed=seed
        )
        gptoss = self.component_review(
            role="gptoss",
            source=source,
            output_dir=output_dir / "gptoss",
            seed=(seed + 1) & 0xFFFFFFFF,
        )
        objections = tuple(opc["parsed"]["objections"] + gptoss["parsed"]["objections"])
        materials = TwoBlockMaterials(
            problem=problem,
            candidate_proof=proof,
            opc_final=str(opc["final"]),
            gptoss_final=str(gptoss["final"]),
            objections=objections,
        )
        materials.validate()
        identity = {
            "problem_sha256": sha256_text(problem),
            "proof_sha256": sha256_text(proof),
            "opc_final_sha256": sha256_text(materials.opc_final),
            "gptoss_final_sha256": sha256_text(materials.gptoss_final),
            "gptoss_reasoning_sha256": sha256_text(str(gptoss["reasoning"])),
            "fusion_block_count": 2,
            "gptoss_reasoning_in_fusion": False,
            "reference_solution_access": False,
        }
        write_json(output_dir / "two_block_identity.json", identity)
        return materials

    def fuse_two_blocks(
        self,
        *,
        materials: TwoBlockMaterials,
        system_prompt: str,
        output_dir: Path,
        seed: int,
    ) -> dict[str, Any]:
        user = fusion_user_prompt(materials)
        (output_dir / "fusion_input.md").parent.mkdir(parents=True, exist_ok=True)
        (output_dir / "fusion_input.md").write_text(user, encoding="utf-8")
        parser = lambda text: parse_fusion_output(
            text, required_objections=materials.objections
        )
        return self.gemma_call(
            output_dir=output_dir,
            name="gemma_review_fusion",
            system_prompt=system_prompt,
            user_prompt=user,
            seed=seed,
            temperature=0.2,
            max_tokens=self.config.fusion_max_tokens,
            parser=parser,
        )
