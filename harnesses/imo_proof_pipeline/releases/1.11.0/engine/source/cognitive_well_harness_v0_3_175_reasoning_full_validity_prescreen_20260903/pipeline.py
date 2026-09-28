from __future__ import annotations

import concurrent.futures
import copy
import re
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_171_compact_packet_ce_prescreen_20260903.pipeline import (
    DEFAULT_MAX_CONCURRENCY,
    DEFAULT_MAX_TOKENS,
    collect_nh_packets,
    safe_component,
    sha256_text,
    stable_digest,
    write_text,
)
from cognitive_well_harness_v0_3_171_compact_packet_ce_prescreen_20260903.protocol import (
    parse_decision_tsv,
    render_decision_tsv,
)


HARNESS_VERSION = "v0.3.175-reasoning-full-validity-prescreen-20260903"
MAX_EXPLANATION_CHARS = 2_400
NUMBERED_REFERENCE_GUARD_VERSION = "v1"
QUANTIFIER_WITNESS_GUARD_VERSION = "v1"
SEQUENCE_LEGALITY_GUARD_VERSION = "v1"


REASONING_ATTACK_PROMPT = """You are the counterexample-first mathematical attacker
for one complete unverified reasoning packet. Keep the packet whole. Attack the
packet, not the submitted proof, and do not summarize, rewrite, or improve it.

Inventory every synthesis-relevant assertion in the packet: its description of the
submitted proof, defect diagnosis, proposed witness, derivation, lemma, repair
route, preserved claim, and any stated or implied necessity, sufficiency, or
impossibility. Treat the whole packet as a conjunction: a correct central diagnosis
does not excuse a false material side claim. Check every sentence, including case
tails and qualifiers such as any, every, only, always, neither, cannot, and unless,
against the exact submitted proof and original problem.
Preserve the packet's exact logical force. A question or request to test another
case is not an assertion. A declarative mathematical proposition remains a claim
even when hedged by words such as seems, likely, apparently, plausibly, or suggests;
the hedge lowers confidence but does not erase refutable content. A calculation for
one selected move or conditional branch does not assert force, necessity, or
impossibility. Never strengthen a packet's wording to create the claim you attack;
any implied claim must be logically entailed by the packet text.
Resolve pronouns, labels, and numbered options in their nearest explicit local
scope. If the packet introduces an enumeration, do not silently rebind its numbers
to a different enumeration in the proof. A representative example of a case type
is not automatically an exhaustive check of every concrete choice in that type.
Ambiguity is not a counterexample: if a reference has multiple reasonable local
bindings, use CHALLENGED only when the explicit refutation works under every such
binding. Otherwise preserve the packet.
First determine the packet's stance toward each quoted or repeated proof claim:
ENDORSES when it uses or corroborates the claim as true, CRITICIZES when it asserts
the claim is false or unsupported, and QUOTES/UNCLEAR when it only reports it. An
endorsed false lemma is a false packet claim and must be challenged. A refutation
of a criticized lemma normally confirms the packet. Mere quotation is not
endorsement. If you find a proof flaw unrelated to any packet assertion, do not
manufacture a packet challenge; preserve the packet and report the independent
issue under PROOF ALARM.
If the packet says the proof is wrong and your calculation also shows the proof is
wrong, that confirms the packet and is not a challenge. To refute a diagnosis, show
that the packet misquotes the proof, uses an illegal witness, makes a false
calculation, or draws a conclusion that fails although its packet premises hold.

Form the negation of each material packet claim and seek a small explicit legal
witness. Test boundaries, equality, signs, parity, residues, symmetric and repeated
objects, excluded candidates, exact substitutions, and alternate constructions.
Do not treat incompleteness, lack of a replacement proof, or uncertainty as falsehood.
Audit domains after every substitution or reparameterization. If an equality or
inequality is known only at one point, on a level set, or under a conditional
restriction, do not use an unrestricted extremum unless its optimizer is proved
admissible. A pointwise or restricted-domain bound does not control a global
minimum or maximum.
Build a dependency map before coefficient comparison or free variation. A relation
required for one fixed configuration is not a polynomial or functional identity in
one of its parameters. Match coefficients only when universal independent variation
is established while every alleged coefficient remains fixed.
For a game or iterative process, respect every quantifier and adversarial response.
One favorable play, one failed strategy, or one loop against one move does not prove
force or impossibility. Derive the backward winning closure from legal moves and
test whether different successor features can cover different responses. Inventory
fixed totals and test whether they decompose into two closure values. For an
exclusivity claim, test at least one concrete excluded candidate.

Return exactly one plain-text line with exactly three fields:
PACKET_ID | VERDICT | EXPLANATION

VERDICT must be SURVIVES or CHALLENGED. Use CHALLENGED only for a complete explicit
refutation of a material assertion actually made by this packet. Its explanation
must begin PACKET FLAW: and contain PACKET CLAIM:, WITNESS:, and CHECK:. CHECK must
explain why the witness refutes the packet rather than confirms its diagnosis. It
must also contain PACKET STANCE: and PROOF ALARM:; use SAME AS PACKET FLAW or NONE
when appropriate. If the audit establishes a concrete defect in the submitted proof,
record it under PROOF ALARM even when the packet is also unsafe; packet deletion must
not erase a valid repair signal.
Otherwise use SURVIVES; this means only that this attack found no refutation. Its
explanation must begin NO PACKET REFUTATION: and contain PACKET TARGET:, ATTACKS:,
PACKET STANCE:, PROOF BINDING:, PROOF ALARM:, and RESULT:. PROOF ALARM must state a
concrete proof defect found by the audit whether it was represented by the packet or
found independently; use NONE only when no concrete proof defect was established.
Follow the applicable marker order exactly. For CHALLENGED use PACKET FLAW: PACKET
STANCE: ...; PACKET CLAIM: ...; WITNESS: ...; CHECK: ...; PROOF ALARM: .... For
SURVIVES use NO PACKET REFUTATION: PACKET TARGET: ...; PACKET STANCE: ...; ATTACKS:
...; PROOF BINDING: ...; PROOF ALARM: ...; RESULT: ....
The explanation is mandatory, concise, and may not contain a pipe character. Do
not return JSON, Markdown, a code fence, a preface, or another line."""


def _restore_unambiguous_packet_claim_marker(explanation: str) -> str:
    """Repair one harmless label omission without interpreting mathematics."""
    if not explanation.startswith("PACKET FLAW:") or "PACKET CLAIM:" in explanation:
        return explanation
    if "WITNESS:" not in explanation:
        return explanation
    prefix, suffix = explanation.split("WITNESS:", 1)
    claim = prefix.removeprefix("PACKET FLAW:").strip()
    if not claim:
        return explanation
    return f"PACKET FLAW: PACKET CLAIM: {claim} WITNESS:{suffix}"


REASONING_AUDITOR_PROMPT = """You are the final independent skeptical mathematical
auditor for one complete unverified reasoning packet. Keep the packet whole. You
receive one attacker assessment, but must recompute it and run an independent
second attack on every material packet assertion.

First verify that a proposed challenge attacks the packet rather than the submitted
proof. Recheck the quoted packet claim, exact proof location, witness legality,
premises, quantifiers, calculation, and strict contradiction. Showing that the
submitted proof is false normally confirms a defect packet. Reject challenges that
merely repeat or strengthen the packet's criticism, attack a different claim, use
an illegal or limiting object, or rely only on incompleteness or suspicion.
Explicitly classify the packet's stance toward the attacked proof proposition as
ENDORSES, CRITICIZES, or QUOTES/UNCLEAR. If the packet uses or corroborates a false
lemma, it endorses a false packet claim and is UNSAFE. If it criticizes that false
lemma, the same counterexample supports the packet. If an independent proof flaw is
outside the packet's assertions, retain the packet and record that issue separately
under PROOF ALARM.

Before accepting UNSAFE, bind PACKET CLAIM to an exact assertion in the packet.
Reject an assessment that converts a question, selected example, or conditional
branch into an unstated universal, necessity, force, or impossibility claim. Treat
a hedged declarative mathematical proposition as refutable content, while preserving
the scope of its hedge. A reconstructed claim may paraphrase but may not strengthen
the packet's logical force.
Resolve pronouns, labels, and numbered options in their nearest explicit local
scope. If the packet introduces an enumeration, do not silently rebind its numbers
to another enumeration in the proof. A representative example of a case type is
not automatically exhaustive over every concrete choice in that type.
An ambiguous reference cannot support deletion. Accept UNSAFE only if the explicit
refutation holds under every reasonable local binding; otherwise use UNVERIFIED.

Then independently negate and attack the packet's proof description, diagnosis,
witness, derivation, lemma, repair route, preserved material, and all necessity,
sufficiency, force, and impossibility claims. Test small and boundary cases, signs,
parity, residues, exact substitutions, excluded candidates, and alternate
constructions. The packet is a conjunction of its material assertions: validating
its main diagnosis does not validate a false side assertion. Audit every sentence,
especially case tails and qualifiers such as any, every, only, always, neither,
cannot, and unless. Recheck the domain after substitutions and optimization: a
bound known at one point, on a level set, or under a conditional restriction does
not justify an unrestricted extremum unless the optimizer is proved admissible.
Build a dependency map before accepting free-variable or coefficient arguments. A
relation for one fixed configuration is not an identity in a fixed or dependent
parameter. Coefficient matching requires universal independent variation while
every alleged coefficient remains fixed.
For games and iterative processes, cover every adversarial response.
Compute the backward winning closure from legal moves, allow different closure
features to cover different successors, inventory fixed totals, and test their
decomposition into closure values. A failed displayed strategy does not establish
impossibility, and a working subfamily does not establish necessity.

Return exactly one plain-text line with exactly three fields:
PACKET_ID | VERDICT | EXPLANATION

VERDICT must be UNSAFE or UNVERIFIED. Use UNSAFE only for a complete explicit
refutation of a material assertion actually made by this packet. Its explanation
must begin PACKET FLAW: and contain PACKET CLAIM:, WITNESS:, and CHECK:. CHECK must
state why the evidence refutes the packet, not why it confirms the packet's attack
on the proof. It must also contain PACKET STANCE: and PROOF ALARM:; use SAME AS
PACKET FLAW or NONE when appropriate. Otherwise use UNVERIFIED, which remains active
and does not certify truth. Its explanation must begin PACKET UNVERIFIED: and
contain PACKET TARGET:, PACKET STANCE:, ATTACKS:, PROOF BINDING:, PROOF ALARM:, and
RESULT:. PROOF ALARM must record a concrete proof defect supported by the audit even
if the packet already represents it or is itself unsafe; packet deletion must not
erase a valid repair signal. Use NONE only when no concrete proof defect was
established. The explanation is mandatory, concise, and may not
contain a pipe character. Follow the applicable marker order exactly. For UNSAFE
use PACKET FLAW: PACKET STANCE: ...; PACKET CLAIM: ...; WITNESS: ...; CHECK: ...;
PROOF ALARM: .... For UNVERIFIED use PACKET UNVERIFIED: PACKET TARGET: ...; PACKET
STANCE: ...; ATTACKS: ...; PROOF BINDING: ...; PROOF ALARM: ...; RESULT: ....
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


def parse_reasoning_verdict(
    text: str, *, expected_packet_id: str, role: str
) -> dict[str, str]:
    line = _single_plain_line(text)
    fields = line.split(" | ", 2)
    allowed_outer_verdicts = (
        {"SURVIVES", "CHALLENGED"}
        if role == "attacker"
        else {"UNSAFE", "UNVERIFIED"}
        if role == "auditor"
        else set()
    )
    if len(fields) == 2 and fields[0].strip() in allowed_outer_verdicts:
        fields = [expected_packet_id, fields[0].strip(), fields[1].strip()]
    if len(fields) != 3:
        inferred = (
            "CHALLENGED"
            if role == "attacker" and line.startswith("PACKET FLAW:")
            else "SURVIVES"
            if role == "attacker" and line.startswith("NO PACKET REFUTATION:")
            else "UNSAFE"
            if role == "auditor" and line.startswith("PACKET FLAW:")
            else "UNVERIFIED"
            if role == "auditor" and line.startswith("PACKET UNVERIFIED:")
            else None
        )
        if inferred is not None:
            fields = [expected_packet_id, inferred, line]
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
        raise ValueError(f"unsupported reasoning-packet role: {role}")
    if verdict not in allowed:
        raise ValueError(f"unsupported {role} verdict: {verdict}")
    if not explanation:
        raise ValueError("verdict explanation must be nonempty")
    if len(explanation) > MAX_EXPLANATION_CHARS:
        raise ValueError("verdict explanation exceeds the compact output bound")

    challenged = verdict in {"CHALLENGED", "UNSAFE"}
    if challenged:
        explanation = _restore_unambiguous_packet_claim_marker(explanation)
    if challenged:
        if not explanation.startswith("PACKET FLAW:"):
            raise ValueError(f"{verdict} explanation must begin PACKET FLAW:")
        for marker in (
            "PACKET STANCE:",
            "PACKET CLAIM:",
            "WITNESS:",
            "CHECK:",
            "PROOF ALARM:",
        ):
            if marker not in explanation:
                raise ValueError(f"{verdict} explanation must include {marker}")
        lowered = explanation.lower()
        flaw_body = lowered.removeprefix("packet flaw:")
        marker_positions = [
            position
            for marker in ("packet stance:", "packet claim:")
            if (position := flaw_body.find(marker)) >= 0
        ]
        flaw_preamble = flaw_body[: min(marker_positions)] if marker_positions else flaw_body
        if "submitted proof" in flaw_preamble or "submitted-proof" in flaw_preamble:
            raise ValueError(
                f"{verdict} attributes the alleged flaw to the submitted proof"
            )
        check = lowered.split("check:", 1)[1]
        confirmation_phrases = (
            "confirms the packet",
            "supports the packet",
            "validates the packet",
            "confirms its diagnosis",
            "supports its diagnosis",
            "validates its diagnosis",
        )
        if any(
            re.search(rf"\b{re.escape(phrase)}\b", check)
            for phrase in confirmation_phrases
        ):
            raise ValueError(
                f"{verdict} says its witness confirms rather than refutes the packet"
            )
    else:
        prefix = (
            "NO PACKET REFUTATION:"
            if verdict == "SURVIVES"
            else "PACKET UNVERIFIED:"
        )
        if not explanation.startswith(prefix):
            raise ValueError(f"{verdict} explanation must begin {prefix}")
        for marker in (
            "PACKET TARGET:",
            "PACKET STANCE:",
            "ATTACKS:",
            "PROOF BINDING:",
            "PROOF ALARM:",
            "RESULT:",
        ):
            if marker not in explanation:
                raise ValueError(f"{verdict} explanation must include {marker}")
    return {
        "packet_id": packet_id,
        "verdict": verdict,
        "explanation": explanation,
    }


def render_reasoning_verdict(verdict: dict[str, str]) -> str:
    """Render one canonical three-field line without ambiguous inner separators."""
    packet_id = str(verdict["packet_id"]).strip()
    status = str(verdict["verdict"]).strip()
    explanation = str(verdict["explanation"]).strip().replace(" | ", " ∣ ")
    if not packet_id or not status or not explanation:
        raise ValueError("canonical verdict fields must be nonempty")
    if any("\n" in field or "\r" in field for field in (packet_id, status, explanation)):
        raise ValueError("canonical verdict fields must occupy one physical line")
    return f"{packet_id} | {status} | {explanation}\n"


def extract_proof_alarm(explanation: str) -> str | None:
    marker = "PROOF ALARM:"
    if marker not in explanation:
        return None
    alarm = explanation.split(marker, 1)[1]
    if "RESULT:" in alarm:
        alarm = alarm.split("RESULT:", 1)[0]
    alarm = alarm.strip().strip(";,. ")
    if not alarm or alarm.upper() == "NONE":
        return None
    return alarm


def unsafe_rebinds_packet_local_numbering(
    *, packet_text: str, explanation: str
) -> bool:
    """Fail open when an UNSAFE verdict silently changes a local numbered scope."""
    claim_match = re.search(
        r"\bPACKET CLAIM:\s*(.*?)\s*;\s*WITNESS:",
        explanation,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if claim_match is None:
        return False
    claim = claim_match.group(1)
    reference_match = re.search(
        r"\b(?:options?|cases?|steps?|items?|claims?|parts?|alternatives?)\b"
        r"(?P<tail>.{0,100})",
        claim,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if reference_match is None:
        return False
    referenced = {
        int(value)
        for value in re.findall(
            r"(?<![A-Za-z])\d+(?![A-Za-z])", reference_match.group("tail")
        )
    }
    if not referenced:
        return False
    locally_enumerated = {
        int(value)
        for value in re.findall(
            r"(?m)^\s*(?:[-*]\s*)?(\d+)[.)]\s+", packet_text
        )
    }
    if not referenced.issubset(locally_enumerated):
        return False
    challenge = explanation[claim_match.end() :]
    proof_rebinding = re.search(
        r"\b(?:submitted\s+proof|proof)\b.{0,100}"
        r"\b(?:options?|cases?|steps?|items?|claims?|parts?|alternatives?)?\s*\d+\b",
        challenge,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return proof_rebinding is not None


def unsafe_uses_example_against_unfixed_strategy(
    *, explanation: str
) -> bool:
    """Reject a single-example refutation of an unfixed existential strategy."""
    claim_match = re.search(
        r"\bPACKET CLAIM:\s*(.*?)\s*;\s*WITNESS:",
        explanation,
        flags=re.IGNORECASE | re.DOTALL,
    )
    check_match = re.search(
        r"\bCHECK:\s*(.*?)(?:\s*;\s*PROOF ALARM:|$)",
        explanation,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if claim_match is None or check_match is None:
        return False
    claim = claim_match.group(1)
    if re.search(
        r"\b(?:if|when|by|using|with)\b", claim, flags=re.IGNORECASE
    ):
        return False
    if re.search(
        r"\b(?:can|could)\s+(?:guarantee|force|ensure|achieve)\b|"
        r"\bthere\s+(?:is|exists)\b.{0,50}\bstrategy\b",
        claim,
        flags=re.IGNORECASE | re.DOTALL,
    ) is None:
        return False
    check = check_match.group(1)
    asserts_universal = re.search(
        r"\b(?:for\s+(?:any|every|all)|regardless\s+of\s+(?:the|any))\b",
        check,
        flags=re.IGNORECASE,
    )
    supplies_only_example = re.search(
        r"\b(?:for\s+example|e\.g\.)\b", check, flags=re.IGNORECASE
    )
    return asserts_universal is not None and supplies_only_example is not None


def unsafe_sequence_witness_omits_recurrence_check(
    *, problem: str, explanation: str
) -> bool:
    """Reject an alternative sequence witness that never checks its recurrence."""
    if re.search(r"\bsequence\b", problem, flags=re.IGNORECASE) is None:
        return False
    if re.search(
        r"\b(?:smallest|recurrence|recursive)\b|"
        r"[A-Za-z]_\{?n\s*\+\s*1\}?",
        problem,
        flags=re.IGNORECASE,
    ) is None:
        return False
    witness_match = re.search(
        r"\bWITNESS:\s*(.*?)\s*;\s*CHECK:",
        explanation,
        flags=re.IGNORECASE | re.DOTALL,
    )
    check_match = re.search(
        r"\bCHECK:\s*(.*?)(?:\s*;\s*PROOF ALARM:|$)",
        explanation,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if witness_match is None or check_match is None:
        return False
    if re.search(
        r"[A-Za-z]_\{?n\}?\s*=", witness_match.group(1), flags=re.IGNORECASE
    ) is None:
        return False
    legality_check = re.search(
        r"\b(?:satisf(?:y|ies|ied)|obey(?:s|ed)?|meet(?:s)?|fulfill(?:s|ed)?|"
        r"valid\s+sequence|defining\s+(?:condition|recurrence)|recurrence)\b",
        check_match.group(1),
        flags=re.IGNORECASE,
    )
    return legality_check is None


def render_proof_alarms_tsv(decisions: list[dict[str, str]]) -> str:
    lines = ["packet_id\tstatus\tproof_alarm"]
    for decision in decisions:
        alarm = extract_proof_alarm(str(decision.get("explanation") or ""))
        if alarm is None:
            continue
        clean = " ".join(alarm.splitlines()).replace("\t", " ")
        lines.append(
            f"{decision['packet_id']}\t{decision['status']}\t{clean}"
        )
    return "\n".join(lines) + "\n"


def attack_user_prompt(*, case: dict[str, Any], packet_row: dict[str, Any]) -> str:
    packet = packet_row["packet"]
    packet_id = str(packet_row["packet_id"])
    target_units = ",".join(str(v) for v in packet.get("target_unit_ids") or [])
    return f"""ORIGINAL PROBLEM
{str(case['problem']).strip()}

SUBMITTED PROOF
{str(case['proof']).strip()}

PACKET ID
{packet_id}

PACKET TYPE
{str(packet.get('type') or 'UNSPECIFIED')}

TARGET LEMMA UNITS
{target_units or 'UNSPECIFIED'}

COMPLETE REASONING PACKET TEXT
{packet_row['source_text']}

Return the required one-line verdict for {packet_id}."""


def auditor_user_prompt(
    *,
    case: dict[str, Any],
    packet_row: dict[str, Any],
    attacker: dict[str, str] | None,
) -> str:
    packet = packet_row["packet"]
    packet_id = str(packet_row["packet_id"])
    assessment = (
        f"{attacker['verdict']} -- {attacker['explanation']}"
        if attacker is not None
        else "UNAVAILABLE -- The attacker failed mechanically or structurally."
    )
    return f"""ORIGINAL PROBLEM
{str(case['problem']).strip()}

SUBMITTED PROOF
{str(case['proof']).strip()}

PACKET ID
{packet_id}

PACKET TYPE
{str(packet.get('type') or 'UNSPECIFIED')}

COMPLETE REASONING PACKET TEXT
{packet_row['source_text']}

ATTACKER ASSESSMENT TO CROSS-EXAMINE
{assessment}

Return the required one-line final auditor verdict for {packet_id}."""


def _checkpoint(
    *, packet_dir: Path, packet_id: str, input_sha256: str
) -> dict[str, str] | None:
    digest_path = packet_dir / "input.sha256"
    decision_path = packet_dir / "decision.tsv"
    if not digest_path.is_file() and not decision_path.is_file():
        return None
    if decision_path.is_file() and not digest_path.is_file():
        raise ValueError(f"incomplete reasoning prescreen checkpoint: {packet_dir}")
    if digest_path.read_text(encoding="utf-8").strip() != input_sha256:
        raise ValueError(f"reasoning prescreen checkpoint input drift: {packet_dir}")
    if not decision_path.is_file():
        return None
    rows = parse_decision_tsv(decision_path.read_text(encoding="utf-8"))
    if len(rows) != 1 or rows[0]["packet_id"] != packet_id:
        raise ValueError(f"invalid reasoning prescreen checkpoint: {packet_dir}")
    return rows[0]


def run_packet_prescreen(
    *,
    runtime: Any,
    case: dict[str, Any],
    packet_row: dict[str, Any],
    output_dir: Path,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    seed_namespace: str = "v0175:reasoning-full-validity",
    attacker_role: str = "gemma",
    auditor_role: str = "qwen",
    attacker_temperature: float = 0.2,
    auditor_temperature: float = 0.1,
) -> dict[str, str]:
    if attacker_role not in {"gemma", "qwen"}:
        raise ValueError(f"unsupported attacker role: {attacker_role}")
    if auditor_role not in {"gemma", "qwen"}:
        raise ValueError(f"unsupported auditor role: {auditor_role}")
    if max_tokens < 1:
        raise ValueError("max_tokens must be positive")
    if attacker_temperature < 0 or auditor_temperature < 0:
        raise ValueError("temperatures must be nonnegative")
    packet_id = str(packet_row["packet_id"])
    packet_dir = output_dir / "packets" / safe_component(packet_id)
    digest = stable_digest(
        {
            "harness_version": HARNESS_VERSION,
            "case_key": case["case_key"],
            "problem_sha256": sha256_text(str(case["problem"])),
            "proof_sha256": sha256_text(str(case["proof"])),
            "packet_id": packet_id,
            "packet_source_sha256": packet_row["source_sha256"],
            "attack_prompt_sha256": sha256_text(REASONING_ATTACK_PROMPT),
            "auditor_prompt_sha256": sha256_text(REASONING_AUDITOR_PROMPT),
            "attacker_role": attacker_role,
            "auditor_role": auditor_role,
            "attacker_temperature": attacker_temperature,
            "auditor_temperature": auditor_temperature,
            "numbered_reference_guard": NUMBERED_REFERENCE_GUARD_VERSION,
            "quantifier_witness_guard": QUANTIFIER_WITNESS_GUARD_VERSION,
            "sequence_legality_guard": SEQUENCE_LEGALITY_GUARD_VERSION,
            "max_tokens": max_tokens,
            "seed_namespace": seed_namespace,
        }
    )
    saved = _checkpoint(
        packet_dir=packet_dir, packet_id=packet_id, input_sha256=digest
    )
    if saved is not None:
        return saved

    write_text(packet_dir / "input.sha256", digest + "\n")
    content = str(packet_row["source_text"])
    packet_section = f"COMPLETE REASONING PACKET TEXT\n{content}\n\n"
    attack_prompt = attack_user_prompt(case=case, packet_row=packet_row)
    if attack_prompt.count(packet_section) != 1:
        raise ValueError(f"whole packet was not supplied exactly once: {packet_id}")
    write_text(packet_dir / "attacker.user_prompt.txt", attack_prompt)

    errors: list[str] = []
    attacker: dict[str, str] | None = None
    try:
        generation = runtime.text(
            role=attacker_role,
            prompt=REASONING_ATTACK_PROMPT,
            user_prompt=attack_prompt,
            destination=packet_dir / "attacker_model_call",
            stage="whole_reasoning_packet_full_field_attack",
            temperature=attacker_temperature,
            max_tokens=max_tokens,
            seed_label=f"{seed_namespace}:{case['case_key']}:{packet_id}:attacker",
        )
        text = str(generation.get("text") or "")
        attacker = parse_reasoning_verdict(
            text, expected_packet_id=packet_id, role="attacker"
        )
        write_text(
            packet_dir / "attacker.verdict.txt",
            render_reasoning_verdict(attacker),
        )
    except Exception as error:
        write_text(packet_dir / "attacker.error.txt", traceback.format_exc())
        errors.append(f"attacker:{type(error).__name__}")

    audit_prompt = auditor_user_prompt(
        case=case, packet_row=packet_row, attacker=attacker
    )
    if audit_prompt.count(packet_section) != 1:
        raise ValueError(
            f"whole packet was not supplied exactly once to auditor: {packet_id}"
        )
    write_text(packet_dir / "auditor.user_prompt.txt", audit_prompt)
    auditor: dict[str, str] | None = None
    try:
        generation = runtime.text(
            role=auditor_role,
            prompt=REASONING_AUDITOR_PROMPT,
            user_prompt=audit_prompt,
            destination=packet_dir / "auditor_model_call",
            stage="whole_reasoning_packet_final_full_field_audit",
            temperature=auditor_temperature,
            max_tokens=max_tokens,
            seed_label=f"{seed_namespace}:{case['case_key']}:{packet_id}:auditor",
        )
        text = str(generation.get("text") or "")
        auditor = parse_reasoning_verdict(
            text, expected_packet_id=packet_id, role="auditor"
        )
        write_text(
            packet_dir / "auditor.verdict.txt",
            render_reasoning_verdict(auditor),
        )
    except Exception as error:
        write_text(packet_dir / "auditor.error.txt", traceback.format_exc())
        errors.append(f"auditor:{type(error).__name__}")

    unsafe_rebinding = (
        auditor is not None
        and auditor["verdict"] == "UNSAFE"
        and unsafe_rebinds_packet_local_numbering(
            packet_text=content,
            explanation=auditor["explanation"],
        )
    )
    unsafe_strategy_example = (
        auditor is not None
        and auditor["verdict"] == "UNSAFE"
        and unsafe_uses_example_against_unfixed_strategy(
            explanation=auditor["explanation"]
        )
    )
    unsafe_sequence_witness = (
        auditor is not None
        and auditor["verdict"] == "UNSAFE"
        and unsafe_sequence_witness_omits_recurrence_check(
            problem=str(case["problem"]),
            explanation=auditor["explanation"],
        )
    )
    if unsafe_rebinding or unsafe_strategy_example or unsafe_sequence_witness:
        alarm = extract_proof_alarm(auditor["explanation"]) or "NONE"
        if unsafe_rebinding:
            reason = "a numbered reference despite a packet-local enumeration"
        elif unsafe_strategy_example:
            reason = "an unfixed existential strategy using only one failed example"
        else:
            reason = "an alternative sequence without checking its defining recurrence"
        decision = {
            "packet_id": packet_id,
            "status": "ACTIVE",
            "explanation": (
                "Deterministic fail-open: the proposed packet challenge refutes "
                f"{reason}; "
                f"PROOF ALARM: {alarm}"
            ),
        }
        write_text(
            packet_dir / "auditor.fail_open_guard.txt",
            f"REJECTED_UNSAFE\t{reason}\n",
        )
    elif auditor is not None and auditor["verdict"] == "UNSAFE":
        decision = {
            "packet_id": packet_id,
            "status": "INACTIVE",
            "explanation": auditor["explanation"],
        }
    elif auditor is not None:
        decision = {
            "packet_id": packet_id,
            "status": "ACTIVE",
            "explanation": auditor["explanation"],
        }
    else:
        detail = ",".join(errors) or "unknown"
        decision = {
            "packet_id": packet_id,
            "status": "ACTIVE",
            "explanation": (
                f"Full-field audit incomplete mechanically ({detail}); "
                "packet remains active."
            ),
        }
    write_text(packet_dir / "decision.tsv", render_decision_tsv([decision]))
    return decision


def apply_packet_decisions(
    case: dict[str, Any],
    decisions: list[dict[str, str]],
    *,
    decision_path: Path | None = None,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
) -> dict[str, Any]:
    packet_rows = collect_nh_packets(case)
    expected_ids = [row["packet_id"] for row in packet_rows]
    by_id = {str(row["packet_id"]): row for row in decisions}
    if len(by_id) != len(decisions) or set(by_id) != set(expected_ids):
        raise ValueError("reasoning decisions are not an exact packet partition")
    filtered = copy.deepcopy(case)
    for group in filtered.get("groups") or []:
        active_packets = []
        for packet in group.get("nh_packets") or []:
            decision = by_id[str(packet["trace_id"])]
            if decision["status"] == "ACTIVE":
                active_packets.append(packet)
            elif decision["status"] != "INACTIVE":
                raise ValueError(
                    f"unsupported packet decision status: {decision['status']}"
                )
        group["nh_packets"] = active_packets
        group["full_validity_active_packet_count"] = len(active_packets)
    proof_alarms = [
        {
            "packet_id": str(row["packet_id"]),
            "packet_status": str(row["status"]),
            "proof_alarm": alarm,
        }
        for row in decisions
        if (alarm := extract_proof_alarm(str(row.get("explanation") or "")))
        is not None
    ]
    alarm_path = decision_path.with_name("proof_alarms.tsv") if decision_path else None
    if alarm_path is not None:
        write_text(alarm_path, render_proof_alarms_tsv(decisions))
    filtered["nh_packet_full_validity_prescreen"] = {
        "harness_version": HARNESS_VERSION,
        "policy": "two_call_whole_packet_fail_open",
        "input_packet_count": len(expected_ids),
        "active_packet_count": sum(row["status"] == "ACTIVE" for row in decisions),
        "inactive_packet_count": sum(
            row["status"] == "INACTIVE" for row in decisions
        ),
        "decision_path": str(decision_path.resolve()) if decision_path else None,
        "proof_alarm_count": len(proof_alarms),
        "proof_alarm_path": str(alarm_path.resolve()) if alarm_path else None,
        "proof_alarms": proof_alarms,
        "whole_packet_text_preserved": True,
        "atomicization": False,
        "logical_model_calls_per_packet": 2,
        "max_concurrency": max_concurrency,
    }
    return filtered


def run_case_prescreen(
    *,
    runtime: Any,
    case: dict[str, Any],
    output_root: Path,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    seed_namespace: str = "v0175:reasoning-full-validity",
    attacker_role: str = "gemma",
    auditor_role: str = "qwen",
    attacker_temperature: float = 0.2,
    auditor_temperature: float = 0.1,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    packet_rows = collect_nh_packets(case)
    case_dir = (
        output_root
        / safe_component(str(case["problem_key"]))
        / safe_component(str(case["candidate_id"]))
    )
    decisions_by_id: dict[str, dict[str, str]] = {}

    def work(packet_row: dict[str, Any]) -> dict[str, str]:
        return run_packet_prescreen(
            runtime=runtime,
            case=case,
            packet_row=packet_row,
            output_dir=case_dir,
            max_tokens=max_tokens,
            seed_namespace=seed_namespace,
            attacker_role=attacker_role,
            auditor_role=auditor_role,
            attacker_temperature=attacker_temperature,
            auditor_temperature=auditor_temperature,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = {executor.submit(work, row): row["packet_id"] for row in packet_rows}
        for future in concurrent.futures.as_completed(futures):
            decision = future.result()
            decisions_by_id[decision["packet_id"]] = decision
    decisions = [decisions_by_id[row["packet_id"]] for row in packet_rows]
    decision_path = case_dir / "packet_status.tsv"
    write_text(decision_path, render_decision_tsv(decisions))
    return (
        apply_packet_decisions(
            case,
            decisions,
            decision_path=decision_path,
            max_concurrency=max_concurrency,
        ),
        decisions,
    )
