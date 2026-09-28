from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
    pipeline as base,
)
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import (
    validation as synthesis_validation,
)
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import (
    EvidenceBundle,
)

from . import HARNESS_VERSION
from . import protocol


MAX_RENDERED_NORMAL_FORM_TERMS = 256
MAX_RENDERED_EXPRESSION_CHARS = 30_000
MAX_RENDERED_CERTIFICATE_CHARS = 120_000


ExactReplay = Callable[[], Mapping[str, Any]]
FormalRequestReplay = Callable[[], Mapping[str, Any]]
CERTIFICATE_AUTHOR_STAGE = "generic_verified_certificate_author"
EXPECTED_BUDGET_FORCING_SCHEMA = (
    "cognitive-well-v0257-all-call-budget-forcing-event-v1"
)
EXPECTED_BUDGET_FORCING_POLICY = (
    "mandatory_one_semantic_continuation_full_replacement"
)


@dataclass(frozen=True)
class GenericCertificateContext:
    """Problem-independent inputs for one model-authored ideal certificate.

    ``arguments`` and ``typed_guards`` use the already frozen safe polynomial
    AST.  ``replay_exact`` must independently revalidate the upstream result;
    a persisted ``PROVED`` word is never sufficient by itself.
    """

    certificate_id: str
    theorem: str
    arguments: Mapping[str, Any]
    typed_guards: Mapping[str, Any]
    replay_formal_request: FormalRequestReplay
    replay_exact: ExactReplay
    formal_request_markdown: str
    exact_result_markdown: str
    source_artifacts: Mapping[str, Path]

    def __post_init__(self) -> None:
        if not self.certificate_id.strip() or not self.certificate_id.replace(
            "_", ""
        ).isalnum():
            raise ValueError("certificate_id must be a nonempty safe identifier")
        if not self.theorem.strip():
            raise ValueError("theorem cannot be empty")
        if not self.formal_request_markdown.strip() or not self.exact_result_markdown.strip():
            raise ValueError("formal request and exact result Markdown are required")
        if not callable(self.replay_exact):
            raise ValueError("replay_exact must be callable")
        if not callable(self.replay_formal_request):
            raise ValueError("replay_formal_request must be callable")
        required_artifacts = {"formal_request", "exact_result"}
        if not required_artifacts <= set(self.source_artifacts):
            raise ValueError(
                "source artifacts must include formal_request and exact_result"
            )
        for label, path in self.source_artifacts.items():
            if not label or not path.is_file():
                raise ValueError(f"missing generic certificate source artifact: {label}")
        if (
            self.source_artifacts["formal_request"]
            .read_text(encoding="utf-8")
            .strip()
            != self.formal_request_markdown.strip()
        ):
            raise ValueError("formal request Markdown differs from its source artifact")
        if (
            self.source_artifacts["exact_result"]
            .read_text(encoding="utf-8")
            .strip()
            != self.exact_result_markdown.strip()
        ):
            raise ValueError("exact result Markdown differs from its source artifact")


def validate_exact_replay(record: Mapping[str, Any]) -> dict[str, Any]:
    """Require a standardized affirmative exact replay record."""

    required = {"schema", "operation", "claim", "verified", "verdict"}
    if not required <= set(record):
        raise ValueError("exact replay record lacks required provenance fields")
    if record.get("verified") is not True:
        raise ValueError("exact replay did not verify")
    if record.get("verdict") != "VERIFIED_SUPPORT":
        raise ValueError("exact replay is not affirmative supporting evidence")
    if not str(record.get("schema") or "").strip():
        raise ValueError("exact replay schema is empty")
    if not str(record.get("operation") or "").strip():
        raise ValueError("exact replay operation is empty")
    if record.get("operation") != exact_tools.IDEAL_OPERATION:
        raise ValueError(
            "generic polynomial certificate requires polynomial_ideal_membership replay"
        )
    if not str(record.get("claim") or "").strip():
        raise ValueError("exact replay claim is empty")
    return dict(record)


def validate_markdown_budget_forcing(
    call: Mapping[str, Any],
    *,
    expected_stage: str,
    expected_model: str,
    canonical_markdown: str,
    expected_timeout_sec: int | None = 600,
) -> dict[str, Any]:
    """Bind a Markdown artifact to the mandatory forced model response."""

    forcing = call.get("metadata", {}).get("v0257_budget_forcing")
    if not isinstance(forcing, Mapping):
        raise ValueError("certificate producer lacks mandatory budget forcing")
    if call.get("attempt") not in range(1, len(base.TOKEN_CAPS) + 1):
        raise ValueError("certificate producer has an invalid recovery attempt")
    if call.get("cap") not in base.TOKEN_CAPS:
        raise ValueError("certificate producer used an unapproved token cap")
    if expected_timeout_sec is not None and (type(expected_timeout_sec) is not int or not 1<=expected_timeout_sec<=3600):
        raise ValueError("invalid expected response timeout")
    if "request_timeout_sec" not in call or call["request_timeout_sec"] != expected_timeout_sec:
        raise ValueError("certificate producer did not use the configured response timeout")
    config=call.get("metadata",{}).get("config")
    if isinstance(config,Mapping) and ("timeout_seconds" not in config or config["timeout_seconds"]!=expected_timeout_sec):
        raise ValueError("certificate producer transport timeout differs from configuration")
    expected = {
        "schema": EXPECTED_BUDGET_FORCING_SCHEMA,
        "policy": EXPECTED_BUDGET_FORCING_POLICY,
        "stage": expected_stage,
        "model": expected_model,
        "structured": False,
        "canonical_artifacts_are_forced_response": True,
    }
    mismatched = [key for key, value in expected.items() if forcing.get(key) != value]
    if mismatched:
        raise ValueError(
            "certificate producer budget-forcing provenance mismatch: "
            + ", ".join(mismatched)
        )
    if forcing.get("forced_text_sha256") != base.sha256_text(canonical_markdown):
        raise ValueError("certificate Markdown is not the canonical forced response")
    cue = str(forcing.get("cue") or "")
    if not cue or forcing.get("cue_sha256") != base.sha256_text(cue):
        raise ValueError("certificate producer continuation cue is not hash-bound")
    return dict(forcing)


def _poly_from_ast(
    ast: Any, *, symbol_map: Mapping[str, Any], symbols: list[Any]
) -> Any:
    sp = exact_tools.require_sympy()
    expression = exact_tools._expression(ast, symbol_map)  # noqa: SLF001
    return sp.Poly(sp.expand(expression), *symbols, domain=sp.QQ)


def _row_verification(
    *,
    row: Mapping[str, Any],
    symbol_map: Mapping[str, Any],
    symbols: list[Any],
    reducer: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sp = exact_tools.require_sympy()
    left = _poly_from_ast(row["left"], symbol_map=symbol_map, symbols=symbols)
    right = _poly_from_ast(row["right"], symbol_map=symbol_map, symbols=symbols)
    left_nf = sp.Poly(
        sp.expand(reducer.reduce(left.as_expr())[1]), *symbols, domain=sp.QQ
    )
    right_nf = sp.Poly(
        sp.expand(reducer.reduce(right.as_expr())[1]), *symbols, domain=sp.QQ
    )
    if left_nf != right_nf:
        raise ValueError(
            f"certificate {row['label']} has unequal exact normal forms"
        )
    common = left_nf.as_expr()
    term_count = len(left_nf.terms()) if not left_nf.is_zero else 0
    if term_count > MAX_RENDERED_NORMAL_FORM_TERMS:
        raise ValueError(
            f"certificate {row['label']} normal form has {term_count} terms; "
            "model must introduce smaller checkable intermediate identities"
        )
    left_latex = sp.latex(left.as_expr())
    right_latex = sp.latex(right.as_expr())
    common_latex = sp.latex(common)
    if max(map(len, (left_latex, right_latex, common_latex))) > MAX_RENDERED_EXPRESSION_CHARS:
        raise ValueError(
            f"certificate {row['label']} expression is too large to expose"
        )
    verification = {
        "label": row["label"],
        "verified_equal": True,
        "method": "exact_QQ_groebner_normal_form_over_selected_source_relations",
        "left_ast_sha256": exact_tools.stable_hash(row["left"]),
        "right_ast_sha256": exact_tools.stable_hash(row["right"]),
        "left_polynomial_terms": exact_tools._term_payload(  # noqa: SLF001
            left.as_expr(), [str(symbol) for symbol in symbols]
        ),
        "right_polynomial_terms": exact_tools._term_payload(  # noqa: SLF001
            right.as_expr(), [str(symbol) for symbol in symbols]
        ),
        "common_normal_form_terms": exact_tools._term_payload(  # noqa: SLF001
            common, [str(symbol) for symbol in symbols]
        ),
        "common_normal_form_term_count": term_count,
    }
    presentation = {
        "label": row["label"],
        "left_latex": left_latex,
        "right_latex": right_latex,
        "common_latex": common_latex,
    }
    return verification, presentation


def verify_and_render(
    *,
    context: GenericCertificateContext,
    proposal_markdown: str,
    exact_replay: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Parse, source-bind, exactly verify, and render one model proposal."""

    sp = exact_tools.require_sympy()
    exact = validate_exact_replay(
        context.replay_exact() if exact_replay is None else exact_replay
    )
    program = protocol.parse_certificate(proposal_markdown)
    replayed_arguments = dict(context.replay_formal_request())
    if exact_tools.stable_hash(replayed_arguments) != exact_tools.stable_hash(
        context.arguments
    ):
        raise ValueError("frozen formal arguments differ from parser replay")
    validated = exact_tools.validate_ideal_arguments(replayed_arguments)
    expected_names = list(validated["symbols"])
    if program["symbols"] != expected_names:
        raise ValueError("certificate symbols do not exactly match the frozen request")

    required_conclusion = program["semantics"]["required_conclusion"]
    if synthesis_validation.compact_math(required_conclusion) not in (
        synthesis_validation.compact_math(context.theorem)
    ):
        raise ValueError("Required conclusion is not a literal theorem substring")

    source_generators = validated["generators"]
    if any(label not in source_generators for label in program["relations"]):
        raise ValueError("certificate selects an unknown source relation")
    expected_guards = sorted(context.typed_guards)
    if sorted(program["guards"]) != expected_guards:
        raise ValueError("certificate must retain every frozen typed guard exactly")

    symbol_map = validated["symbol_map"]
    symbols = [symbol_map[name] for name in expected_names]
    if program.get("zeros"):
        from .explicit_certificate import verify
        guard_values = {label: _poly_from_ast(ast, symbol_map=symbol_map, symbols=symbols).as_expr()
                        for label, ast in context.typed_guards.items()}
        explicit = verify(program, validated, guard_values)
        conclusion = program["conclusion"]
        conclusion_map = {**symbol_map, "T": validated["target"].as_expr()}
        if (sp.expand(_poly_from_ast(conclusion["left"], symbol_map=conclusion_map, symbols=symbols).as_expr()
                - validated["target"].as_expr()) != 0
                or not _poly_from_ast(conclusion["right"], symbol_map=conclusion_map, symbols=symbols).is_zero):
            raise ValueError("C1 must be exactly the frozen formal target on the left and zero on the right")
        verification = {
            "schema": "cognitive-well-v0324-explicit-source-certificate-v1",
            "verified": True,
            "proposal_sha256": base.sha256_text(proposal_markdown.strip()),
            "program_sha256": exact_tools.stable_hash(program),
            "formal_arguments_sha256": exact_tools.stable_hash(replayed_arguments),
            "exact_replay_sha256": exact_tools.stable_hash(exact),
            "rendered_markdown_sha256": base.sha256_text(explicit["markdown"]),
            "model_semantics_require_independent_audit": True,
            "explicit_checks": explicit["checks"],
            "groebner_search_performed": False,
        }
        return {"program": program, "exact_replay": exact,
                "markdown": explicit["markdown"], "verification": verification}
    selected_generators = [
        sp.Poly(source_generators[label].as_expr(), *symbols, domain=sp.QQ)
        for label in program["relations"]
    ]
    reducer = sp.groebner(
        [item.as_expr() for item in selected_generators],
        *symbols,
        order="grevlex",
        domain=sp.QQ,
    )

    guard_rows: list[dict[str, Any]] = []
    for label in program["guards"]:
        polynomial = _poly_from_ast(
            context.typed_guards[label], symbol_map=symbol_map, symbols=symbols
        )
        if polynomial.is_zero:
            raise ValueError(f"typed guard {label} is identically zero")
        guard_rows.append(
            {
                "label": label,
                "ast_sha256": exact_tools.stable_hash(context.typed_guards[label]),
                "polynomial_terms": exact_tools._term_payload(  # noqa: SLF001
                    polynomial.as_expr(), expected_names
                ),
                "latex": sp.latex(polynomial.as_expr()),
            }
        )

    identity_records: list[dict[str, Any]] = []
    identity_presentations: list[dict[str, Any]] = []
    for row in program["identities"]:
        verified_row, presentation = _row_verification(
            row=row,
            symbol_map=symbol_map,
            symbols=symbols,
            reducer=reducer,
        )
        identity_records.append(verified_row)
        identity_presentations.append(presentation)

    conclusion = program["conclusion"]
    conclusion_left = _poly_from_ast(
        conclusion["left"], symbol_map=symbol_map, symbols=symbols
    )
    conclusion_right = _poly_from_ast(
        conclusion["right"], symbol_map=symbol_map, symbols=symbols
    )
    frozen_target = sp.Poly(
        validated["target"].as_expr(), *symbols, domain=sp.QQ
    )
    if conclusion_left != frozen_target or not conclusion_right.is_zero:
        raise ValueError(
            "C1 must be exactly the frozen formal target on the left and zero on the right"
        )
    conclusion_record, conclusion_presentation = _row_verification(
        row=conclusion,
        symbol_map=symbol_map,
        symbols=symbols,
        reducer=reducer,
    )
    if conclusion_presentation["common_latex"] != "0":
        raise ValueError("frozen target did not reduce to the explicit zero normal form")

    relation_lines = []
    for label, polynomial in zip(
        program["relations"], selected_generators, strict=True
    ):
        relation_lines.append(
            f"\\[{label}:\\quad {sp.latex(polynomial.as_expr())}=0.\\]"
        )
    guard_lines = (
        [f"\\[{row['label']}:\\quad {row['latex']}\\ne0.\\]" for row in guard_rows]
        if guard_rows
        else ["No division or cancellation guard is present in the frozen input."]
    )
    identity_lines: list[str] = []
    for row in identity_presentations:
        identity_lines.extend(
            (
                f"\\[{row['label']}:\\quad {row['left_latex']}={row['right_latex']}.\\]",
                "Reducing both displayed sides by the source relations above, in "
                "the listed variable order, gives the identical exact normal form",
                f"\\[{row['common_latex']}.\\]",
            )
        )
    if not identity_lines:
        identity_lines.append(
            "No auxiliary identity was proposed; the checked conclusion below is direct."
        )

    semantics = program["semantics"]
    markdown = "\n\n".join(
        (
            "## Verified algebraic certificate",
            "The certificate author supplied the following semantic bindings, which "
            "the whole-proof auditor must independently check against the theorem:\n\n"
            f"- Formal source: {semantics['formal_source']}\n"
            f"- Target meaning: {semantics['target_meaning']}\n"
            f"- Guard use: {semantics['guard_use']}\n"
            f"- Proof consequence: {semantics['proof_consequence']}",
            "Use the variable order\n\n\\["
            + ", ".join(expected_names)
            + ".\\]",
            "The selected source relations are\n\n" + "\n".join(relation_lines),
            "The complete typed nonzero conditions are\n\n" + "\n".join(guard_lines),
            "The model-proposed intermediate identities have been checked exactly:\n\n"
            + "\n\n".join(identity_lines),
            "Finally, the model-proposed conclusion is exactly the frozen formal "
            "target, not a substitute:\n\n"
            f"\\[{conclusion_presentation['left_latex']}=0.\\]\n\n"
            "Both sides reduce by the displayed source relations to the explicit "
            "common normal form\n\n"
            f"\\[{conclusion_presentation['common_latex']}.\\]\n\n"
            f"Therefore the verified formal conclusion is: {required_conclusion}",
        )
    )
    if len(markdown) > MAX_RENDERED_CERTIFICATE_CHARS:
        raise ValueError("rendered certificate exceeds the human-readable size limit")

    verification = {
        "schema": "cognitive-well-v0324-generic-verified-certificate-v1",
        "harness_version": HARNESS_VERSION,
        "verified": True,
        "certificate_id": context.certificate_id,
        "proposal_sha256": base.sha256_text(proposal_markdown.strip()),
        "program_sha256": exact_tools.stable_hash(program),
        "formal_arguments_sha256": exact_tools.stable_hash(replayed_arguments),
        "exact_replay_sha256": exact_tools.stable_hash(exact),
        "selected_relations": list(program["relations"]),
        "selected_relation_terms": {
            label: exact_tools._term_payload(  # noqa: SLF001
                polynomial.as_expr(), expected_names
            )
            for label, polynomial in zip(
                program["relations"], selected_generators, strict=True
            )
        },
        "typed_guards": guard_rows,
        "identity_checks": identity_records,
        "conclusion_check": conclusion_record,
        "required_conclusion": required_conclusion,
        "rendered_markdown_sha256": base.sha256_text(markdown),
        "model_semantics_require_independent_audit": True,
    }
    return {
        "program": program,
        "exact_replay": exact,
        "markdown": markdown,
        "verification": verification,
    }


@dataclass(frozen=True)
class ModelAuthoredVerifiedCertificateProvider:
    context: GenericCertificateContext
    proposal_path: Path
    expected_proposal_sha256: str
    expected_exact_replay_sha256: str
    expected_source_artifact_sha256: Mapping[str, str]
    expected_model: str
    producer_call: Mapping[str, Any]
    provider_id: str = "generic_model_authored_verified_certificate_v1"

    def materialize(self) -> EvidenceBundle:
        proposal_path = self.proposal_path.resolve()
        proposal = proposal_path.read_text(encoding="utf-8").strip()
        if base.sha256_text(proposal) != self.expected_proposal_sha256:
            raise ValueError("model-authored certificate proposal hash drift")
        current_source_hashes = {
            label: base.sha256_file(path)
            for label, path in sorted(self.context.source_artifacts.items())
        }
        if current_source_hashes != dict(self.expected_source_artifact_sha256):
            raise ValueError("generic certificate source artifact hash drift")
        validate_markdown_budget_forcing(
            self.producer_call,
            expected_stage=CERTIFICATE_AUTHOR_STAGE,
            expected_model=self.expected_model,
            canonical_markdown=proposal,
        )
        verified = verify_and_render(context=self.context, proposal_markdown=proposal)
        if (
            verified["verification"]["exact_replay_sha256"]
            != self.expected_exact_replay_sha256
        ):
            raise ValueError("exact replay changed after certificate generation")
        source_artifacts = {
            **self.context.source_artifacts,
            "model_certificate_proposal": proposal_path,
        }
        return EvidenceBundle(
            provider_id=self.provider_id,
            verdict="VERIFIED_SUPPORT",
            markdown=verified["markdown"],
            verification=verified["verification"],
            tool_record={
                "schema": "cognitive-well-v0324-generic-certificate-tool-record-v1",
                "operation": verified["exact_replay"]["operation"],
                "claim": verified["exact_replay"]["claim"],
                "decision": "PROVED",
                "result_polarity": "VERIFIED_SUPPORT",
                "certificate_program_sha256": verified["verification"][
                    "program_sha256"
                ],
                "model_authored_certificate": True,
                "deterministically_verified": True,
            },
            source_artifacts=source_artifacts,
        )
