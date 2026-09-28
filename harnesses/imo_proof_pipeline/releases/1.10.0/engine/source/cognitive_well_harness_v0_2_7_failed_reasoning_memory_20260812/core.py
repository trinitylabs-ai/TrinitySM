from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from jsonschema import Draft202012Validator


MODEL = "nvidia/Gemma-4-31B-IT-NVFP4"
EXECUTION_DISCIPLINE = (
    "\n\nHard termination rule: Never repeat a completed round or restart the "
    "analysis. When the stated round budget is exhausted or the error list is "
    "stable, emit the requested final output immediately. Concision is part of "
    "the protocol; uncertainty must be recorded in the verdict rather than "
    "resolved by extending the loop."
)

GRADE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "grading_log",
        "pre_mortem",
        "coroners_report",
        "overall_strategy",
        "strengths",
        "errors",
        "scaffolding_questions",
        "score",
    ],
    "properties": {
        "grading_log": {
            "type": "array",
            "maxItems": 16,
            "items": {"type": "string", "maxLength": 1000},
        },
        "pre_mortem": {"type": "string", "maxLength": 1200},
        "coroners_report": {"type": "string", "maxLength": 2400},
        "overall_strategy": {"type": "string", "maxLength": 2400},
        "strengths": {
            "type": "array",
            "maxItems": 10,
            "items": {"type": "string", "maxLength": 1000},
        },
        "errors": {
            "type": "array",
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["severity", "description", "defense_rejected_because"],
                "properties": {
                    "severity": {"type": "string", "enum": ["slip", "fallacy"]},
                    "description": {"type": "string", "maxLength": 1600},
                    "defense_rejected_because": {"type": "string", "maxLength": 1200},
                },
            },
        },
        "scaffolding_questions": {
            "type": "array",
            "maxItems": 5,
            "items": {"type": "string", "maxLength": 1000},
        },
        "score": {"type": "integer", "minimum": 0, "maximum": 7},
    },
}

CONJECTURE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["conjectures", "negations", "proof"],
    "properties": {
        "conjectures": {"type": "array", "maxItems": 3, "items": {"type": "string"}},
        "negations": {"type": "array", "maxItems": 3, "items": {"type": "string"}},
        "proof": {"type": "string"},
    },
}

FAILED_LEMMA_SCREEN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decisions"],
    "properties": {
        "decisions": {
            "type": "array",
            "maxItems": 3,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "candidate_index",
                    "verdict",
                    "matched_memory_ids",
                    "addressed_failures",
                    "rationale",
                ],
                "properties": {
                    "candidate_index": {"type": "integer", "minimum": 0, "maximum": 2},
                    "verdict": {
                        "type": "string",
                        "enum": [
                            "new",
                            "repaired",
                            "equivalent_refuted",
                            "equivalent_unproved",
                            "equivalent_grader_conflict",
                            "reuses_failed_reasoning",
                            "sibling_duplicate",
                        ],
                    },
                    "matched_memory_ids": {
                        "type": "array",
                        "maxItems": 18,
                        "items": {"type": "string", "minLength": 1, "maxLength": 128},
                    },
                    "addressed_failures": {
                        "type": "array",
                        "maxItems": 8,
                        "items": {"type": "string", "minLength": 1, "maxLength": 1000},
                    },
                    "rationale": {"type": "string", "minLength": 1, "maxLength": 1800},
                },
            },
        }
    },
}

COMBINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["solution_a_analysis", "solution_b_analysis", "decision", "justification"],
    "properties": {
        "solution_a_analysis": {"type": "string"},
        "solution_b_analysis": {"type": "string"},
        "decision": {"type": "string", "enum": ["A", "B"]},
        "justification": {"type": "string"},
    },
}


def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_or_compute(path: Path, compute: Callable[[], Any]) -> Any:
    if path.exists():
        return read_json(path)
    value = compute()
    write_json(path, value)
    return value


def parse_json_object_with_metadata(
    text: str,
    *,
    schema: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Parse an object, allowing only one narrow serialization repair."""

    value = text.strip()
    value = re.sub(r"\A```(?:json)?\s*", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*```\Z", "", value).strip()
    strict_variants = [value]
    start, end = value.find("{"), value.rfind("}")
    if 0 <= start < end:
        strict_variants.append(value[start : end + 1])

    variants: list[tuple[str, str]] = []
    seen: set[str] = set()
    for candidate in strict_variants:
        if candidate not in seen:
            variants.append(("none", candidate))
            seen.add(candidate)
    # A duplicated leading brace is the only automatic repair. Strict parsing
    # above always has precedence, and the repaired object must pass the full
    # caller-provided schema below.
    for candidate in strict_variants:
        if candidate.startswith("{{"):
            repaired = candidate[1:]
            if repaired not in seen:
                variants.append(("drop_one_duplicated_leading_brace", repaired))
                seen.add(repaired)

    validator = Draft202012Validator(schema) if schema is not None else None
    errors: list[str] = []
    for normalization, variant in variants:
        try:
            decoded = json.loads(variant)
        except json.JSONDecodeError as exc:
            errors.append(f"{normalization}: {exc}")
            continue
        if not isinstance(decoded, dict):
            errors.append(f"{normalization}: decoded {type(decoded).__name__}")
            continue
        if validator is not None:
            schema_errors = sorted(validator.iter_errors(decoded), key=lambda row: list(row.path))
            if schema_errors:
                first = schema_errors[0]
                location = ".".join(str(part) for part in first.absolute_path) or "<root>"
                errors.append(f"{normalization}: schema {location}: {first.message}")
                continue
        return decoded, {
            "normalization": normalization,
            "schema_validated": validator is not None,
        }
    raise ValueError("no JSON object: " + " | ".join(errors))


def parse_json_object(
    text: str,
    *,
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    parsed, _ = parse_json_object_with_metadata(text, schema=schema)
    return parsed


_FINAL_GRADE_RE = re.compile(
    r"(?im)^\s*FINAL_GRADE\s*:\s*([0-7])\s*/\s*7\s*$"
)


def parse_plaintext_grade(report: str) -> dict[str, Any]:
    matches = list(_FINAL_GRADE_RE.finditer(report))
    if not matches:
        raise ValueError("grader report is missing a final FINAL_GRADE: N/7 line")
    score = int(matches[-1].group(1))
    if score == 5:
        raise ValueError("grader used the disallowed score 5")
    errors: list[dict[str, str]] = []
    if score == 6:
        errors.append(
            {
                "severity": "slip",
                "description": "See the complete plaintext grading report.",
                "defense_rejected_because": "The report retained a minor slip.",
            }
        )
    elif score <= 4:
        errors.append(
            {
                "severity": "fallacy",
                "description": "See the complete plaintext grading report.",
                "defense_rejected_because": "The report retained an answer-critical gap.",
            }
        )
    return {
        "grading_log": [report],
        "pre_mortem": "Contained in the plaintext grading report.",
        "coroners_report": report,
        "overall_strategy": "Contained in the plaintext grading report.",
        "strengths": [],
        "errors": errors,
        "scaffolding_questions": [],
        "score": score,
        "raw_report": report,
    }


def parallel_map(function: Callable[[Any], Any], items: Iterable[Any], concurrency: int) -> list[Any]:
    values = list(items)
    if concurrency <= 1:
        return [function(item) for item in values]
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        return list(executor.map(function, values))


class ModelEngine:
    def __init__(
        self,
        *,
        endpoint: str,
        model: str,
        master_seed: int,
        concurrency: int,
        raw_dir: Path,
    ) -> None:
        if endpoint.rstrip("/") != "http://127.0.0.1:8020/v1":
            raise ValueError("appendix-faithful one-GPU profile is pinned to GPU 0 port 8020")
        if model != MODEL:
            raise ValueError(f"all roles must use the pinned model {MODEL!r}")
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.master_seed = int(master_seed)
        self.concurrency = int(concurrency)
        self.raw_dir = raw_dir

    def seed(self, namespace: str, index: int = 0) -> int:
        material = f"{self.master_seed}:{namespace}:{index}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1

    @staticmethod
    def _format(name: str, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "json_schema",
            "json_schema": {"name": name, "strict": True, "schema": schema},
        }

    def _call(
        self,
        *,
        prompt: str,
        seed: int,
        temperature: float,
        max_tokens: int,
        schema_name: str | None = None,
        schema: dict[str, Any] | None = None,
        thinking_token_budget: int | None = None,
    ) -> dict[str, Any]:
        from openai import OpenAI

        client = OpenAI(base_url=self.endpoint, api_key="EMPTY", timeout=7200, max_retries=2)
        request: dict[str, Any] = {
            "model": self.model,
            # Appendix F publishes these role instructions as system prompts.
            # Keeping the complete task contract in the system message also
            # prevents later context materials from overriding it.
            "messages": [
                {"role": "system", "content": prompt + EXECUTION_DISCIPLINE},
                {"role": "user", "content": "Execute the requested task now."},
            ],
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens,
            "seed": seed,
            "extra_body": {
                "top_k": 64,
                "chat_template_kwargs": {"enable_thinking": True},
            },
        }
        if schema is not None:
            request["response_format"] = self._format(str(schema_name), schema)
        if thinking_token_budget is not None:
            request["extra_body"]["thinking_token_budget"] = thinking_token_budget
        started = time.perf_counter()
        response = client.chat.completions.create(**request)
        raw = response.model_dump(mode="json")
        message = raw["choices"][0]["message"]
        return {
            "raw": raw,
            "reasoning": str(message.get("reasoning_content") or message.get("reasoning") or ""),
            "final": str(message.get("content") or ""),
            "finish_reason": raw["choices"][0].get("finish_reason"),
            "usage": raw.get("usage") or {},
            "latency_seconds": time.perf_counter() - started,
            "seed": seed,
            "prompt_sha256": sha256(prompt + EXECUTION_DISCIPLINE),
            "message_roles": ["system", "user"],
            "thinking_enabled": True,
            "thinking_token_budget": thinking_token_budget,
            "model": self.model,
            "endpoint": self.endpoint,
        }

    def _saved_response(
        self,
        *,
        path: Path,
        prompt: str,
        seed: int,
        thinking_token_budget: int | None,
    ) -> tuple[dict[str, Any] | None, list[str]]:
        """Load a response only when its authoritative request identity matches.

        Resuming by filename alone is unsafe because an upstream stochastic
        response can change the downstream prompt while retaining the same
        namespace.  The fields below are present in the v0.2.3 artifacts and
        are sufficient to bind a saved response to this exact request.
        """

        if not path.exists():
            return None, ["saved response does not exist"]
        result = read_json(path)
        expected = {
            "prompt_sha256": sha256(prompt + EXECUTION_DISCIPLINE),
            "seed": seed,
            "model": self.model,
            "endpoint": self.endpoint,
            "thinking_token_budget": thinking_token_budget,
        }
        mismatches = [
            f"{key}: saved={result.get(key)!r}, expected={value!r}"
            for key, value in expected.items()
            if result.get(key) != value
        ]
        return (None if mismatches else result), mismatches

    def _load_or_call(
        self,
        *,
        raw_path: Path,
        prompt: str,
        seed: int,
        temperature: float,
        max_tokens: int,
        schema_name: str | None = None,
        schema: dict[str, Any] | None = None,
        thinking_token_budget: int | None = None,
    ) -> tuple[dict[str, Any], str]:
        result, mismatches = self._saved_response(
            path=raw_path,
            prompt=prompt,
            seed=seed,
            thinking_token_budget=thinking_token_budget,
        )
        resume_path = raw_path.with_name(raw_path.stem + "_resume.json")
        if result is not None:
            write_json(
                resume_path,
                {
                    "accepted": True,
                    "response_source": "saved_raw_response",
                    "request_identity_validated": True,
                },
            )
            return result, "saved_raw_response"
        if raw_path.exists():
            write_json(
                resume_path,
                {
                    "accepted": False,
                    "response_source": "saved_raw_response",
                    "request_identity_validated": False,
                    "mismatches": mismatches,
                    "action": "live_inference",
                },
            )
        result = self._call(
            prompt=prompt,
            seed=seed,
            temperature=temperature,
            max_tokens=max_tokens,
            schema_name=schema_name,
            schema=schema,
            thinking_token_budget=thinking_token_budget,
        )
        write_json(raw_path, result)
        return result, "live_inference"

    def text(
        self,
        *,
        prompt: str,
        namespace: str,
        index: int = 0,
        temperature: float = 1.0,
        max_tokens: int = 65_536,
    ) -> dict[str, Any]:
        errors: list[str] = []
        for attempt in range(1, 3):
            raw_path = self.raw_dir / f"{namespace}_{index}_attempt{attempt}.json"
            result, _ = self._load_or_call(
                raw_path=raw_path,
                prompt=prompt,
                seed=self.seed(namespace, index) + attempt - 1,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if result["final"].strip() and result["finish_reason"] != "length":
                return result
            errors.append(f"attempt{attempt}: finish={result['finish_reason']}, chars={len(result['final'])}")
        raise RuntimeError("text generation failed: " + " | ".join(errors))

    def structured(
        self,
        *,
        prompt: str,
        namespace: str,
        schema_name: str,
        schema: dict[str, Any],
        index: int = 0,
        temperature: float = 0.1,
        max_tokens: int = 32_768,
        thinking_token_budget: int = 16_384,
    ) -> dict[str, Any]:
        errors: list[str] = []
        for attempt in range(1, 3):
            raw_path = self.raw_dir / f"{namespace}_{index}_attempt{attempt}.json"
            result, response_source = self._load_or_call(
                raw_path=raw_path,
                prompt=prompt,
                seed=self.seed(namespace, index) + attempt - 1,
                temperature=temperature,
                max_tokens=max_tokens,
                schema_name=schema_name,
                schema=schema,
                thinking_token_budget=thinking_token_budget,
            )
            parse_audit_path = self.raw_dir / f"{namespace}_{index}_attempt{attempt}_parse.json"
            if result["finish_reason"] == "length":
                errors.append(f"attempt{attempt}: output reached max_tokens={max_tokens}")
                write_json(
                    parse_audit_path,
                    {"accepted": False, "response_source": response_source, "error": errors[-1]},
                )
                continue
            try:
                parsed, parse_metadata = parse_json_object_with_metadata(
                    result["final"], schema=schema
                )
            except Exception as exc:
                errors.append(f"attempt{attempt}: {type(exc).__name__}: {exc}")
                write_json(
                    parse_audit_path,
                    {"accepted": False, "response_source": response_source, "error": errors[-1]},
                )
                continue
            parse_audit = {
                "accepted": True,
                "response_source": response_source,
                "request_identity_validated": response_source == "saved_raw_response",
                **parse_metadata,
            }
            write_json(parse_audit_path, parse_audit)
            return {"parsed": parsed, "response": result, "parse_audit": parse_audit}
        raise RuntimeError("structured generation failed: " + " | ".join(errors))

    def grade(
        self,
        *,
        prompt: str,
        namespace: str,
        index: int = 0,
        temperature: float = 0.1,
        max_tokens: int = 65_536,
        thinking_token_budget: int = 16_384,
    ) -> dict[str, Any]:
        """Run the appendix plaintext grader, then extract only its terminal score."""
        errors: list[str] = []
        for attempt in range(1, 3):
            raw_path = self.raw_dir / f"{namespace}_{index}_attempt{attempt}.json"
            result, _ = self._load_or_call(
                raw_path=raw_path,
                prompt=prompt,
                seed=self.seed(namespace, index) + attempt - 1,
                temperature=temperature,
                max_tokens=max_tokens,
                thinking_token_budget=thinking_token_budget,
            )
            if result["finish_reason"] == "length":
                errors.append(f"attempt{attempt}: output reached max_tokens={max_tokens}")
                continue
            try:
                parsed = parse_plaintext_grade(result["final"])
            except Exception as exc:
                errors.append(f"attempt{attempt}: {type(exc).__name__}: {exc}")
                continue
            return {"parsed": parsed, "response": result}
        raise RuntimeError("plaintext grading failed: " + " | ".join(errors))


def validate_grade(grade: dict[str, Any]) -> dict[str, Any]:
    result = dict(grade)
    score = int(result.get("score", -1))
    errors = list(result.get("errors") or [])
    valid_scale = score in {0, 1, 2, 3, 4, 6, 7}
    result["valid_scale"] = valid_scale
    result["effective_score"] = score if valid_scale else 0
    result["perfect"] = valid_scale and score == 7 and not errors
    return result


def mean_grade(grades: list[dict[str, Any]]) -> float:
    return (
        sum(int(row.get("effective_score", row["score"])) for row in grades) / len(grades)
        if grades
        else 0.0
    )
