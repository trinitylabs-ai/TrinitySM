"""Opt-in, single saved-proof audit with the exact lemma statement retained.

No proof rewrite, theorem-specific hints, prior jury output, or new ideal search.
The original experiment is immutable; this produces a separate diagnostic audit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import tool_purpose
from . import pipeline
from .certificate import validate_markdown_budget_forcing
from .rewrite import assert_generic_boundary, write_record
from .saved_witness import audit_statement


STAGE = "modular_exact_evidence_whole_proof_audit"
REPLACEMENT_HEADING = "# Submitted Replacement Proof\n\n"
VIEW_NOTE = """# Compact Audit View

Only the inserted lemma's machine-verified internal derivation is omitted below.
Its exact assumptions, nonzero guards, and conclusion are retained verbatim; the
full derivation remains unchanged in the submitted proof and verified artifact.
Treat only that conditional lemma as established. For certificate-internal
inspectability, rely on the separately checked full artifact, not on its omission
from this view. Check every surrounding calculation, the derivation of every
lemma hypothesis, and the translation of its conclusion. Neither the original
proof nor the rewritten surrounding proof is certified by this fact.

"""
OMISSION = "\n\n[Only the verified internal lemma derivation is omitted from this audit view.]"


def compact_prompt(*, user_prompt, proof, evidence, verification):
    statement = audit_statement(evidence, verification)
    if proof.count(evidence) != 1:
        raise ValueError("proof must contain the exact certificate once")
    if user_prompt.count(REPLACEMENT_HEADING) != 1:
        raise ValueError("audit prompt lacks a unique submitted-proof section")
    prefix, submitted = user_prompt.split(REPLACEMENT_HEADING, 1)
    if submitted.rstrip() != proof:
        raise ValueError("audit prompt does not contain the saved submitted proof")
    before, after = proof.split(evidence, 1)
    view = before + statement + OMISSION + after
    prompt = prefix + VIEW_NOTE + REPLACEMENT_HEADING + view
    return prompt, view, {
        "certificate_characters": len(evidence), "statement_characters": len(statement),
        "omitted_derivation_characters": len(evidence) - len(statement),
        "certificate_sha256": pipeline.base.sha256_text(evidence),
        "statement_sha256": pipeline.base.sha256_text(statement),
        "surrounding_proof_unchanged": True,
    }


def prepare(source, *, cycle=1, with_changes=False):
    source = Path(source).resolve()
    read = lambda name: json.loads((source / name).read_text(encoding="utf-8"))
    manifest, lock = read("manifest.json"), read("protocol_lock.json")
    if manifest["state"] not in ("completed", "failed_closed"):
        raise ValueError("only a stopped synthesis can be independently audited")
    if cycle < 1:
        raise ValueError("cycle must be positive")
    record = manifest["cycles"][cycle - 1]
    call = record["audit_call"]
    model = source / f"04_audit/cycle_{cycle:02d}/model/attempt_{call['attempt']:02d}_cap_{call['cap']}"
    metadata = json.loads((model / f"{STAGE}.pre_budget_forcing.metadata.json").read_text())
    system = (model / f"{STAGE}.prompt.txt").read_text().rstrip()
    user = (model / f"{STAGE}.user_prompt.txt").read_text().rstrip()
    evidence = (source / "01_evidence/evidence.md").read_text().strip()
    verification = read("01_evidence/verification.json")
    proof = (source / f"02_rewrite/cycle_{cycle:02d}/terminal_proof.md").read_text().strip()
    original = (source / "input/source_proof.md").read_text().strip()
    for value, expected in (
        (system, metadata["prompt_sha256"]), (user, metadata["user_prompt_sha256"]),
        (system, lock["auditor_system_sha256"]), (evidence, lock["evidence_sha256"]),
        (original, lock["task"]["source_proof_sha256"]),
    ):
        if pipeline.base.sha256_text(value) != expected:
            raise ValueError("saved synthesis input binding changed")
    if pipeline.synthesis_pipeline._canonical_sha(verification) != lock["verification_sha256"]:
        raise ValueError("saved evidence verification binding changed")
    artifacts = read("01_evidence/source_artifacts.json")
    for row in artifacts.values():
        if pipeline.base.sha256_file(Path(row["path"])) != row["sha256"]:
            raise ValueError("saved exact source artifact changed")
    if user.count(original) != 1 or metadata["stage"] != STAGE:
        raise ValueError("saved original-proof audit context is not uniquely bound")
    prompt, view, details = compact_prompt(user_prompt=user, proof=proof,
        evidence=evidence, verification=verification)
    if with_changes:
        from . import change_audit
        marker = read("contract.json")["evidence_marker"]
        rows = change_audit.detect(original, proof, evidence, marker)
        ledger = change_audit.render(rows)
        prefix, replacement = prompt.split(REPLACEMENT_HEADING, 1)
        prompt = prefix + ledger + "\n\n" + REPLACEMENT_HEADING + replacement
        system += "\n\n" + change_audit.INSTRUCTION
        details.update(change_count=len(rows), change_ledger=rows,
            change_ledger_characters=len(ledger), change_ledger_sha256=pipeline.base.sha256_text(ledger))
    details.update(schema="generic-compact-saved-certificate-audit-v1", source=str(source), cycle=cycle,
        system_prompt_unchanged=not with_changes, old_prompt_characters=len((model / f"{STAGE}.prompt.txt").read_text().rstrip()) + len(user),
        new_prompt_characters=len(system) + len(prompt), original_proof_sha256=pipeline.base.sha256_text(original),
        submitted_proof_sha256=pipeline.base.sha256_text(proof), saved_source_artifacts_checked=len(artifacts),
        old_initial_prompt_tokens=metadata["usage"]["prompt_tokens"], model=metadata["model"],
        endpoint=metadata["endpoint"], config=metadata["config"], maximum_logical_audits=1,
        mandatory_budget_forcing=True, semantic_rejection_retries=0, parser_retries=0,
        prior_audits_or_scores_supplied=False, new_rewrite_calls=0, new_singular_calls=0,
        new_formalization_calls=0, original_run_promoted_or_modified=False)
    details["deterministic_change_review"] = with_changes
    if len(system) + len(prompt) > 180_000:
        raise ValueError("audit prompt exceeds the fixed character budget; no changes were truncated")
    return system, prompt, view, details, bool(lock.get("gap_closure_explanation_required"))


def run(source, output, *, cycle=1, with_changes=False):
    assert_generic_boundary()
    system, user, view, record, closure = prepare(source, cycle=cycle, with_changes=with_changes)
    output = Path(output).resolve()
    if output.is_relative_to(Path(source).resolve()):
        raise ValueError("diagnostic output must not be inside the original synthesis")
    output.mkdir(parents=True, exist_ok=False)
    write_record(output / "profile.json", record)
    write_record(output / "status.json", {**record, "state": "running", "stage": "qwen_audit"})
    pipeline.base.write_text(output / "audit_view.md", view)
    try:
        (output / "model").mkdir()
        pipeline.mandatory_budget_forcing.install()
        generated = pipeline.base.transport.run_openai_chat_generation(
            endpoint=record["endpoint"], model=record["model"], prompt=system,
            user_prompt=user, output_dir=output / "model", stage=STAGE,
            config=pipeline.base.transport.HTTPGenerationConfig(**record["config"]))
        text = str(generated.get("text") or "").strip()
        metadata = generated["metadata"]
        if not text or metadata.get("finish_reason") in ("length", "repetition"):
            raise ValueError("audit response was empty or unfinished")
        forcing = validate_markdown_budget_forcing({"attempt": 1, "cap": record["config"]["max_tokens"],
            "request_timeout_sec": record["config"]["timeout_seconds"], "metadata": metadata},
            expected_stage=STAGE, expected_model=record["model"], canonical_markdown=text)
        pipeline.base.write_text(output / "audit.md", text)
        if with_changes:
            from . import change_audit
            audit = change_audit.parse(text, record["change_ledger"], require_gap_closure=closure)
        else:
            audit = tool_purpose.parse_proof_audit(text, require_gap_closure=closure)
        record.update(state="completed", stage="finished", audit=audit,
            audit_passed=bool(audit["passed"]), budget_forcing=forcing,
            new_continuation_usage=metadata["usage"])
        primary = json.loads((output / f"model/{STAGE}.pre_budget_forcing.metadata.json").read_text())
        record["new_initial_usage"] = primary["usage"]
    except Exception as error:
        record.update(state="failed_closed", stage="finished", error=f"{type(error).__name__}: {error}")
    write_record(output / "status.json", record)
    write_record(output / "result.json", record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--with-changes", action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        print(json.dumps(prepare(args.source, cycle=args.cycle, with_changes=args.with_changes)[3], indent=2))
    else:
        result = run(args.source, args.output, cycle=args.cycle, with_changes=args.with_changes)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["state"] == "completed" else 1)


if __name__ == "__main__":
    main()
