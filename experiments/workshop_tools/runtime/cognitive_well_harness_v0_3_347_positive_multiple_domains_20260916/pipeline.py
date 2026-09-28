from __future__ import annotations

import signal
import traceback
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Mapping

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
    pipeline as base,
)
from .synthesis_core import pipeline as synthesis_pipeline
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import (
    LiteralRequirement,
    SynthesisAdapter,
    SynthesisContract,
    TaskInputs,
)
from cognitive_well_harness_v0_3_257_v108_third_resolve_raw_t10_bf_temp07_20260904 import (
    budget_forcing as mandatory_budget_forcing,
)

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from .certificate import (
    CERTIFICATE_AUTHOR_STAGE,
    GenericCertificateContext,
    ModelAuthoredVerifiedCertificateProvider,
    validate_exact_replay,
    validate_markdown_budget_forcing,
    verify_and_render,
)


ModelCall = Callable[..., tuple[str, Any, dict[str, Any]]]


def _verify_explicit_proposal(context, proposal, exact_replay):
    from .protocol import parse_certificate

    if not parse_certificate(proposal).get("zeros"):
        raise ValueError("an explicit zero derivation ending in C1 is required; no full-ideal search is performed")

    def expired(signum, frame):
        raise ValueError("certificate expansion exceeded 120 seconds; use smaller explicit intermediate identities")

    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, 120)
    try:
        return verify_and_render(context=context, proposal_markdown=proposal, exact_replay=exact_replay)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _mandatory_budget_forced_model_call(
    **kwargs: Any,
) -> tuple[str, Any, dict[str, Any]]:
    """Install the inherited all-call forcing transport before every model call."""

    mandatory_budget_forcing.install()
    # Keep deep reasoning and the mandatory continuation, but reserve output
    # space: an unbounded forced pass can consume the entire cap in thought.
    kwargs.setdefault("thinking_token_budget", 16_384)
    return base._model_call(**kwargs)  # noqa: SLF001


CERTIFICATE_AUTHOR_SYSTEM = r"""You are the certificate-author stage of a
problem-independent exact proof pipeline.  Read the theorem, the complete proof
attempt, a typed polynomial formal request, and an affirmative exact-result report.
Package the already certified lemma into a small human-checkable algebraic derivation
of the formal target equal to zero. You make every mathematical choice: which source relations to retain,
which intermediate identities help a human proof, how the formal target maps back to
the theorem, and how each typed guard is used.

Output Markdown only.  Never output JSON, Python, executable code, or prose outside
the required headings.  The fenced certificate-args block is a line-oriented
S-expression DSL inside Markdown.  It will be parsed fail-closed and every identity
will be checked exactly over QQ.  Do not claim a relation merely because a tool said
PROVED.  Do not mention models, prompts, retries, or operators.

An expression is an integer or one of:
  (symbol name)
  (rational numerator denominator)
  (add expression expression ...)
  (mul expression expression ...)
  (sub expression expression)
  (pow expression nonnegative_integer)
  (neg expression)

Use the exact original symbol list. The reference (symbol T) expands to the frozen
target; (symbol Dn) expands to that source generator, and each guard label expands
to its frozen polynomial. You may define up to 40 short polynomial abbreviations,
using original variables, guard labels, T, and earlier definitions only.

The zero derivations are the human-checkable proof. A row
zero = Z1 :: expression :: scale :: combination
asserts scale*expression = combination modulo selected unit-circle equations.
The combination must vanish when every Dn and previously derived Zn is set to zero.
Thus use explicit multiples of source equations or previously derived zero
expressions. Every factor in scale must be covered by a given typed nonzero guard;
use 1 when no division is necessary. The checker expands these identities exactly
and exposes any unit-circle correction multiples. It never searches the full ideal.
Finish with zero = C1 :: (symbol T) :: scale :: combination.

Derive compact useful relations from the original equations first, then combine
them to obtain the target. Definitions can encode compound-angle expressions as
polynomials in the supplied sine/cosine variables. No additional semantic audit or
new formalization is being requested: concentrate on readable algebraic packaging.

Return exactly:

# Certificate Semantics

- Formal source: one line explaining where the selected equations arise in the proof
- Target meaning: one line translating the formal target to the theorem
- Guard use: one line explaining every supplied typed nonzero guard, or why none exists
- Proof consequence: one line explaining how C1 completes the proof
- Required conclusion: one short literal substring copied from the theorem conclusion

# Certificate Program

```certificate-args
symbols = the exact comma-separated source symbol list
relation = D1
relation = another retained D-numbered source relation
define = a_short_name :: polynomial S-expression
identity = I1 :: one polynomial S-expression :: an equal polynomial S-expression
identity = I2 :: one polynomial S-expression :: an equal polynomial S-expression
zero = Z1 :: polynomial S-expression :: nonzero scale :: combination using Dn
zero = C1 :: (symbol T) :: nonzero scale :: combination using Dn and previous Zn
conclusion = C1 :: (symbol T) :: 0
guard = one exact supplied typed-guard label
```

Relations, identities, and guards may repeat as fields, but labels may not repeat.
If no intermediate identity is useful, write `identity = NONE`.  If no typed guard
is supplied, write `guard = NONE`. Definitions may be omitted. The final C1 zero
derivation is mandatory. Omit unused intermediate identities rather than inventing them."""


def certificate_author_prompt(
    *, task: TaskInputs, context: GenericCertificateContext
) -> str:
    validated = exact_tools.validate_ideal_arguments(context.arguments)
    guard_labels = ", ".join(sorted(context.typed_guards)) or "NONE"
    from .protocol import _render_ast
    guard_expressions = "\n".join(f"- {label} = {_render_ast(ast)}" for label, ast in context.typed_guards.items()) or "NONE"
    relation_labels = ", ".join(validated["generators"])
    witness = task.additional_documents.get("saved_exact_witness.md", "NONE")
    return f"""# Original Theorem

{task.theorem}

# Complete Untrusted Proof Attempt

{task.source_proof}

# Typed Formal Request

{context.formal_request_markdown}

# Independently Replayed Exact Result

{context.exact_result_markdown}

# Saved Exact Witness (no new algebraic search)

{witness}

# Frozen Compiler Facts

- Exact symbol order: {', '.join(validated['symbols'])}
- Available source relations: {relation_labels}
- Required typed guard labels: {guard_labels}
- Frozen target reference: (symbol T)
- Guard labels in your program refer to the original Guard Program and the definitions below. The exact-result report may separately renumber factors; those are linked by their provenance, not by label equality.

# Exact Guard Reference Definitions

{guard_expressions}

# Required Output

Return only the complete Markdown certificate record required by the system
instructions.  The semantic lines and all certificate-program choices must be your
own mathematical work.  Do not emit JSON."""


def _with_user_semantics(model_call, semantics):
    """Keep legacy author notes as untrusted user data, never system rules."""
    context = "# Model-Authored Semantic Bindings — Untrusted Context\n\n" + "\n".join(
        f"- {key}: {value}" for key, value in semantics.items()) + "\n\n"

    def call(**kwargs):
        heading = "# Exact-Evidence Verdict"
        if kwargs["user_prompt"].count(heading) != 1:
            raise ValueError("ambiguous semantic-context insertion boundary")
        kwargs["user_prompt"] = kwargs["user_prompt"].replace(heading, context + heading, 1)
        return model_call(**kwargs)

    return call


def _generic_contract(program: Mapping[str, Any], *, conclusion_label: str = "C1") -> SynthesisContract:
    conclusion = str(program["semantics"]["required_conclusion"])
    return SynthesisContract(
        evidence_marker="[[VERIFIED_EXACT_EVIDENCE]]",
        rewrite_requirements=(
            "Define every formal symbol used in the inserted certificate from the theorem.",
            "Derive every selected source relation from the geometric or algebraic setup.",
            "Justify every typed nonzero guard before division or cancellation.",
            (
                "Use the inserted identities with their exact logical polarity and "
                "translate the certificate conclusion back to the theorem; do not cite an external computation."
            ),
            "Write a complete standalone proof and explicitly state the theorem conclusion.",
        ),
        literal_requirements=(
            LiteralRequirement("theorem_conclusion", (conclusion,)),
        ),
        conclusion_alternatives=(conclusion,),
        auditor_focus=(
            "Independently check the model-authored semantic bindings: every formal "
            "symbol and selected source relation must be derived from the theorem, all "
            "typed guards must be justified, the frozen target must have the claimed "
            "mathematical meaning, and the exact certificate must actually complete the proof."
        ),
        max_cycles=3,
    )


def _verify_synthesis_budget_forcing(
    *,
    synthesis_root: Path,
    synthesis: Mapping[str, Any],
    gemma: base.Role,
    qwen: base.Role,
    expected_timeout_sec: int | None = 600,
) -> list[dict[str, Any]]:
    """Rebind every accepted synthesis artifact to its forced Markdown response."""

    records: list[dict[str, Any]] = []
    for cycle in synthesis.get("cycles", []):
        number = int(cycle["cycle"])
        rewrite_path = (
            synthesis_root
            / f"02_rewrite/cycle_{number:02d}/raw_with_marker.md"
        )
        audit_path = synthesis_root / f"04_audit/cycle_{number:02d}/audit.md"
        rewrite = rewrite_path.read_text(encoding="utf-8").strip()
        audit = audit_path.read_text(encoding="utf-8").strip()
        rewrite_forcing = validate_markdown_budget_forcing(
            cycle["rewrite_call"],
            expected_stage="modular_exact_evidence_whole_proof_rewrite",
            expected_model=gemma.model,
            canonical_markdown=rewrite,
            expected_timeout_sec=expected_timeout_sec,
        )
        audit_forcing = validate_markdown_budget_forcing(
            cycle["audit_call"],
            expected_stage="modular_exact_evidence_whole_proof_audit",
            expected_model=qwen.model,
            canonical_markdown=audit,
            expected_timeout_sec=expected_timeout_sec,
        )
        records.append(
            {
                "cycle": number,
                "rewrite_budget_forcing_sha256": exact_tools.stable_hash(
                    rewrite_forcing
                ),
                "audit_budget_forcing_sha256": exact_tools.stable_hash(
                    audit_forcing
                ),
            }
        )
    if not records:
        raise ValueError("proof synthesis returned no budget-forced model cycle")
    return records


def generate_provider(
    *,
    task: TaskInputs,
    context: GenericCertificateContext,
    gemma: base.Role,
    output_dir: Path,
    master_seed: int,
    request_timeout_sec: int = 600,
    model_call: ModelCall | None = None,
) -> tuple[ModelAuthoredVerifiedCertificateProvider, dict[str, Any]]:
    """Ask the model for Markdown, then exactly verify its certificate program."""

    if gemma.reasoning_effort not in {"max", "xhigh", "ultra"}:
        raise ValueError("certificate author must use a deep reasoning effort")
    if task.theorem.strip() != context.theorem.strip():
        raise ValueError("certificate context theorem differs from synthesis task")
    exact_replay = validate_exact_replay(context.replay_exact())
    exact_sha256 = exact_tools.stable_hash(exact_replay)
    source_artifact_sha256 = {
        label: base.sha256_file(path)
        for label, path in sorted(context.source_artifacts.items())
    }
    selected_model_call = model_call or _mandatory_budget_forced_model_call
    text, verified, call = selected_model_call(
        role=gemma,
        system_prompt=CERTIFICATE_AUTHOR_SYSTEM,
        user_prompt=certificate_author_prompt(task=task, context=context),
        destination=output_dir,
        stage=CERTIFICATE_AUTHOR_STAGE,
        master_seed=master_seed,
        parser=lambda proposal: _verify_explicit_proposal(context, proposal, exact_replay),
        request_timeout_sec=request_timeout_sec,
    )
    forcing = validate_markdown_budget_forcing(
        call,
        expected_stage=CERTIFICATE_AUTHOR_STAGE,
        expected_model=gemma.model,
        canonical_markdown=text,
    )
    proposal_path = output_dir / "certificate_proposal.md"
    base.write_text(proposal_path, text)
    base.write_json(output_dir / "certificate_program.json", verified["program"])
    base.write_json(output_dir / "certificate_verification.json", verified["verification"])
    base.write_json(output_dir / "producer_call.json", call)
    provider = ModelAuthoredVerifiedCertificateProvider(
        context=context,
        proposal_path=proposal_path,
        expected_proposal_sha256=base.sha256_text(text),
        expected_exact_replay_sha256=exact_sha256,
        expected_source_artifact_sha256=source_artifact_sha256,
        expected_model=gemma.model,
        producer_call=call,
    )
    return provider, {
        "proposal_sha256": base.sha256_text(text),
        "exact_replay_sha256": exact_sha256,
        "source_artifact_sha256": source_artifact_sha256,
        "program_sha256": verified["verification"]["program_sha256"],
        "rendered_markdown_sha256": verified["verification"][
            "rendered_markdown_sha256"
        ],
        "budget_forcing_sha256": exact_tools.stable_hash(forcing),
        "producer_call": call,
    }


def run(
    *,
    task: TaskInputs,
    context: GenericCertificateContext,
    output_dir: Path,
    gemma: base.Role,
    qwen: base.Role,
    master_seed: int,
    request_timeout_sec: int = 600,
    model_call: ModelCall | None = None,
) -> dict[str, Any]:
    """Generate, verify, and synthesize from a model-authored certificate."""

    destination = output_dir.resolve()
    selected_model_call = model_call or _mandatory_budget_forced_model_call
    destination.mkdir(parents=True, exist_ok=False)
    preflight = {
        "schema": "cognitive-well-v0324-generic-certificate-run-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "state": "running",
        "problem_id": task.problem_id,
        "certificate_id": context.certificate_id,
        "model_output_format": "strict_markdown_with_fenced_sexpression_dsl",
        "json_model_output": False,
        "certificate_author": asdict(gemma),
        "proof_auditor": asdict(qwen),
        "certificate_author_deep_reasoning": True,
        "budget_forcing": "mandatory_for_certificate_author_rewriter_and_auditor",
        "operator_interventions": 0,
        "manual_certificate_content": False,
        "codex_model_calls": 0,
        "master_seed": master_seed,
    }
    base.write_json(destination / "manifest.json", preflight)
    try:
        provider, certificate_record = generate_provider(
            task=task,
            context=context,
            gemma=gemma,
            output_dir=destination / "01_certificate_author",
            master_seed=master_seed + 1_000,
            request_timeout_sec=request_timeout_sec,
            model_call=selected_model_call,
        )
        verified_bundle = provider.materialize()
        program = verify_and_render(
            context=context,
            proposal_markdown=provider.proposal_path.read_text(encoding="utf-8").strip(),
        )["program"]
        adapter = SynthesisAdapter(
            adapter_id=f"generic_verified_certificate__{context.certificate_id}",
            task=task,
            evidence_provider=provider,
            contract=_generic_contract(program),
        )
        synthesis = synthesis_pipeline.run(
            adapter=adapter,
            output_dir=destination / "02_proof_synthesis",
            gemma=gemma,
            qwen=qwen,
            master_seed=master_seed + 2_000,
            model_call=_with_user_semantics(selected_model_call, program["semantics"]),
        )
        synthesis_forcing = _verify_synthesis_budget_forcing(
            synthesis_root=destination / "02_proof_synthesis",
            synthesis=synthesis,
            gemma=gemma,
            qwen=qwen,
        )
        result = {
            **preflight,
            "state": "completed",
            "certificate": certificate_record,
            "evidence_sha256": base.sha256_text(verified_bundle.markdown),
            "synthesis_result": synthesis,
            "synthesis_budget_forcing": synthesis_forcing,
            "terminal_proof": synthesis["terminal_proof"],
            "terminal_proof_sha256": synthesis["terminal_proof_sha256"],
        }
        base.write_json(destination / "result.json", result)
        base.write_json(destination / "manifest.json", result)
        return result
    except Exception as error:
        failure = {
            **preflight,
            "state": "failed_closed",
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        base.write_json(destination / "failure.json", failure)
        base.write_json(destination / "manifest.json", failure)
        raise
