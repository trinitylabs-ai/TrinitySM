from __future__ import annotations

import fcntl
import json
import re
import threading
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Callable, Iterator

from experiments.local_math_verifier.runtime import (
    GenerationConfig,
    HTTPGenerationConfig,
    run_llama_generation,
    run_openai_chat_generation,
    utc_now,
    write_json,
)

from .contracts import (
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    PhaseOneFeedbackConfig,
)
from .protocol import (
    FUSION_SYSTEM_PROMPT,
    REPAIR_SYSTEM_PROMPT,
    RESOLVER_SYSTEM_PROMPT,
    ThreeBlockMaterials,
    fusion_user_prompt,
    independent_review_prompt,
    parse_fusion_output,
    parse_repair_output,
    repair_user_prompt,
    resolver_user_prompt,
    sha256_text,
    split_gptoss_three_blocks,
    validate_component_review,
)


@contextmanager
def reviewer_gpu_lock(cuda_device: str) -> Iterator[None]:
    # Share the established local-fusion lock so this harness cannot load a
    # reviewer concurrently with an older local-verifier job on the same GPU.
    lock_path = Path(f"/tmp/cognitive-well-local-fusion-gpu{cuda_device}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class PhaseOneFeedbackRuntime:
    """Run the frozen three-block Qwen feedback and Gemma rewrite boundary."""

    def __init__(self, config: PhaseOneFeedbackConfig) -> None:
        config.validate(require_files=False)
        self.config = config
        self._qwen_slots = threading.BoundedSemaphore(config.qwen_concurrency)

    def _review_config(
        self, *, role: str, seed: int, bounded_retry: bool = False
    ) -> GenerationConfig:
        return GenerationConfig(
            ctx_size=self.config.reviewer_ctx_size,
            predict=(
                self.config.opc_predict
                if role == "opc"
                else self.config.gptoss_predict
            ),
            threads=12,
            gpu_layers=999,
            batch_size=256,
            ubatch_size=128,
            temperature=DEFAULT_TEMPERATURE,
            seed=seed,
            reasoning_budget=(
                self.config.gptoss_retry_reasoning_budget
                if role == "gptoss" and bounded_retry
                else None
            ),
            cuda_visible_devices=self.config.reviewer_cuda_device,
        )

    def _component_identity(
        self, *, prompt: str, model: Path, config: GenerationConfig
    ) -> dict[str, Any]:
        return {
            "prompt_sha256": sha256_text(prompt),
            "model_path": str(model.resolve()),
            "llama_binary": str(self.config.llama_binary.resolve()),
            "config": asdict(config),
        }

    @staticmethod
    def _continuation_prompt(*, original_prompt: str, partial: str) -> str:
        return (
            original_prompt
            + "\n\n## Preserved partial assistant generation\n"
            + partial
            + "\n\n## Cap-exhaustion continuation repair\n"
            "The preserved response above reached its output-token cap. "
            "Continue exactly where it stopped. Do not restart or repeat "
            "completed material. Output only the missing continuation."
        )

    @staticmethod
    def _merge_continuation(partial: str, continuation: str) -> str:
        partial = partial.strip()
        continuation = continuation.strip()
        if not partial:
            return continuation
        if not continuation:
            return partial
        # A continuation model occasionally restarts from the beginning despite
        # the instruction. Prefer that self-contained restatement over creating
        # a duplicated protocol document.
        prefix = partial[: min(256, len(partial))]
        if len(prefix) >= 64 and continuation.startswith(prefix):
            return continuation
        maximum = min(len(partial), len(continuation), 8_192)
        overlap = 0
        for size in range(maximum, 31, -1):
            if partial[-size:] == continuation[:size]:
                overlap = size
                break
        separator = "" if overlap or partial.endswith((" ", "\n")) else "\n"
        return partial + separator + continuation[overlap:]

    @staticmethod
    def _normalize_gptoss_thinking_boundary(report: str) -> str:
        """Keep one outer GPT-OSS reasoning boundary after continuation.

        llama.cpp closes a capped GPT-OSS turn with ``[End thinking]`` even
        though the reasoning was truncated.  A continuation starts a new turn
        and can also quote that forced closing marker while describing where it
        resumed.  Preserve all generated text, but demote every nested marker
        to plain prose and retain only the first opening plus last closing
        marker as the frozen three-block protocol boundary.
        """

        value = report.strip()
        start = "[Start thinking]"
        end = "[End thinking]"
        if not value.startswith(start) or end not in value:
            return value
        last_end = value.rfind(end)
        reasoning = value[len(start) : last_end]
        final = value[last_end + len(end) :]
        reasoning = reasoning.replace(start, "[Start-thinking]").replace(
            end, "[End-thinking]"
        )
        return f"{start}{reasoning}{end}{final}".strip()

    @staticmethod
    def _normalize_opc_terminal_marker(report: str) -> str:
        """Repair harmless OPC formatting around its declared final verdict.

        OPC occasionally emits ``boxed{incorrect}`` or ``boxed{correct}``
        despite being told to use the LaTeX ``\\boxed`` command, and may append
        a duplicate prose block after that declared terminal line.  Accept no
        broader protocol drift: find only a stand-alone boxed verdict, retain
        everything through it, canonicalize it, and discard only the forbidden
        post-terminal text.
        """

        value = report.strip()
        matches = list(
            re.finditer(
                r"(?im)^[ \t]*(?:\\)?boxed\s*\{\s*(correct|incorrect)\s*\}[ \t]*$",
                value,
            )
        )
        if not matches:
            return value
        match = matches[-1]
        prefix = value[: match.start()].rstrip()
        verdict = rf"\boxed{{{match.group(1).lower()}}}"
        return f"{prefix}\n{verdict}" if prefix else verdict

    @staticmethod
    def _reusable_http_generation(result: dict[str, Any]) -> str:
        reasoning = str(result.get("reasoning") or "").strip()
        final = str(result.get("text") or "").strip()
        chunks: list[str] = []
        if reasoning:
            chunks.append("[Preserved reasoning]\n" + reasoning)
        if final:
            chunks.append("[Preserved final response fragment]\n" + final)
        return "\n\n".join(chunks)

    def _generate_component(
        self,
        *,
        role: str,
        source_prompt: str,
        output_dir: Path,
        seed: int,
    ) -> tuple[str, dict[str, Any]]:
        output_dir.mkdir(parents=True, exist_ok=True)
        prompt = independent_review_prompt(role=role, source_prompt=source_prompt)
        model = self.config.opc_model if role == "opc" else self.config.gptoss_model
        primary = self._review_config(role=role, seed=seed)
        summary_path = output_dir / f"{role}.component.json"
        report_path = output_dir / f"{role}.txt"
        if summary_path.is_file() and report_path.is_file():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            report = report_path.read_text(encoding="utf-8").strip()
            saved_reasoning_budget = summary.get("reasoning_budget")
            cached_config = (
                self._review_config(
                    role=role, seed=seed + 1, bounded_retry=True
                )
                if role == "gptoss" and saved_reasoning_budget is not None
                else primary
            )
            expected = self._component_identity(
                prompt=prompt,
                model=model,
                config=cached_config,
            )
            if (
                all(summary.get(key) == value for key, value in expected.items())
                and summary.get("report_sha256") == sha256_text(report)
            ):
                validate_component_review(role=role, report=report)
                if role == "gptoss":
                    split_gptoss_three_blocks(report)
                return report, {**summary, "response_source": "saved_component"}

        attempts = [(f"{role}_review", primary)]
        if role == "gptoss":
            attempts.append(
                (
                    "gptoss_review_bounded_retry",
                    self._review_config(
                        role=role, seed=seed + 1, bounded_retry=True
                    ),
                )
            )
        errors: list[str] = []
        for stage, attempt_config in attempts:
            result = run_llama_generation(
                binary=str(self.config.llama_binary),
                model=model,
                prompt=prompt,
                output_dir=output_dir,
                stage=stage,
                config=attempt_config,
                detect_token_cap=True,
            )
            report = str(result["text"]).strip()
            if role == "opc":
                report = self._normalize_opc_terminal_marker(report)
            cap_recovery: dict[str, Any] | None = None
            if result["metadata"].get("finish_reason") == "length":
                recovery_config = replace(
                    attempt_config,
                    ctx_size=attempt_config.ctx_size * 2,
                    predict=attempt_config.predict * 2,
                    seed=(attempt_config.seed + 1_000_003) & 0xFFFFFFFF,
                )
                recovery = run_llama_generation(
                    binary=str(self.config.llama_binary),
                    model=model,
                    prompt=self._continuation_prompt(
                        original_prompt=prompt, partial=report
                    ),
                    output_dir=output_dir,
                    stage=f"{stage}_cap_continuation",
                    config=recovery_config,
                    detect_token_cap=True,
                )
                continued = str(recovery["text"]).strip()
                report = self._merge_continuation(report, continued)
                if role == "gptoss":
                    report = self._normalize_gptoss_thinking_boundary(report)
                else:
                    report = self._normalize_opc_terminal_marker(report)
                cap_recovery = {
                    "triggered": True,
                    "reused_partial_generation": True,
                    "primary_predict": attempt_config.predict,
                    "recovery_predict": recovery_config.predict,
                    "primary_ctx_size": attempt_config.ctx_size,
                    "recovery_ctx_size": recovery_config.ctx_size,
                    "partial_sha256": sha256_text(str(result["text"])),
                    "continuation_sha256": sha256_text(continued),
                    "continuation_generation": recovery["metadata"],
                }
                if recovery["metadata"].get("finish_reason") == "length":
                    errors.append(
                        f"{stage}: doubled-cap continuation also reached its cap"
                    )
                    continue
            try:
                validate_component_review(role=role, report=report)
                if role == "gptoss":
                    split_gptoss_three_blocks(report)
            except ValueError as error:
                # A disobedient continuation can restate a complete report. If
                # concatenation duplicated protocol framing, validate that
                # self-contained continuation before moving to a fresh retry.
                if cap_recovery is not None:
                    report = (
                        self._normalize_gptoss_thinking_boundary(continued)
                        if role == "gptoss"
                        else self._normalize_opc_terminal_marker(continued)
                    )
                    try:
                        validate_component_review(role=role, report=report)
                        if role == "gptoss":
                            split_gptoss_three_blocks(report)
                    except ValueError:
                        errors.append(f"{stage}: {error}")
                        break
                else:
                    errors.append(f"{stage}: {error}")
                    continue
            report_path.write_text(report + "\n", encoding="utf-8")
            summary = {
                **self._component_identity(
                    prompt=prompt, model=model, config=attempt_config
                ),
                "selected_stage": stage,
                "reasoning_budget": attempt_config.reasoning_budget,
                "report_sha256": sha256_text(report),
                "generation": result["metadata"],
                "cap_recovery": cap_recovery or {"triggered": False},
                "prior_errors": errors,
                "completed_at": utc_now(),
            }
            write_json(summary_path, summary)
            return report, {**summary, "response_source": "live_component"}
        raise RuntimeError(f"{role} exhausted component attempts: {'; '.join(errors)}")

    def generate_three_block_reviews(
        self,
        *,
        problem: str,
        proof: str,
        grading_rubric: str,
        source_prompt: str,
        output_dir: Path,
        seed: int,
    ) -> dict[str, Any]:
        self.config.validate(require_files=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "source_request.txt").write_text(
            source_prompt, encoding="utf-8"
        )
        with reviewer_gpu_lock(self.config.reviewer_cuda_device):
            opc, opc_metadata = self._generate_component(
                role="opc",
                source_prompt=source_prompt,
                output_dir=output_dir,
                seed=seed,
            )
            gptoss, gptoss_metadata = self._generate_component(
                role="gptoss",
                source_prompt=source_prompt,
                output_dir=output_dir,
                seed=seed + 1,
            )
        whole_proof, adversarial = split_gptoss_three_blocks(gptoss)
        materials = ThreeBlockMaterials(
            problem=problem,
            candidate_proof=proof,
            grading_rubric=grading_rubric,
            local_critic=opc,
            whole_proof_grader=whole_proof,
            adversarial_checker=adversarial,
        )
        materials.validate()
        for name, value in {
            "local_critic.md": opc,
            "whole_proof_grader.md": whole_proof,
            "adversarial_checker.md": adversarial,
        }.items():
            (output_dir / name).write_text(value + "\n", encoding="utf-8")
        identity = {
            "problem_sha256": sha256_text(problem),
            "candidate_proof_sha256": sha256_text(proof),
            "grading_rubric_sha256": sha256_text(grading_rubric),
            "source_prompt_sha256": sha256_text(source_prompt),
            "local_critic_sha256": sha256_text(opc),
            "whole_proof_grader_sha256": sha256_text(whole_proof),
            "adversarial_checker_sha256": sha256_text(adversarial),
            "review_layout": "split_gptoss_three_slot",
            "reference_solution_access": False,
        }
        write_json(output_dir / "three_block_identity.json", identity)
        return {
            "materials": materials,
            "identity": identity,
            "component_metadata": {
                "opc": opc_metadata,
                "gptoss": gptoss_metadata,
            },
        }

    @staticmethod
    def _http_config(*, max_tokens: int, seed: int) -> HTTPGenerationConfig:
        return HTTPGenerationConfig(
            max_tokens=max_tokens,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            top_k=DEFAULT_TOP_K,
            seed=seed,
            thinking_token_budget=None,
            reasoning_effort=None,
            timeout_seconds=14_400,
        )

    def _cached_protocol_output(
        self,
        *,
        output_dir: Path,
        stage: str,
        endpoint: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        base_seed: int,
        parser: Callable[[str], dict[str, Any]],
    ) -> tuple[str, dict[str, Any], dict[str, Any]] | None:
        report_path = output_dir / f"{stage}_output.md"
        summary_path = output_dir / f"{stage}_generation.json"
        if not report_path.is_file() or not summary_path.is_file():
            return None
        report = report_path.read_text(encoding="utf-8").strip()
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        expected = {
            "endpoint": endpoint.rstrip("/"),
            "model": model,
            "system_prompt_sha256": sha256_text(system_prompt),
            "user_prompt_sha256": sha256_text(user_prompt),
            "base_seed": base_seed,
            "report_sha256": sha256_text(report),
        }
        if not all(summary.get(key) == value for key, value in expected.items()):
            return None
        saved_max_tokens = summary.get("max_tokens")
        allowed_max_tokens = {max_tokens, max_tokens * 2}
        if saved_max_tokens not in allowed_max_tokens:
            return None
        if (
            saved_max_tokens == max_tokens * 2
            and int(summary.get("selected_attempt", 1)) < 2
            and not bool(summary.get("cap_recovery", {}).get("triggered"))
        ):
            return None
        parsed = parser(report)
        if not parsed.get("valid"):
            return None
        return report, parsed, {**summary, "response_source": "saved_protocol_output"}

    def _run_protocol_call(
        self,
        *,
        output_dir: Path,
        stage: str,
        endpoint: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        base_seed: int,
        parser: Callable[[str], dict[str, Any]],
        use_qwen_slot: bool,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        output_dir.mkdir(parents=True, exist_ok=True)
        cached = self._cached_protocol_output(
            output_dir=output_dir,
            stage=stage,
            endpoint=endpoint,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            base_seed=base_seed,
            parser=parser,
        )
        if cached is not None:
            return cached
        errors: list[dict[str, Any]] = []
        for attempt in range(self.config.protocol_attempts):
            attempt_max_tokens = max_tokens
            config = self._http_config(
                max_tokens=attempt_max_tokens,
                seed=(base_seed + attempt) & 0xFFFFFFFF,
            )

            def call() -> dict[str, Any]:
                return run_openai_chat_generation(
                    endpoint=endpoint,
                    model=model,
                    prompt=system_prompt,
                    user_prompt=user_prompt,
                    output_dir=output_dir,
                    stage=f"{stage}_attempt{attempt + 1}",
                    config=config,
                )

            if use_qwen_slot:
                with self._qwen_slots:
                    with reviewer_gpu_lock(self.config.reviewer_cuda_device):
                        result = call()
            else:
                result = call()
            report = str(result["text"]).strip()
            parsed = parser(report)
            finish_reason = result["metadata"].get("finish_reason")
            cap_recovery: dict[str, Any] | None = None
            if finish_reason == "length":
                reusable = self._reusable_http_generation(result)
                if not reusable:
                    raise RuntimeError(
                        f"{stage} reached max_tokens without reusable generation"
                    )
                recovery_config = self._http_config(
                    max_tokens=max_tokens * 2,
                    seed=(base_seed + attempt + 1_000_003) & 0xFFFFFFFF,
                )

                def recovery_call() -> dict[str, Any]:
                    return run_openai_chat_generation(
                        endpoint=endpoint,
                        model=model,
                        prompt=system_prompt,
                        user_prompt=user_prompt,
                        output_dir=output_dir,
                        stage=f"{stage}_attempt{attempt + 1}_cap_continuation",
                        config=recovery_config,
                        prior_generation=reusable,
                    )

                if use_qwen_slot:
                    with self._qwen_slots:
                        with reviewer_gpu_lock(self.config.reviewer_cuda_device):
                            recovery_result = recovery_call()
                else:
                    recovery_result = recovery_call()
                continuation = str(recovery_result["text"]).strip()
                report = self._merge_continuation(report, continuation)
                parsed = parser(report)
                if not parsed.get("valid") and continuation:
                    continuation_parsed = parser(continuation)
                    if continuation_parsed.get("valid"):
                        report = continuation
                        parsed = continuation_parsed
                cap_recovery = {
                    "triggered": True,
                    "reused_partial_generation": True,
                    "primary_max_tokens": max_tokens,
                    "recovery_max_tokens": max_tokens * 2,
                    "partial_final_sha256": sha256_text(str(result["text"])),
                    "partial_reusable_sha256": sha256_text(reusable),
                    "continuation_sha256": sha256_text(continuation),
                    "continuation_generation": recovery_result["metadata"],
                }
                finish_reason = recovery_result["metadata"].get("finish_reason")
                attempt_max_tokens = max_tokens * 2
                if finish_reason == "length":
                    parsed = {
                        **parsed,
                        "valid": False,
                        "errors": [
                            *parsed.get("errors", []),
                            "doubled-cap continuation also reached max_tokens",
                        ],
                    }
            if not parsed.get("valid"):
                errors.append(
                    {
                        "attempt": attempt + 1,
                        "finish_reason": finish_reason,
                        "errors": parsed.get("errors", []),
                    }
                )
                if cap_recovery is not None:
                    break
                continue
            (output_dir / f"{stage}_output.md").write_text(
                report + "\n", encoding="utf-8"
            )
            write_json(output_dir / f"{stage}_parsed.json", parsed)
            summary = {
                "endpoint": endpoint.rstrip("/"),
                "model": model,
                "system_prompt_sha256": sha256_text(system_prompt),
                "user_prompt_sha256": sha256_text(user_prompt),
                "max_tokens": attempt_max_tokens,
                "primary_max_tokens": max_tokens,
                "recovery_max_tokens": max_tokens * 2,
                "base_seed": base_seed,
                "selected_attempt": attempt + 1,
                "report_sha256": sha256_text(report),
                "generation": result["metadata"],
                "cap_recovery": cap_recovery or {"triggered": False},
                "prior_errors": errors,
                "completed_at": utc_now(),
            }
            write_json(output_dir / f"{stage}_generation.json", summary)
            return report, parsed, {**summary, "response_source": "live_protocol_call"}
        raise RuntimeError(f"{stage} exhausted protocol attempts: {errors}")

    def fuse(
        self,
        *,
        materials: ThreeBlockMaterials,
        output_dir: Path,
        seed: int,
    ) -> dict[str, Any]:
        user_prompt = fusion_user_prompt(materials)
        (output_dir / "fusion_input.md").parent.mkdir(parents=True, exist_ok=True)
        (output_dir / "fusion_input.md").write_text(user_prompt, encoding="utf-8")
        report, parsed, metadata = self._run_protocol_call(
            output_dir=output_dir,
            stage="fusion",
            endpoint=self.config.qwen_endpoint,
            model=self.config.qwen_model,
            system_prompt=FUSION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=self.config.qwen_fusion_max_tokens,
            base_seed=seed,
            parser=parse_fusion_output,
            use_qwen_slot=True,
        )
        return {"report": report, "parsed": parsed, "metadata": metadata}

    def propose_repair(
        self,
        *,
        materials: ThreeBlockMaterials,
        diagnosis: str,
        accepted_ids: list[str],
        output_dir: Path,
        seed: int,
    ) -> dict[str, Any]:
        if not accepted_ids:
            raise ValueError("repair architect requires at least one accepted defect ID")
        user_prompt = repair_user_prompt(materials, diagnosis)
        (output_dir / "repair_input.md").write_text(user_prompt, encoding="utf-8")
        parser = lambda report: parse_repair_output(report, accepted_ids)
        report, parsed, metadata = self._run_protocol_call(
            output_dir=output_dir,
            stage="repair",
            endpoint=self.config.qwen_endpoint,
            model=self.config.qwen_model,
            system_prompt=REPAIR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=self.config.qwen_repair_max_tokens,
            base_seed=seed,
            parser=parser,
            use_qwen_slot=True,
        )
        return {"report": report, "parsed": parsed, "metadata": metadata}

    def rewrite_with_gemma(
        self,
        *,
        materials: ThreeBlockMaterials,
        diagnosis: str,
        repair: str,
        engine: Any,
        output_dir: Path,
        seed: int,
        max_tokens: int,
    ) -> dict[str, Any]:
        user_prompt = resolver_user_prompt(materials, diagnosis, repair)
        (output_dir / "gemma_rewriter_input.md").write_text(
            user_prompt, encoding="utf-8"
        )

        def parse_proof(value: str) -> dict[str, Any]:
            proof = value.strip()
            errors = [] if proof else ["Gemma rewriter returned an empty proof"]
            return {"valid": not errors, "errors": errors}

        proof, _, metadata = self._run_protocol_call(
            output_dir=output_dir,
            stage="gemma_rewriter",
            endpoint=str(engine.endpoint),
            model=str(engine.model),
            system_prompt=RESOLVER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            base_seed=seed,
            parser=parse_proof,
            use_qwen_slot=False,
        )
        return {"proof": proof, "metadata": metadata}
