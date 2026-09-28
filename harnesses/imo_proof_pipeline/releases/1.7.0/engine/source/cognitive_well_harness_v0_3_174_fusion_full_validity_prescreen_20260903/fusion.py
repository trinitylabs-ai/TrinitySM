from __future__ import annotations

import copy
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_171_compact_packet_ce_prescreen_20260903.pipeline import (
    DEFAULT_MAX_TOKENS,
    effective_generation_role,
    sha256_text,
    stable_digest,
    write_text,
)
from cognitive_well_harness_v0_3_171_compact_packet_ce_prescreen_20260903.protocol import (
    parse_decision_tsv,
    render_decision_tsv,
)


HARNESS_VERSION = "v0.3.174-fusion-full-validity-prescreen-20260903"
FUSION_PACKET_ID = "FUSION"
MAX_EXPLANATION_CHARS = 2_400
FUSION_ATTACK_PROMPT = """You are the counterexample-first mathematical attacker
for one complete unverified Fusion repair packet. Keep the packet whole. Your task
is one-sided falsification, not proof generation or proof certification.

Extract every synthesis-relevant affirmative proposition from every field,
especially the resolver brief and preservable material. "Prove X" asserts X. Form
its negation and try hard to find a small explicit legal witness: an included object
that fails, an excluded object that works, a boundary or symmetric case, an exact
calculation, a finite structure or play, or a direct contradiction with the exact
submitted proof. Check every premise, quantifier, domain restriction, operation,
and decisive calculation. A working subfamily does not establish necessity.
Whenever a target says only, exactly, if and only if, or otherwise excludes cases,
test at least one concrete excluded candidate. Prefer small candidates suggested by
an ambient total, conservation law, complementary construction, or small multiple,
not merely variants of the packet's displayed sufficient construction.

For a game, iterative process, or algorithm, a witness about force or impossibility
must handle every adversarial response required by the quantifiers. One favorable
play, one bad reply, or a loop against one proposed strategy does not settle whether
another strategy exists. For a universal positive strategy, require a uniform legal
strategy and well-founded progress under every response. For a negative strategy,
require a legal invariant covering every move.
Also run a backward-closure attack: start from terminal winning features and add a
precursor only when one legal action sends every adversarial successor to a feature
already in the closure. Iterate the closure and compare it with excluded candidates,
ambient totals, and conservation laws. Do not assume the closure consists only of
subdivisions of the packet's displayed base case. Derive every closure operation
from the legal move, including whether two already-winning successor features can
be combined into a winning precursor. Do not reason only forward from one
universally forceable seed; test whether an ambient total decomposes into closure
elements and thereby forces entry into the closure. The two successors may be
covered by two different already-winning features; do not require each successor
to contain the terminal target itself or the same feature. When features carry
values, derive whether the move combines two closure values into a third. If a
legal move creates complementary response features with a fixed total, test whether
that total is a sum of two possibly different closure values and whether the legal
range or continuity realizes the pair. Such a move puts every response in the
closure even if neither response contains the same feature.
Inventory every fixed total induced by the move, including complementary features
created outside the quantity deliberately split. Merely restating that the chosen
quantity equals the sum of its two split parts is not this ambient-total test. If
the closure has valued features, test small sums of two closure values against each
fixed or global total.

Then compare every diagnosis, reviewer assessment, failed obligation, independent
validation, impact, and proof location with the exact submitted proof, and check
cross-field consistency and binding. Evidence that the submitted proof is broken
is never evidence that an affirmative repair target is true. A correct criticism
cannot rescue false guidance. A diagnostic packet need not contain a replacement
proof, and missing proof alone is not a counterexample.

Return exactly one plain-text line with exactly three fields:
PACKET_ID | VERDICT | EXPLANATION

PACKET_ID must be FUSION. VERDICT must be SURVIVES or CHALLENGED. Use CHALLENGED
only for an explicit, checkable refutation of a material packet assertion. Its
explanation must begin PACKET FLAW: and contain CLAIM:, WITNESS:, and CHECK: stating
the exact assertion, witness, premise checks, and failure or direct proof mismatch.
Otherwise use SURVIVES; this means only that this
attack found no refutation, never that the packet is true. A SURVIVES explanation
must begin ALL MATERIAL FIELDS CHECKED: and contain TARGET CHECK:, TARGET CLAIM:,
NEGATION SEARCH:, OUTSIDE TEST:, and BACKWARD CLOSURE:. TARGET CLAIM must transcribe
the affirmative resolver target, not a diagnosis of the submitted proof. OUTSIDE
TEST must name a concrete excluded candidate for a classification, or say not
applicable. BACKWARD CLOSURE must state the derived closure operation and ambient
total check for an adversarial process, or say not applicable. The SUCCESSOR PAIR:
field must state whether two different closure features cover the two responses, or
say not applicable only when there are no adversarial responses. The AMBIENT
DECOMPOSITION: field must name and test a conserved/fixed total against two closure
values, including totals of newly created complementary response features, or state
that no such total exists. It may not merely restate the deliberate split. Name the attacks
attempted and that no complete witness was found, then briefly cover
diagnosis/consistency. The
explanation is mandatory and may not contain a pipe character. Do not return JSON,
Markdown, a code fence, a preface, or another line."""


FUSION_AUDITOR_PROMPT = """You are the final independent, skeptical mathematical
auditor for one complete unverified Fusion repair packet. You receive one attacker
assessment. Keep the packet whole; do not split, rewrite, or improve it.

First cross-examine any proposed refutation. Recompute the explicit witness and
verify every premise, quantifier, domain condition, legal operation, adversarial
branch, and strict failure of the exact packet assertion. Reject an attack based on
a gap, an illegal or incomplete play, a merely suboptimal strategy, or a different
claim. Never deactivate a mathematically positive packet on such an attack.

Whether the attacker challenged or survived, perform an independent second
counterexample attack on every affirmative proposition in the resolver brief and
preservable material. Form its negation; for a classification seek an included
object that fails and an excluded object that works. Test small, boundary,
symmetric, divisibility, invariant, and alternate-construction cases when relevant.
For an exclusivity claim, explicitly test a concrete excluded candidate suggested
by an ambient total, conservation law, complementary construction, or small
multiple; do not spend that test rechecking an included sufficient subfamily.
For a game, iterative process, or algorithm, force/impossibility evidence must cover
every adversarial response required by the quantifiers: one play or a loop against
one strategy is insufficient. A working subfamily cannot establish necessity.
Independently compute the backward winning closure from terminal features, adding a
precursor only when one legal action covers every adversarial successor. Compare the
iterated closure with excluded candidates, ambient totals, and conservation laws;
never restrict it to subdivisions of the packet's displayed base case without proof.
Derive all closure operations from legal moves, including combining already-winning
successor features into a precursor, and test whether an ambient total decomposes
into closure elements. Do not reason only forward from one forceable seed.
The two adversarial successors may be covered by different already-winning
features; never require both to contain the terminal target itself or the same
feature. When features have values, derive and iterate the operation combining two
closure values into their precursor.
If a move creates complementary response values with a fixed total, explicitly test
whether the total decomposes into two possibly different closure values and whether
a legal move can realize that pair. Then every response is already winning even if
the features differ.
Inventory all fixed totals induced by the legal move, especially complementary
response features outside the deliberately split quantity. Merely rewriting the
chosen quantity as its two parts is not an ambient decomposition. Test small sums of
closure values against every fixed and global total.

Then directly compare all diagnoses and locations with the submitted proof and
check all other fields for consistency and exact-proof binding. Evidence that the
proof is broken gives zero support to the repair target. Treat the packet as a
conjunction: one refuted synthesis-relevant field makes it UNSAFE even when another
correct criticism is sound.

Use two verdicts conservatively. Return UNSAFE only with a complete explicit
refutation whose premise and failure checks you can state. Otherwise return
UNVERIFIED. Failure to find a counterexample never certifies truth. UNVERIFIED
remains active and includes both a clean two-pass counterexample survival and any
target lacking a checked proof.

Return exactly one plain-text line with exactly three fields:
PACKET_ID | VERDICT | EXPLANATION

PACKET_ID must be FUSION. VERDICT must be UNSAFE or UNVERIFIED. An UNSAFE
explanation must begin PACKET FLAW: and precisely identify one false or unsafe
Fusion assertion using CLAIM:, WITNESS:, and CHECK: with a decisive mathematical
reason or direct proof comparison.
An UNVERIFIED explanation must begin MATERIAL TARGET UNVERIFIED: and identify the
main unrefuted target using TARGET CLAIM:, NEGATION SEARCH:, OUTSIDE TEST:,
BACKWARD CLOSURE:, and MISSING PROOF:.
Include SUCCESSOR PAIR: to state the different-feature check, or not applicable.
Include AMBIENT DECOMPOSITION: to state the fixed-total test, or that none exists.
TARGET CLAIM must transcribe affirmative resolver guidance rather than the diagnosed
proof defect. The explanation is mandatory and may not contain a pipe character.
Do not return JSON, Markdown, a code fence, a preface, or another line."""


def _single_plain_line(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("model returned an empty verdict")
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if len(lines) == 2 and lines[0] == "PACKET_ID | VERDICT | EXPLANATION":
        stripped = lines[1]
    elif len(lines) != 1:
        raise ValueError("verdict must occupy exactly one physical line")
    if stripped.startswith("```") or stripped.endswith("```"):
        raise ValueError("Markdown fences are not allowed")
    if stripped.startswith("{") or stripped.startswith("["):
        raise ValueError("JSON output is not allowed")
    return stripped


def parse_full_scan_line(
    text: str, *, expected_packet_id: str, role: str
) -> dict[str, str]:
    line = _single_plain_line(text)
    fields = line.split(" | ", 2)
    if len(fields) != 3:
        raise ValueError(
            "verdict must contain exactly PACKET_ID | VERDICT | EXPLANATION"
        )
    packet_id, verdict, explanation = (field.strip() for field in fields)
    if packet_id != expected_packet_id:
        raise ValueError(
            f"verdict packet mismatch: expected {expected_packet_id}, got {packet_id}"
        )
    allowed = (
        {"SURVIVES", "CHALLENGED"}
        if role == "attacker"
        else {"UNSAFE", "UNVERIFIED"}
        if role == "auditor"
        else None
    )
    if allowed is None:
        raise ValueError(f"unsupported full-scan role: {role}")
    if verdict not in allowed:
        raise ValueError(f"unsupported {role} verdict: {verdict}")
    if not explanation:
        raise ValueError("verdict explanation must be nonempty")
    if len(explanation) > MAX_EXPLANATION_CHARS:
        raise ValueError("verdict explanation exceeds the compact output bound")
    unsafe = verdict in {"CHALLENGED", "UNSAFE"}
    required_prefix = (
        "PACKET FLAW:"
        if unsafe
        else "MATERIAL TARGET UNVERIFIED:"
        if verdict == "UNVERIFIED"
        else "ALL MATERIAL FIELDS CHECKED:"
    )
    if not explanation.startswith(required_prefix):
        raise ValueError(f"{verdict} explanation must begin {required_prefix}")
    if verdict == "SURVIVES" and "TARGET CHECK:" not in explanation:
        raise ValueError(f"{verdict} explanation must include TARGET CHECK:")
    if verdict == "SURVIVES":
        for marker in (
            "TARGET CLAIM:",
            "NEGATION SEARCH:",
            "OUTSIDE TEST:",
            "BACKWARD CLOSURE:",
            "SUCCESSOR PAIR:",
            "AMBIENT DECOMPOSITION:",
        ):
            if marker not in explanation:
                raise ValueError(f"{verdict} explanation must include {marker}")
    if verdict == "CHALLENGED":
        for marker in ("CLAIM:", "WITNESS:", "CHECK:"):
            if marker not in explanation:
                raise ValueError(f"{verdict} explanation must include {marker}")
    if verdict == "UNSAFE":
        for marker in ("CLAIM:", "WITNESS:", "CHECK:"):
            if marker not in explanation:
                raise ValueError(f"{verdict} explanation must include {marker}")
        lowered = explanation.lower()
        proof_only_attributions = (
            "submitted proof asserts",
            "submitted proof claims",
            "submitted proof incorrectly asserts",
            "submitted proof incorrectly claims",
            "submitted proof wrongly asserts",
            "submitted proof wrongly claims",
            "the submitted proof's claim",
            "the submitted proof’s claim",
        )
        diagnosis_confirmations = (
            "validates the packet's diagnosis",
            "validating the packet's diagnosis",
            "confirms the packet's diagnosis",
            "confirming the packet's diagnosis",
            "validates the fusion packet's diagnosis",
            "confirms the fusion packet's diagnosis",
        )
        if any(phrase in lowered for phrase in proof_only_attributions):
            raise ValueError(
                f"{verdict} attacks a submitted-proof claim rather than a packet claim"
            )
        if any(phrase in lowered for phrase in diagnosis_confirmations):
            raise ValueError(
                f"{verdict} says its witness confirms rather than refutes the packet"
            )
    if verdict == "UNVERIFIED":
        for marker in (
            "TARGET CLAIM:",
            "NEGATION SEARCH:",
            "OUTSIDE TEST:",
            "BACKWARD CLOSURE:",
            "SUCCESSOR PAIR:",
            "AMBIENT DECOMPOSITION:",
            "MISSING PROOF:",
        ):
            if marker not in explanation:
                raise ValueError(f"{verdict} explanation must include {marker}")
    return {
        "packet_id": packet_id,
        "verdict": verdict,
        "explanation": explanation,
    }


def fusion_scan_user_prompt(*, case: dict[str, Any], content: str) -> str:
    return f"""ORIGINAL PROBLEM
{str(case['problem']).strip()}

SUBMITTED PROOF
{str(case['proof']).strip()}

PACKET ID
{FUSION_PACKET_ID}

COMPLETE FUSION PACKET TEXT
{content}

Return the required one-line verdict for {FUSION_PACKET_ID}."""


def fusion_auditor_user_prompt(
    *, case: dict[str, Any], content: str, attacker: dict[str, str] | None
) -> str:
    assessment = (
        f"{attacker['verdict']} -- {attacker['explanation']}"
        if attacker is not None
        else "UNAVAILABLE -- The attacker call failed mechanically or structurally."
    )
    return f"""ORIGINAL PROBLEM
{str(case['problem']).strip()}

SUBMITTED PROOF
{str(case['proof']).strip()}

PACKET ID
{FUSION_PACKET_ID}

COMPLETE FUSION PACKET TEXT
{content}

ATTACKER ASSESSMENT TO CROSS-EXAMINE
{assessment}

Return the required one-line final auditor verdict for {FUSION_PACKET_ID}."""


def _checkpoint(*, destination: Path, input_sha256: str) -> dict[str, str] | None:
    digest_path = destination / "input.sha256"
    decision_path = destination / "decision.tsv"
    if not digest_path.is_file() and not decision_path.is_file():
        return None
    if decision_path.is_file() and not digest_path.is_file():
        raise ValueError(f"incomplete Fusion prescreen checkpoint: {destination}")
    if digest_path.read_text(encoding="utf-8").strip() != input_sha256:
        raise ValueError(f"Fusion prescreen checkpoint input drift: {destination}")
    if not decision_path.is_file():
        return None
    rows = parse_decision_tsv(decision_path.read_text(encoding="utf-8"))
    if len(rows) != 1 or rows[0]["packet_id"] != FUSION_PACKET_ID:
        raise ValueError(f"invalid Fusion prescreen checkpoint: {destination}")
    return rows[0]


def apply_fusion_decision(
    case: dict[str, Any], decision: dict[str, str], *, decision_path: Path | None
) -> dict[str, Any]:
    if decision["packet_id"] != FUSION_PACKET_ID:
        raise ValueError("Fusion decision has the wrong packet ID")
    filtered = copy.deepcopy(case)
    if decision["status"] == "INACTIVE":
        filtered["fusion"] = None
    elif decision["status"] != "ACTIVE":
        raise ValueError(f"unsupported Fusion status: {decision['status']}")
    filtered["fusion_packet_prescreen"] = {
        "harness_version": HARNESS_VERSION,
        "policy": "configurable_attack_then_final_full_field_audit_exactly_two_calls",
        "status": decision["status"],
        "explanation": decision["explanation"],
        "decision_path": str(decision_path.resolve()) if decision_path else None,
        "whole_packet_text_preserved": True,
        "atomicization": False,
        "one_packet_per_model_request": True,
        "auditor_runs_on_survivors": True,
        "logical_model_calls_per_present_packet": 2,
    }
    return filtered


def run_fusion_prescreen(
    *,
    runtime: Any,
    case: dict[str, Any],
    output_root: Path,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    seed_namespace: str = "v0174:fusion-full-validity-prescreen",
    attacker_role: str = "qwen",
    auditor_role: str = "gemma",
) -> tuple[dict[str, Any], dict[str, str]]:
    fusion = case.get("fusion")
    if fusion is None:
        skipped = copy.deepcopy(case)
        skipped["fusion_packet_prescreen"] = {
            "harness_version": HARNESS_VERSION,
            "policy": "skip_when_no_fusion_packet",
            "status": "SKIPPED_NO_PACKET",
            "explanation": "No Fusion repair packet was present; no model call was made.",
            "decision_path": None,
            "whole_packet_text_preserved": True,
            "atomicization": False,
            "one_packet_per_model_request": True,
            "auditor_runs_on_survivors": True,
            "logical_model_calls_per_present_packet": 0,
        }
        return skipped, {
            "packet_id": FUSION_PACKET_ID,
            "status": "SKIPPED_NO_PACKET",
            "explanation": "No Fusion repair packet was present; no model call was made.",
        }
    if max_tokens < 1:
        raise ValueError("max_tokens must be positive")
    if attacker_role not in {"gemma", "qwen"}:
        raise ValueError(f"unsupported attacker role: {attacker_role}")
    if auditor_role not in {"gemma", "qwen"}:
        raise ValueError(f"unsupported auditor role: {auditor_role}")
    content = str(fusion.get("content") or "")
    if not content.strip():
        raise ValueError(f"empty Fusion packet: {case['case_key']}")

    destination = (
        output_root
        / str(case["problem_key"])
        / str(case["candidate_id"])
        / "fusion"
    )
    digest = stable_digest(
        {
            "harness_version": HARNESS_VERSION,
            "case_key": case["case_key"],
            "problem_sha256": sha256_text(str(case["problem"])),
            "proof_sha256": sha256_text(str(case["proof"])),
            "fusion_content_sha256": sha256_text(content),
            "attack_prompt_sha256": sha256_text(FUSION_ATTACK_PROMPT),
            "auditor_prompt_sha256": sha256_text(FUSION_AUDITOR_PROMPT),
            "attacker_role": attacker_role,
            "auditor_role": auditor_role,
            "max_tokens": max_tokens,
            "seed_namespace": seed_namespace,
        }
    )
    saved = _checkpoint(destination=destination, input_sha256=digest)
    decision_path = destination / "decision.tsv"
    if saved is not None:
        return apply_fusion_decision(
            case, saved, decision_path=decision_path
        ), saved

    write_text(destination / "input.sha256", digest + "\n")
    attack_prompt = fusion_scan_user_prompt(case=case, content=content)
    packet_section = f"COMPLETE FUSION PACKET TEXT\n{content}\n\n"
    if attack_prompt.count(packet_section) != 1:
        raise ValueError("whole Fusion packet was not supplied exactly once")
    write_text(destination / "attacker.user_prompt.txt", attack_prompt)

    mechanical_errors: list[str] = []
    attacker: dict[str, str] | None = None
    try:
        generation = runtime.text(
            role=attacker_role,
            prompt=FUSION_ATTACK_PROMPT,
            user_prompt=attack_prompt,
            destination=destination / "attacker_model_call",
            stage="whole_fusion_packet_full_field_attack",
            temperature=0.2,
            max_tokens=max_tokens,
            seed_label=f"{seed_namespace}:{case['case_key']}:attacker",
        )
        text = str(generation.get("text") or "")
        write_text(destination / "attacker.verdict.txt", text.strip() + "\n")
        attacker = parse_full_scan_line(
            text, expected_packet_id=FUSION_PACKET_ID, role="attacker"
        )
        attacker["effective_role"] = effective_generation_role(
            attacker_role, dict(generation.get("metadata") or {})
        )
    except Exception as error:
        write_text(destination / "attacker.error.txt", traceback.format_exc())
        mechanical_errors.append(f"attacker:{type(error).__name__}")

    auditor: dict[str, str] | None = None
    audit_prompt = fusion_auditor_user_prompt(
        case=case, content=content, attacker=attacker
    )
    if audit_prompt.count(packet_section) != 1:
        raise ValueError("whole Fusion packet was not supplied exactly once to auditor")
    write_text(destination / "auditor.user_prompt.txt", audit_prompt)
    try:
        generation = runtime.text(
            role=auditor_role,
            prompt=FUSION_AUDITOR_PROMPT,
            user_prompt=audit_prompt,
            destination=destination / "auditor_model_call",
            stage="whole_fusion_packet_final_full_field_audit",
            temperature=0.1,
            max_tokens=max_tokens,
            seed_label=f"{seed_namespace}:{case['case_key']}:auditor",
        )
        text = str(generation.get("text") or "")
        write_text(destination / "auditor.verdict.txt", text.strip() + "\n")
        auditor = parse_full_scan_line(
            text, expected_packet_id=FUSION_PACKET_ID, role="auditor"
        )
        auditor["effective_role"] = effective_generation_role(
            auditor_role, dict(generation.get("metadata") or {})
        )
    except Exception as error:
        write_text(destination / "auditor.error.txt", traceback.format_exc())
        mechanical_errors.append(f"auditor:{type(error).__name__}")

    if auditor is not None and auditor["verdict"] == "UNSAFE":
        decision = {
            "packet_id": FUSION_PACKET_ID,
            "status": "INACTIVE",
            "explanation": auditor["explanation"],
        }
    elif auditor is not None and auditor["verdict"] == "UNVERIFIED":
        decision = {
            "packet_id": FUSION_PACKET_ID,
            "status": "ACTIVE",
            "explanation": auditor["explanation"],
        }
    else:
        detail = ",".join(mechanical_errors) or "unknown"
        decision = {
            "packet_id": FUSION_PACKET_ID,
            "status": "ACTIVE",
            "explanation": (
                f"Full-field prescreen incomplete mechanically ({detail}); packet remains active."
            ),
        }

    write_text(decision_path, render_decision_tsv([decision]))
    return apply_fusion_decision(
        case, decision, decision_path=decision_path
    ), decision
