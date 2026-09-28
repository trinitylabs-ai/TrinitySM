from __future__ import annotations

import json
import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator


DISABLED_FEATURES = (
    "apps",
    "browser_use",
    "computer_use",
    "image_generation",
    "in_app_browser",
    "multi_agent",
    "shell_tool",
    "skill_search",
    "standalone_web_search",
    "unified_exec",
)
TOOL_ITEM_TYPES = {
    "command_execution",
    "computer_action",
    "file_change",
    "function_call",
    "image_generation",
    "mcp_tool_call",
    "tool_call",
    "web_search",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def codex_command(output_path: Path, model: str, schema_path: Path) -> list[str]:
    command = ["codex", "exec"]
    for feature in DISABLED_FEATURES:
        command.extend(["--disable", feature])
    command.extend(
        [
            "--skip-git-repo-check",
            "--ephemeral",
            "--ignore-user-config",
            "--strict-config",
            "--model",
            model,
            "--config",
            'model_reasoning_effort="max"',
            "--sandbox",
            "read-only",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            "--json",
            "-",
        ]
    )
    return command


def find_tool_events(output: str) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") or {}
        event_type = str(event.get("type") or "")
        item_type = str(item.get("type") or "")
        if item_type in TOOL_ITEM_TYPES or "tool_call" in event_type:
            violations.append(event)
    return violations


def exact_schema_validate(result: Any, schema_path: Path) -> None:
    schema = read_json(schema_path)
    Draft202012Validator(schema).validate(result)
    if not isinstance(result, dict) or set(result) != set(schema["required"]):
        raise ValueError(f"structured keys do not exactly match {schema_path.name}")


def request_bound_stem(
    *, call_root: Path, stem: str, request_identity: dict[str, Any]
) -> str:
    """Route a changed request beside an immutable cached Terra artifact."""

    result_path = call_root / f"{stem}.json"
    request_path = call_root / f"{stem}.request.json"
    if not result_path.exists() and not request_path.exists():
        return stem
    if request_path.exists() and read_json(request_path) == request_identity:
        return stem
    identity_bytes = json.dumps(
        request_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    digest = hashlib.sha256(identity_bytes).hexdigest()[:16]
    return f"{stem}.request-{digest}"


def terra_json_call(
    *,
    prompt: str,
    schema_path: Path,
    call_root: Path,
    stem: str,
    model: str,
    repo_root: Path,
    validator: Callable[[dict[str, Any]], None],
) -> dict[str, Any]:
    call_root.mkdir(parents=True, exist_ok=True)
    request_identity = {
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "schema_sha256": hashlib.sha256(schema_path.read_bytes()).hexdigest(),
        "model": model,
        "reasoning_effort": "max",
        "sandbox": "read-only",
        "tools_disabled": list(DISABLED_FEATURES),
    }
    stem = request_bound_stem(
        call_root=call_root,
        stem=stem,
        request_identity=request_identity,
    )
    result_path = call_root / f"{stem}.json"
    request_path = call_root / f"{stem}.request.json"
    if result_path.exists():
        if not request_path.exists() or read_json(request_path) != request_identity:
            raise RuntimeError(
                f"request-hash collision or corrupt Terra cache for {call_root / stem}"
            )
        result = read_json(result_path)
        exact_schema_validate(result, schema_path)
        validator(result)
        return result
    write_json(request_path, request_identity)
    prompt_path = call_root / f"{stem}.prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    errors: list[str] = []
    for attempt in range(1, 3):
        partial_path = call_root / f"{stem}.attempt{attempt}.partial.json"
        events_path = call_root / f"{stem}.attempt{attempt}.events.jsonl"
        completed = subprocess.run(
            codex_command(partial_path, model, schema_path),
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=repo_root,
            check=False,
        )
        events_path.write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0:
            errors.append(f"attempt {attempt}: codex exit {completed.returncode}")
            continue
        if find_tool_events(completed.stdout):
            errors.append(f"attempt {attempt}: forbidden Terra tool event")
            continue
        try:
            result = read_json(partial_path)
            exact_schema_validate(result, schema_path)
            validator(result)
        except Exception as error:
            errors.append(f"attempt {attempt}: {type(error).__name__}: {error}")
            continue
        os.replace(partial_path, result_path)
        return result
    raise RuntimeError(f"Terra call {stem} failed closed: {' | '.join(errors)}")
