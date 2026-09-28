from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import (
    pipeline as v084,
)
from cognitive_well_harness_v0_3_99_semantic_obligation_grouping_20260827 import (
    pipeline as v099,
)
from cognitive_well_harness_v0_3_100_current_semantic_ledger_20260827 import (
    pipeline as v100,
)

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
GROUP_TEMPERATURE = 0.1
AUDIT_TEMPERATURE = 0.1
RESOLVE_TEMPERATURE = 0.4


SHARED_GROUP_SYSTEM_PROMPT = r"""You are a conservative semantic organizer of
current unresolved obligations across several proof attempts for one olympiad
problem.

Each supplied local record is already a representative current obligation for one
candidate proof. Group records only when they describe the same mathematical repair
across attempts: the assumptions, required conclusion, and load-bearing argument must
be compatible, and one mathematical repair strategy must close every occurrence.
Candidate-specific notation and proof locations do not prevent a merge, but retain
their local occurrence information. Do not infer that a defect in one proof occurs in
another. Do not solve, repair, close, discard, or change a record.

Do not merge merely because records concern the same theorem, object, technique, or
downstream conclusion. Keep distinct proof-local implementation errors separate when
their repairs differ. A concrete counterexample may join the general obligation it
witnesses; label it WITNESS. A broader report may join only when its repair target is
genuinely the same; label it BROADER. Use SAME for equivalent records. If one record
explicitly contains independent components, it may appear in multiple groups and
every such appearance must be COMPOUND_COMPONENT. Otherwise each ID appears exactly
once.

Return only compact Markdown. Repeat this exact block until every supplied ID is
covered:

## Group
- Canonical obligation: <one atomic cross-attempt mathematical obligation>
- Proof location: <generic interface plus candidate-local locations when useful>
- Logical scope: <assumptions and conclusion governed by this obligation>
- Minimum repair: <one repair strategy that closes every occurrence>
- Members: OB1:SAME, OB2:WITNESS
- Reason: <why these records share one repair target>

Use only supplied IDs and relation labels SAME, WITNESS, BROADER, or
COMPOUND_COMPONENT. Keep every field on one physical line. Do not return JSON, fences,
scores, verdicts, or extra sections.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Prefer separate singleton groups over a speculative merge."""


SHARED_AUDIT_SYSTEM_PROMPT = r"""You are the independent global auditor of a
proposed shared obligation bank for several proof attempts of one olympiad problem.

For each proposal, decide whether one mathematical repair strategy really closes
every local record under a compatible logical scope. Candidate-local notation may
differ, but a defect found only in one proof must not be imputed to another. You may
KEEP a proposal or SPLIT it into a complete partition. You may not move records
between proposals, merge distinct proposals, drop or add a record, solve the problem,
or repair a proof.

When the same source ID occurs in multiple proposals as COMPOUND_COMPONENT, a later
partition may be REDUNDANT_WITH the earliest proposal only if it repeats the same
component and shares that source ID. Otherwise retain both.

Return only compact Markdown, one block per proposal in supplied order:

## PG1
- Decision: KEEP
- Partitions: OB1, OB2
- Dispositions: KEEP
- Reason: <why one repair suffices>

or

## PG2
- Decision: SPLIT
- Partitions: OB3 || OB4
- Dispositions: KEEP || REDUNDANT_WITH PG1
- Reason: <why repairs differ and why any repeated component is redundant>

Every member must occur exactly once in its proposal partitions. KEEP has one
partition; SPLIT has at least two. Dispositions correspond one-for-one with
partitions. A REDUNDANT_WITH target must be an earlier proposal sharing at least one
member ID. Do not return JSON, fences, scores, verdicts, or extra sections.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. When equivalence is uncertain, split and keep."""


RESOLVER_SYSTEM_PROMPT = r"""You are an expert olympiad proof resolver. Rewrite one
submitted proof into a complete, rigorous, self-contained solution of the original
problem.

The supplied obligation bank is advisory diagnostic evidence, not established
mathematics. Independently verify every item against the problem and the submitted
proof. MANDATORY records have an occurrence explicitly mapped to this proof: repair
each genuine one, including its surrounding assumptions, application, and downstream
dependencies. OPTIONAL CROSS-PROOF records come from other attempts: use them only as
warnings, alternative routes, or reusable insight, and never claim that they occur in
this proof without checking.

Choose the least disruptive rigorous route that actually works, but you may replace a
local span, restructure the argument, or write a fresh proof when necessary. Do not
preserve a familiar approach at the cost of rigor. Check all load-bearing algebra,
logic, quantifiers, cases, boundary conditions, and stated conclusions.

Return only the complete replacement proof, with no patch notation and no discussion
of reviewers, ledgers, prompts, candidates, or workflow. If a complete solution cannot
be justified, return the strongest rigorous partial proof and explicitly identify its
first unresolved mathematical gap; never conceal a gap behind confident prose.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort on this problem. Use the maximum reasoning effort available before
producing the final response. Do not finalize merely because a plausible answer or
familiar pattern has been found."""


def _load_problem(path: Path) -> str:
    return v099.load_problem(path)


def load_cases(source_run: Path) -> list[dict[str, Any]]:
    source_run = source_run.resolve()
    manifest_path = source_run / "manifest.json"
    summary_path = source_run / "summary.json"
    if not manifest_path.is_file() or not summary_path.is_file():
        raise ValueError(f"source run lacks manifest/summary: {source_run}")
    manifest = v099.load_json(manifest_path)
    summary = v099.load_json(summary_path)
    if summary.get("state") != "completed":
        raise ValueError("source v0.3.100 run is not completed")
    if not str(manifest.get("schema") or "").startswith("cognitive-well-v0100-"):
        raise ValueError("v0.3.101 consumes a completed v0.3.100 run")
    upstream = Path(str(manifest["source_run"])).resolve()
    upstream_manifest = v099.load_json(upstream / "manifest.json")
    upstream_by_case = {
        str(row["case_id"]): row for row in upstream_manifest.get("cases") or []
    }
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in manifest.get("cases") or []:
        case_id = str(raw.get("case_id") or "").strip()
        if not case_id or case_id in seen or case_id not in upstream_by_case:
            raise ValueError(f"missing, duplicate, or unbound case: {case_id!r}")
        seen.add(case_id)
        upstream_case = upstream_by_case[case_id]
        problem_path = Path(str(upstream_case["problem_path"])).resolve()
        proof_path = Path(str(raw["proof_path"])).resolve()
        ledger_path = source_run / "cases" / case_id / "current_semantic_obligation_ledger.json"
        for path in (problem_path, proof_path, ledger_path):
            if not path.is_file():
                raise FileNotFoundError(path)
        proof = proof_path.read_text(encoding="utf-8").strip()
        if v099.sha256_text(proof) != str(raw["proof_sha256"]):
            raise ValueError(f"proof hash drift for {case_id}")
        ledger = v099.load_json(ledger_path)
        groups = [dict(row) for row in ledger.get("current_representative_ledger") or []]
        if len(groups) != int(ledger.get("current_representative_group_count", -1)):
            raise ValueError(f"invalid current representative ledger for {case_id}")
        cases.append(
            {
                "case_id": case_id,
                "problem_id": str(raw["problem_id"]),
                "candidate_id": str(raw["candidate_id"]),
                "problem_path": str(problem_path),
                "problem": _load_problem(problem_path),
                "proof_path": str(proof_path),
                "proof": proof,
                "proof_sha256": str(raw["proof_sha256"]),
                "ledger_path": str(ledger_path.resolve()),
                "ledger_sha256": v099.file_sha256(ledger_path),
                "local_groups": groups,
            }
        )
    if not cases:
        raise ValueError("source run has no cases")
    return cases


def build_problem_jobs(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        buckets[case["problem_id"]].append(case)
    jobs: list[dict[str, Any]] = []
    for problem_id in sorted(buckets):
        problem_cases = buckets[problem_id]
        problems = {case["problem"] for case in problem_cases}
        if len(problems) != 1:
            raise ValueError(f"problem statement drift inside {problem_id}")
        local_records: list[dict[str, Any]] = []
        pseudo_entries: list[dict[str, str]] = []
        for case in problem_cases:
            for group in case["local_groups"]:
                obligation_id = f"OB{len(local_records) + 1}"
                local_ref = f"{case['case_id']}:{group['semantic_group_id']}"
                pseudo_entries.append({"obligation_id": obligation_id})
                local_records.append(
                    {
                        "obligation_id": obligation_id,
                        "local_group_ref": local_ref,
                        "case_id": case["case_id"],
                        "candidate_id": case["candidate_id"],
                        "local_group_id": group["semantic_group_id"],
                        "canonical_obligation": group["canonical_obligation"],
                        "proof_location": group["proof_location"],
                        "logical_scope": group["logical_scope"],
                        "minimum_repair": group["minimum_repair"],
                        "local_member_count": group["member_count"],
                        "local_member_refs": [
                            {
                                "obligation_id": member["obligation_id"],
                                "source": member.get("source"),
                                "phase": member.get("phase"),
                                "current_issue": member.get("current_issue"),
                            }
                            for member in group["members"]
                        ],
                    }
                )
        jobs.append(
            {
                "case_id": problem_id,
                "problem_id": problem_id,
                "problem": problem_cases[0]["problem"],
                "cases": problem_cases,
                "candidate_proofs": [
                    {
                        "case_id": case["case_id"],
                        "candidate_id": case["candidate_id"],
                        "proof": case["proof"],
                    }
                    for case in problem_cases
                ],
                "local_records": local_records,
                "pseudo_entries": pseudo_entries,
            }
        )
    return jobs


def shared_proposal_user_prompt(job: dict[str, Any]) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + job["problem"].strip()
        + "\n\n# CANDIDATE PROOFS\n\n"
        + json.dumps(job["candidate_proofs"], ensure_ascii=False, indent=2)
        + "\n\n# LOCAL CURRENT REPRESENTATIVE GROUPS\n\n"
        + json.dumps(job["local_records"], ensure_ascii=False, indent=2)
        + "\n\nGroup every supplied local record now.\n"
    )


def shared_audit_user_prompt(job: dict[str, Any]) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + job["problem"].strip()
        + "\n\n# CANDIDATE PROOFS\n\n"
        + json.dumps(job["candidate_proofs"], ensure_ascii=False, indent=2)
        + "\n\n# LOCAL CURRENT REPRESENTATIVE GROUPS\n\n"
        + json.dumps(job["local_records"], ensure_ascii=False, indent=2)
        + "\n\n# ALL GEMMA PROPOSED SHARED GROUPS\n\n"
        + json.dumps(job["proposal"]["proposal_groups"], ensure_ascii=False, indent=2)
        + "\n\nAudit every proposal now.\n"
    )


def run_shared_proposal(
    *, job: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return v099.load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt = shared_proposal_user_prompt(job)
    identity = v099.sha256_text(SHARED_GROUP_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{job['problem_id']}:shared_proposal:{identity}"
    runtime = v084.runtime_for(endpoint, v099.stable_seed(label), GEMMA_MODEL)
    generated = runtime.text(
        role="gemma",
        prompt=SHARED_GROUP_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"shared_problem_group_proposal_{identity}",
        temperature=GROUP_TEMPERATURE,
        max_tokens=8_000,
        seed_label=label,
    )
    raw = str(generated["text"])
    recovery_mode = "primary"
    primary_error: str | None = None
    try:
        groups = v099.parse_group_proposal(text=raw, source_entries=job["pseudo_entries"])
    except Exception as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "format_retry"
        retry = runtime.text(
            role="gemma",
            prompt=SHARED_GROUP_SYSTEM_PROMPT,
            user_prompt=v099._format_retry_prompt(
                task_prompt=prompt, malformed=raw, error=error
            ),
            destination=output_dir / "format_retry",
            stage=f"shared_problem_group_proposal_retry_{identity}",
            temperature=GROUP_TEMPERATURE,
            max_tokens=6_000,
            seed_label=label + ":format_retry",
        )
        generated = retry
        groups = v099.parse_group_proposal(
            text=str(retry["text"]), source_entries=job["pseudo_entries"]
        )
    result = {
        "schema": "cognitive-well-v0101-shared-proposal-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "problem_id": job["problem_id"],
        "proposal_group_count": len(groups),
        "proposal_groups": groups,
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run_shared_audit(
    *, job: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return v099.load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    proposals = job["proposal"]["proposal_groups"]
    prompt = shared_audit_user_prompt(job)
    identity = v099.sha256_text(SHARED_AUDIT_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{job['problem_id']}:shared_audit:{identity}"
    runtime = v084.runtime_for(endpoint, v099.stable_seed(label), QWEN_MODEL)
    generated = runtime.text(
        role="qwen",
        prompt=SHARED_AUDIT_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"shared_problem_group_audit_{identity}",
        temperature=AUDIT_TEMPERATURE,
        max_tokens=6_000,
        seed_label=label,
    )
    raw = str(generated["text"])
    recovery_mode = "primary"
    primary_error: str | None = None
    try:
        audits = v100.parse_global_audit(text=raw, proposal_groups=proposals)
    except Exception as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "format_retry"
        retry = runtime.text(
            role="qwen",
            prompt=SHARED_AUDIT_SYSTEM_PROMPT,
            user_prompt=v099._format_retry_prompt(
                task_prompt=prompt, malformed=raw, error=error
            ),
            destination=output_dir / "format_retry",
            stage=f"shared_problem_group_audit_retry_{identity}",
            temperature=AUDIT_TEMPERATURE,
            max_tokens=4_000,
            seed_label=label + ":format_retry",
        )
        generated = retry
        audits = v100.parse_global_audit(
            text=str(retry["text"]), proposal_groups=proposals
        )
    result = {
        "schema": "cognitive-well-v0101-shared-audit-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "problem_id": job["problem_id"],
        "audit_count": len(audits),
        "audits": audits,
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def materialize_shared_bank(job: dict[str, Any]) -> dict[str, Any]:
    local_by_id = {row["obligation_id"]: row for row in job["local_records"]}
    audit_by_id = {row["proposal_group_id"]: row for row in job["audit"]["audits"]}
    shared_groups: list[dict[str, Any]] = []
    redundancy_links: list[dict[str, Any]] = []
    for proposal in job["proposal"]["proposal_groups"]:
        proposal_id = proposal["proposal_group_id"]
        audit = audit_by_id[proposal_id]
        relation_by_id = {
            member["obligation_id"]: member["relation"] for member in proposal["members"]
        }
        for partition_index, (partition, disposition) in enumerate(
            zip(audit["partitions"], audit["dispositions"], strict=True), start=1
        ):
            if disposition["disposition"] == "REDUNDANT_WITH":
                redundancy_links.append(
                    {
                        "source_proposal_group_id": proposal_id,
                        "source_partition_index": partition_index,
                        "local_record_ids": partition,
                        "redundant_with_proposal_group_id": disposition["target"],
                        "audit_reason": audit["reason"],
                    }
                )
                continue
            complete = set(partition) == set(relation_by_id)
            if complete:
                canonical = {
                    key: proposal[key]
                    for key in (
                        "canonical_obligation",
                        "proof_location",
                        "logical_scope",
                        "minimum_repair",
                    )
                }
            else:
                representative = max(
                    (local_by_id[item] for item in partition),
                    key=lambda row: (len(row["canonical_obligation"]), row["obligation_id"]),
                )
                canonical = {
                    "canonical_obligation": representative["canonical_obligation"],
                    "proof_location": " | ".join(
                        sorted({local_by_id[item]["proof_location"] for item in partition})
                    ),
                    "logical_scope": representative["logical_scope"],
                    "minimum_repair": representative["minimum_repair"],
                }
            occurrences = [
                {
                    **local_by_id[item],
                    "relation": relation_by_id[item],
                }
                for item in partition
            ]
            shared_groups.append(
                {
                    "shared_group_id": f"SG{len(shared_groups) + 1}",
                    "source_proposal_group_id": proposal_id,
                    "source_partition_index": partition_index,
                    "audit_decision": audit["decision"],
                    **canonical,
                    "occurrence_count": len(occurrences),
                    "applicable_case_ids": sorted({row["case_id"] for row in occurrences}),
                    "applicable_candidate_ids": sorted(
                        {row["candidate_id"] for row in occurrences}
                    ),
                    "occurrences": occurrences,
                    "proposal_reason": proposal["reason"],
                    "audit_reason": audit["reason"],
                }
            )
    represented = {
        row["obligation_id"]
        for group in shared_groups
        for row in group["occurrences"]
    }
    expected = set(local_by_id)
    if represented != expected:
        raise ValueError(
            f"shared bank coverage mismatch: missing={sorted(expected - represented)} "
            f"extra={sorted(represented - expected)}"
        )
    for case in job["cases"]:
        expected_refs = {
            f"{case['case_id']}:{group['semantic_group_id']}"
            for group in case["local_groups"]
        }
        actual_refs = {
            row["local_group_ref"]
            for group in shared_groups
            for row in group["occurrences"]
            if row["case_id"] == case["case_id"]
        }
        if expected_refs != actual_refs:
            raise ValueError(f"candidate applicability drift for {case['case_id']}")
    return {
        "schema": "cognitive-well-v0101-shared-problem-obligation-bank-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_id": job["problem_id"],
        "candidate_count": len(job["cases"]),
        "local_representative_group_count": len(job["local_records"]),
        "shared_group_count": len(shared_groups),
        "shared_reduction_count": len(job["local_records"]) - len(shared_groups),
        "shared_groups": shared_groups,
        "cross_group_redundancy_links": redundancy_links,
    }


def resolver_packets(
    *, case: dict[str, Any], bank: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mandatory: list[dict[str, Any]] = []
    optional: list[dict[str, Any]] = []
    for group in bank["shared_groups"]:
        core = {
            "shared_group_id": group["shared_group_id"],
            "canonical_obligation": group["canonical_obligation"],
            "logical_scope": group["logical_scope"],
            "minimum_repair": group["minimum_repair"],
        }
        matching = [
            row for row in group["occurrences"] if row["case_id"] == case["case_id"]
        ]
        if matching:
            mandatory.append(core | {"this_proof_occurrences": matching})
        else:
            optional.append(
                core
                | {
                    "originating_candidate_ids": group["applicable_candidate_ids"],
                    "cross_proof_warning_only": True,
                }
            )
    expected = len(case["local_groups"])
    actual = sum(len(row["this_proof_occurrences"]) for row in mandatory)
    if actual != expected:
        raise ValueError(
            f"resolver packet lost local groups for {case['case_id']}: {actual}/{expected}"
        )
    return mandatory, optional


def resolver_user_prompt(
    *, case: dict[str, Any], mandatory: list[dict[str, Any]], optional: list[dict[str, Any]]
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + case["problem"].strip()
        + "\n\n# SUBMITTED PROOF TO REPLACE\n\n"
        + case["proof"].strip()
        + "\n\n# MANDATORY CURRENT-PROOF OBLIGATIONS\n\n"
        + json.dumps(mandatory, ensure_ascii=False, indent=2)
        + "\n\n# OPTIONAL CROSS-PROOF WARNINGS OR ALTERNATIVE ROUTES\n\n"
        + json.dumps(optional, ensure_ascii=False, indent=2)
        + "\n\nWrite the complete replacement proof now.\n"
    )


def run_resolver(
    *, case: dict[str, Any], bank: dict[str, Any], endpoint: str,
    output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return v099.load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    mandatory, optional = resolver_packets(case=case, bank=bank)
    prompt = resolver_user_prompt(case=case, mandatory=mandatory, optional=optional)
    identity = v099.sha256_text(RESOLVER_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{case['case_id']}:shared_bank_resolve:{identity}"
    runtime = v084.runtime_for(endpoint, v099.stable_seed(label), GEMMA_MODEL)
    generated = runtime.text(
        role="gemma",
        prompt=RESOLVER_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"shared_bank_complete_proof_resolve_{identity}",
        temperature=RESOLVE_TEMPERATURE,
        max_tokens=32_768,
        seed_label=label,
    )
    proof = str(generated["text"]).strip()
    if not proof:
        raise ValueError(f"empty resolver output for {case['case_id']}")
    proof_path = output_dir / "resolved_proof.md"
    proof_path.write_text(proof + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v0101-shared-bank-resolve-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "case_id": case["case_id"],
        "problem_id": case["problem_id"],
        "candidate_id": case["candidate_id"],
        "source_proof_path": case["proof_path"],
        "source_proof_sha256": case["proof_sha256"],
        "shared_bank_sha256": v099.sha256_text(
            json.dumps(bank, ensure_ascii=False, sort_keys=True)
        ),
        "mandatory_shared_group_count": len(mandatory),
        "mandatory_local_occurrence_count": sum(
            len(row["this_proof_occurrences"]) for row in mandatory
        ),
        "optional_cross_proof_group_count": len(optional),
        "resolved_proof_path": str(proof_path.resolve()),
        "resolved_proof_sha256": v099.sha256_text(proof),
        "temperature": RESOLVE_TEMPERATURE,
        "max_tokens": 32_768,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run(
    *, source_run: Path, output_dir: Path,
    gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT,
    qwen_endpoint: str = DEFAULT_QWEN_ENDPOINT,
    group_workers: int = 2, audit_workers: int = 2, resolver_workers: int = 2,
    seed_namespace: str = "v0101", dry_run: bool = False,
) -> dict[str, Any]:
    if min(group_workers, audit_workers, resolver_workers) < 1:
        raise ValueError("all batch worker counts must be positive")
    source_run = source_run.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = load_cases(source_run)
    problem_jobs = build_problem_jobs(cases)
    manifest = {
        "schema": "cognitive-well-v0101-shared-problem-ledger-resolve-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_run": str(source_run),
        "source_run_manifest_sha256": v099.file_sha256(source_run / "manifest.json"),
        "models": {"proposal": GEMMA_MODEL, "audit": QWEN_MODEL, "resolver": GEMMA_MODEL},
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "qwen_endpoint": qwen_endpoint,
            "group_workers": group_workers,
            "audit_workers": audit_workers,
            "resolver_workers": resolver_workers,
            "gemma_precision": "BF16",
            "gemma_mtp": 4,
            "reasoning_effort": "max",
        },
        "temperatures": {
            "shared_group_proposal": GROUP_TEMPERATURE,
            "shared_group_audit": AUDIT_TEMPERATURE,
            "complete_proof_resolve": RESOLVE_TEMPERATURE,
        },
        "protocol": {
            "shared_bank_unit": "problem",
            "local_input_unit": "v0.3.100_current_representative_group",
            "problem_specific_prompting": False,
            "per_proof_applicability_map": True,
            "current_proof_obligations_are_mandatory_advisory": True,
            "cross_proof_obligations_are_optional_advisory": True,
            "resolver_returns_complete_proof": True,
            "post_resolver_audit_in_this_harness": False,
        },
        "batch_plan": {
            "gemma_shared_proposals": {"jobs": len(problem_jobs), "concurrency": group_workers},
            "qwen_shared_audits": {"jobs": len(problem_jobs), "concurrency": audit_workers},
            "gemma_proof_resolves": {"jobs": len(cases), "concurrency": resolver_workers},
        },
        "prompt_sha256": {
            "shared_proposal": v099.sha256_text(SHARED_GROUP_SYSTEM_PROMPT),
            "shared_audit": v099.sha256_text(SHARED_AUDIT_SYSTEM_PROMPT),
            "resolver": v099.sha256_text(RESOLVER_SYSTEM_PROMPT),
        },
        "problems": [
            {
                "problem_id": job["problem_id"],
                "candidate_count": len(job["cases"]),
                "local_representative_group_count": len(job["local_records"]),
            }
            for job in problem_jobs
        ],
        "cases": [
            {
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
                "local_representative_group_count": len(case["local_groups"]),
            }
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})
    if dry_run:
        summary = {
            "schema": "cognitive-well-v0101-dry-run-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "problem_count": len(problem_jobs),
            "case_count": len(cases),
            "local_representative_group_count": sum(
                len(job["local_records"]) for job in problem_jobs
            ),
            "planned_model_calls": {
                "gemma_shared_proposals": len(problem_jobs),
                "qwen_shared_audits": len(problem_jobs),
                "gemma_complete_proof_resolves": len(cases),
                "normal_total": 2 * len(problem_jobs) + len(cases),
            },
            "completed_at": utc_now(),
        }
        write_json(output_dir / "summary.json", summary)
        write_json(output_dir / "status.json", {"state": "dry_run_completed", "stage": "done", "updated_at": utc_now()})
        return summary

    write_json(output_dir / "status.json", {"state": "running", "stage": "gemma_shared_problem_proposal_batch", "updated_at": utc_now()})

    def proposal_task(job: dict[str, Any]) -> None:
        job_dir = output_dir / "problems" / job["problem_id"]
        job["proposal"] = run_shared_proposal(
            job=job, endpoint=gemma_endpoint,
            output_dir=job_dir / "01_gemma_shared_proposal",
            seed_namespace=seed_namespace,
        )

    v099.run_parallel(name="shared-proposal", jobs=problem_jobs, workers=group_workers, task=proposal_task)
    write_json(output_dir / "status.json", {"state": "running", "stage": "qwen_shared_problem_audit_batch", "updated_at": utc_now()})

    def audit_task(job: dict[str, Any]) -> None:
        job_dir = output_dir / "problems" / job["problem_id"]
        job["audit"] = run_shared_audit(
            job=job, endpoint=qwen_endpoint,
            output_dir=job_dir / "02_qwen_shared_audit",
            seed_namespace=seed_namespace,
        )
        job["bank"] = materialize_shared_bank(job)
        write_json(job_dir / "shared_problem_obligation_bank.json", job["bank"])

    v099.run_parallel(name="shared-audit", jobs=problem_jobs, workers=audit_workers, task=audit_task)
    bank_by_problem = {job["problem_id"]: job["bank"] for job in problem_jobs}
    write_json(output_dir / "status.json", {"state": "running", "stage": "gemma_complete_proof_resolve_batch", "updated_at": utc_now()})
    case_jobs = [{"case_id": case["case_id"], "case": case} for case in cases]

    def resolver_task(job: dict[str, Any]) -> None:
        case = job["case"]
        case["resolve"] = run_resolver(
            case=case, bank=bank_by_problem[case["problem_id"]],
            endpoint=gemma_endpoint,
            output_dir=output_dir / "cases" / case["case_id"] / "03_gemma_shared_bank_resolve",
            seed_namespace=seed_namespace,
        )

    v099.run_parallel(name="proof-resolve", jobs=case_jobs, workers=resolver_workers, task=resolver_task)
    rows = [
        {
            "case_id": case["case_id"],
            "problem_id": case["problem_id"],
            "candidate_id": case["candidate_id"],
            "mandatory_shared_group_count": case["resolve"]["mandatory_shared_group_count"],
            "mandatory_local_occurrence_count": case["resolve"]["mandatory_local_occurrence_count"],
            "optional_cross_proof_group_count": case["resolve"]["optional_cross_proof_group_count"],
            "resolved_proof_path": case["resolve"]["resolved_proof_path"],
            "resolved_proof_sha256": case["resolve"]["resolved_proof_sha256"],
        }
        for case in cases
    ]
    summary = {
        "schema": "cognitive-well-v0101-shared-problem-ledger-resolve-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "problem_count": len(problem_jobs),
        "case_count": len(cases),
        "local_representative_group_count": sum(len(job["local_records"]) for job in problem_jobs),
        "shared_group_count": sum(job["bank"]["shared_group_count"] for job in problem_jobs),
        "shared_reduction_count": sum(job["bank"]["shared_reduction_count"] for job in problem_jobs),
        "rows": rows,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "status.json", {"state": "completed", "stage": "done", "updated_at": utc_now()})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Shared per-problem ledger and batched proof replay")
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--qwen-endpoint", default=DEFAULT_QWEN_ENDPOINT)
    parser.add_argument("--group-workers", type=int, default=2)
    parser.add_argument("--audit-workers", type=int, default=2)
    parser.add_argument("--resolver-workers", type=int, default=2)
    parser.add_argument("--seed-namespace", default="v0101")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run(
        source_run=args.source_run,
        output_dir=args.output_dir,
        gemma_endpoint=args.gemma_endpoint,
        qwen_endpoint=args.qwen_endpoint,
        group_workers=args.group_workers,
        audit_workers=args.audit_workers,
        resolver_workers=args.resolver_workers,
        seed_namespace=args.seed_namespace,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
