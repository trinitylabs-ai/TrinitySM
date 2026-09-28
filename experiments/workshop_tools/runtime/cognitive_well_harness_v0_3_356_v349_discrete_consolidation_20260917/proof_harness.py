"""Problem + proof -> model-selected algebra tool -> checked-appendix rewrite.

Use --execute-models to launch inference. Without it, only input snapshots and a
bounded run plan are written. No saved experiment, gold proof or score is loaded
by fresh runs. Internal JSON is bookkeeping, never a model response contract.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from pathlib import Path
import threading
import re

from . import HARNESS_REVISION, input_context, shared_feedback
from . import algebra_workflow, division_fresh_audited as fresh, final_revision, rewrite
from . import radical_resume_synthesis as resume
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT

base = rewrite.pipeline.base
acquisition = rewrite.acquisition
SCHEMA = "generic-checked-appendix-proof-harness-v1"
GEOMETRY_OPERATIONS = ('exact_geometry', 'rational_identity')
ROOT_OPERATIONS = ('real_root_classification',)
DISCRETE_OPERATIONS = ('uniform_partition_count', 'symbolic_modular_order')
EXECUTABLE_OPERATIONS = (rewrite.pipeline.exact_tools.IDEAL_OPERATION, *GEOMETRY_OPERATIONS, *ROOT_OPERATIONS, *DISCRETE_OPERATIONS)


def matcher_operations(excluded=()):
    # Accept historical exclusions, but advertise only complete automatic routes.
    known_operations=tuple(base.exact_tools.EXPOSED_OPERATIONS)+GEOMETRY_OPERATIONS+ROOT_OPERATIONS+DISCRETE_OPERATIONS
    if set(excluded)-set(known_operations):
        raise ValueError('unknown matcher operation exclusion')
    result=tuple(x for x in EXECUTABLE_OPERATIONS if x not in excluded)
    if not result:raise ValueError('cannot exclude all matcher operations')
    return result


def matcher_system(allowed):
    system=base.matcher_system(tuple(x for x in allowed if x not in GEOMETRY_OPERATIONS+ROOT_OPERATIONS+DISCRETE_OPERATIONS))
    if 'exact_geometry' in allowed:
        system+='\nUse exact_geometry for identities involving constructed points, equal ordinary angles, strict triangle interiors, incidence, circle centers or distances. A typed Cartesian program compiles source constraints and derives checked nonzero guards before polynomial certification.'
    if 'rational_identity' in allowed:
        system+='\nUse rational_identity for scalar rational consequences with explicitly justified denominators; the same exact compiler and certificate checks apply.'
    if 'real_root_classification' in allowed:
        system+='\nUse real_root_classification to find ALL real roots of a univariate polynomial, rational expression, or expression involving one variable-dependent square root on a finite exact interval. It also differentiates a supplied function and classifies all stationary points by exact derivative signs. Algebraic constant coefficients are supported. Original denominators must be nonzero and the variable radicand strictly positive throughout the interval; singular open endpoints are allowed. It checks the positive square-root branch and rejects extraneous roots from squaring. No free parameters or transcendental functions are supported. This is an executable audited route, including complete exact root isolation, sign classification, replay and proof synthesis.'
    if 'uniform_partition_count' in allowed:
        system+='\nUse uniform_partition_count to certify a lower bound on nonnegative K-subset sums of N labeled real weights with nonnegative total when K divides N. It counts equal-block partitions and their uniform incidences and supplies a checked double-counting proof. Parameters and source normalization must be model-derived.'
    if 'symbolic_modular_order' in allowed:
        system+='\nUse symbolic_modular_order to certify infinite exponent families for divisibility of exponential polynomial terms. For a model-chosen symbolic integer modulus M >= 2, bases, inverse polynomials, and exponent residue R, it verifies integer-polynomial identities and proves all positive exponents n congruent to R modulo phi(M). It does not guess a modulus or infer eventual constancy.'
    return system


def matcher_prompt(problem, proof, detection, allowed):
    legacy=tuple(x for x in allowed if x not in GEOMETRY_OPERATIONS+ROOT_OPERATIONS+DISCRETE_OPERATIONS)
    prompt=base.matcher_prompt(problem,proof,detection,legacy)
    additions=[x for x in GEOMETRY_OPERATIONS if x in allowed]
    if additions:prompt+='\n\nAdditional allowlisted operations: '+', '.join(additions)+'. These accept a source-bound construction program and certify its polynomial consequence. The formalizer receives the grammar after selection.'
    if 'real_root_classification' in allowed:
        prompt+='\n\nAdditional allowlisted operation: real_root_classification. It computes complete real-root sets and left/right signs, or stationary points and local min/max classifications, for an exact one-variable rational or single-square-root expression on a finite interval. The source function is differentiated by the tool in stationary-points mode. Algebraic constants, branch filtering and original denominator checks are included; no numerical root guessing is used. The formalizer receives the grammar after selection.'
    for op in DISCRETE_OPERATIONS:
        if op in allowed:
            description = ('Input: any N labeled real numbers with nonnegative total, and a positive integer K dividing N. Exact output: the number A of nonnegative-sum K-subsets satisfies A >= binomial(N,K)/(N/K) = binomial(N-1,K-1). This is a universal inequality over arbitrary real weights, with a complete partition-incidence proof; no sign-pattern enumeration or assumed extremizer is required.'
                if op == 'uniform_partition_count' else
                'Input: integer-polynomial modulus M >= 2, bases a, inverses b, offsets c, and integer residue R. It verifies a*b-1 and (a^R+c, using b^(-R) for negative R) are integer-polynomial multiples of M. Exact output: M divides a^n+c for EVERY positive n congruent to R modulo phi(M), and infinitely many such n exist. This can supply a common-divisor subsequence lemma in a convergence argument; the model must derive M and the surrounding contradiction.')
            prompt+='\n\nAdditional allowlisted operation: '+op+'. '+description+' The formalizer receives the typed grammar after selection.'
    return prompt


def detection_capabilities(allowed):
    descriptions = {
        'polynomial_ideal_membership': 'Exact polynomial consequences under recorded equations and nonzero conditions.',
        'exact_geometry': 'Exact consequences of source-derived planar constructions and real-domain conditions.',
        'rational_identity': 'Exact rational identities and symbolic scalar computations with explicit denominator conditions.',
        'real_root_classification': 'Complete roots or stationary points of supported one-variable expressions on an exact interval.',
        'uniform_partition_count': 'For N labeled real weights of nonnegative total and K dividing N, a partition-incidence certificate proves at least binomial(N-1,K-1) nonnegative-sum K-subsets. The source normalization and N,K must be derived.',
        'symbolic_modular_order': 'For model-derived integer-polynomial modulus M >= 2, bases, inverses, offsets and exponent residue R, exact polynomial identities certify divisibility of exponential terms for every positive n congruent to R modulo phi(M). This yields an infinite common-divisor subsequence when several terms share M. Choosing M and connecting this local lemma to the full theorem remain mathematical obligations.',
    }
    return ('\n\n# Available Exact Evidence Capabilities\n\n'
        + '\n'.join('- '+descriptions[op] for op in allowed)
        + '\n\nUse these general contracts to select a useful exactly checkable obligation. '
          'A source-derived local lemma is eligible when its downstream proof obligation is explicit. '
          'Do not assume a chosen parameter or an uncomputed result. Keep the required detector response format.')


def parse_matcher(text, desired, allowed):
    normalized, normalization = base.protocol.normalize_matcher(text, allowed_operations=allowed)
    parsed = base.mdp.parse_matcher(normalized, allowed)
    if parsed['call_requested'] and parsed['claim'] == 'DETECTED_CLAIM':
        if parsed['operation'] not in DISCRETE_OPERATIONS:
            raise ValueError('claim references require a discrete operation')
        bound, count = re.subn(r'(?ms)(^# Immutable Claim\s*\n).*?(?=^# Fit Rationale\s*\n)',
            lambda match: match[1]+'\n'+desired+'\n\n', normalized, count=1)
        if count != 1:
            raise ValueError('ambiguous immutable claim reference')
        result = base._parse_matcher(bound, desired, allowed)
        result.update(claim_reference='DETECTED_CLAIM', claim_sha256=base.sha256_text(desired),
                      reference_resolution='exact_upstream_detection_text')
        result['reference_input_normalization'] = normalization
        return result
    return base._parse_matcher(text, desired, allowed)


MATCHER_RESPONSE_TEMPLATE = """

Use one of the following complete response formats according to your decision.
Replace each angle-bracket placeholder with one nonempty paragraph. Put each
value on its own line below its heading. Return only the four Markdown sections,
without code fences or placeholder text.

For uniform_partition_count or symbolic_modular_order, write the literal
DETECTED_CLAIM under Immutable Claim. It references the single immutable desired
exact fact already supplied in this request. The host binds the reference to
that exact source text and its hash. Do not retype or paraphrase the claim.
For all other operations, copy the desired exact fact byte-for-byte as below.

If your decision is CALL_TOOL:

# Decision

CALL_TOOL

# Operation

<exactly one operation from the supplied allowlist>

# Immutable Claim

<copy the supplied desired exact fact byte-for-byte>

# Fit Rationale

<one paragraph explaining why the operation fits>

If your decision is NO_TOOL:

# Decision

NO_TOOL

# Operation

none

# Immutable Claim

NONE

# Fit Rationale

<one paragraph explaining why no allowed operation fits>
"""
FORMALIZER_SYSTEM = """You are a mathematical formalizer with access to a checked
algebra service. Read the original theorem, proof and model-recorded gap. Decide
CALL_TOOL or NO_TOOL and author all mathematical inputs yourself. Derive equations
from the hypotheses: the old proof and gap analysis are untrusted.

The service takes polynomial equations, a polynomial target and typed nonzero
conditions. Its deterministic cascade is guarded substitution/normalization and
polynomial division; guarded radical membership; eligible Laurent reduction;
then guarded radical membership of the reduced target. A positive result needs
an explicit re-expanded certificate and, when transformed, a checked source lift.
INCONCLUSIVE is not a disproof. The service proves only the supplied implication,
not your interpretation of the original theorem.

Use a small faithful representation. Explain each symbol, source equation,
target correspondence, denominator and nonzero condition in the requested
Markdown sections and source-grounded Domain Ledger. Retain boundary conditions
that the polynomial backend cannot express. Never assume the target as an input,
invent a guard or silently remove a branch. No example solution, successful
formalization or human mathematical representation is supplied.

Emit Markdown only, never JSON or executable code. Begin with # Decision and
CALL_TOOL, then the prescribed formalization sections. If a faithful encoding
is unavailable, emit # Decision with NO_TOOL, then # Reason. Do not guess results.
"""


@dataclass(frozen=True)
class Config:
    batch_size: int = 8
    workers: int = 8
    cycles: int = 3
    formalizer_temperature: float = 0.1
    division_timeout: int = 60
    algebra_timeout: int = 300
    memory_mb: int = 4096
    gemma_endpoint: str = "http://127.0.0.1:8030/v1"
    qwen_endpoint: str = "http://127.0.0.1:8027/v1"
    excluded_operations: tuple[str, ...] = ()
    proof_rewriter: str = "qwen"
    shared_lane_feedback: bool = True

    def validate(self):
        if type(self.shared_lane_feedback) is not bool:
            raise ValueError('shared lane feedback must be boolean')
        if self.proof_rewriter not in {"gemma", "qwen"}:
            raise ValueError("proof rewriter must be gemma or qwen")
        if not 1 <= self.workers <= self.batch_size <= 8 or not 1 <= self.cycles <= 3:
            raise ValueError("require 1 <= workers <= batch size <= 8 and 1 <= cycles <= 3")
        if not 1 <= self.division_timeout <= 600:
            raise ValueError("Division timeout must be in 1..600 seconds")
        if not 1 <= self.algebra_timeout <= 300:
            raise ValueError("Certificate search timeout must be in 1..300 seconds")
        if not 256 <= self.memory_mb <= 8192:
            raise ValueError("CPU worker memory must be in 256..8192 MiB")
        fresh.division.validate_temperature(self.formalizer_temperature)
        matcher_operations(self.excluded_operations)

    def gemma(self):
        return base.Role(self.gemma_endpoint, base.DEFAULT_GEMMA_MODEL, 0.2, "max")

    def qwen(self):
        return base.Role(self.qwen_endpoint, base.DEFAULT_QWEN_MODEL, 0.1, None)

    def proof_writer(self):
        """Select only the proof-writing role; acquisition/formalization are unchanged."""
        if self.proof_rewriter == "qwen":
            return replace(self.qwen(), temperature=0.2)
        if self.proof_rewriter == "gemma":
            return self.gemma()
        raise ValueError("proof rewriter must be gemma or qwen")

    @classmethod
    def from_saved(cls, values):
        # Older manifests predate this switch and used Gemma for synthesis.
        return cls(**{"proof_rewriter": "gemma", "shared_lane_feedback": False, **values})


def associated_context(documents):
    if set(documents) - {input_context.FUSION_DOCUMENT}:
        raise ValueError("unverified associated documents are not model context")
    return "" if not documents else ("\n\n# Associated Source Information — Untrusted Context\n\n"
        + "\n\n".join(f"## {name}\n\n{text}" for name, text in sorted(documents.items())))


def prepare(problem_file, proof_file, output, *, problem_id, config, seed, associated=(), fusion_result=None):
    config.validate()
    rewrite.assert_generic_boundary()
    if associated:
        raise ValueError("unverified or reserved associated documents are disabled; use a verified Fusion handoff")
    problem = acquisition.v0220.load_problem(problem_file, explicit_problem_id=problem_id)
    proof = proof_file.read_text().strip()
    if not proof:
        raise ValueError("input proof is empty")
    documents, provenance = input_context.from_fusion(fusion_result, problem, proof)
    output.mkdir(parents=True, exist_ok=False)
    # Snapshot only the statement and id, deliberately excluding any extra JSON
    # fields such as a reference solution in the caller's problem file.
    rewrite.write_record(output / "input/problem.json", {"problem_id": problem.problem_id, "statement": problem.statement})
    base.write_text(output / "input/source_proof.md", proof)
    for name, text in documents.items():
        base.write_text(output / "input/associated" / name, text)
    inputs = [output / "input/problem.json", output / "input/source_proof.md",
              *(output / "input/associated" / name for name in documents)]
    manifest = {"schema": SCHEMA, "state": "prepared", "problem_id": problem.problem_id,
        "master_seed": seed, "config": asdict(config),
        "input_artifacts": {str(path.relative_to(output)): base.sha256_file(path) for path in inputs},
        "associated_documents": sorted(documents), "model_output": "Markdown",
        "associated_provenance": provenance, "harness_revision": HARNESS_REVISION,
        "shared_feedback_policy": shared_feedback.POLICY if config.shared_lane_feedback else None,
        "shared_feedback_prompt_character_limit": shared_feedback.MAX_PROMPT_CHARS if config.shared_lane_feedback else 0,
        "generation_reference_reads": False,
        "budget_forcing": True, "preloaded_certificate": False, "gold_inputs": False,
        "backend_order": list(algebra_workflow.ORDER), "appendix_in_rewriter_prompt": False,
        "whole_proof_audit_includes_appendix": True, "synthesis_request_timeout": None,
        "max_logical_model_stages": 2 + 2 * config.cycles * config.batch_size + 8,
        "max_rewrite_cycles": 3, "final_qwen_revision": True,
        "proof_rewriter_model": config.proof_writer().model,
        "proof_rewriter_temperature": config.proof_writer().temperature,
        "final_revision_policy": final_revision.POLICY, "max_final_revision_cycles": 1,
        "strict_scoring": "separate_not_generation_feedback"}
    rewrite.write_record(output / "manifest.json", manifest)
    rewrite.write_record(output / "status.json", manifest)
    return manifest, documents


def reuse_detection(source, output):
    """Reuse a bound detector only; matching is a new, explicitly requested call."""
    source = source.resolve()
    previous, current = resume.read(source / "manifest.json"), resume.read(output / "manifest.json")
    if previous.get("schema") != SCHEMA or previous.get("input_artifacts") != current["input_artifacts"]:
        raise ValueError("saved detection belongs to different harness inputs")
    for name, digest in current["input_artifacts"].items():
        if base.sha256_file(source / name) != digest or base.sha256_file(output / name) != digest:
            raise ValueError("saved detection input drift")
    root = source / "01_acquisition"
    text = (root / "01_detection/detection.md").read_text().strip()
    parsed = acquisition.protocol.parse_detection(text)
    stage = "direct_laurent_gap_detection"
    rows = [row for row in resume.read(root / "model_budget.json")["calls"]
            if row["stage"] == stage and row["state"] == "completed"]
    if len(rows) != 1:
        raise ValueError("saved detection lacks a unique completed producer")
    row = rows[0]
    producer = root / "01_detection/model" / f"attempt_{row['attempt']:02d}_cap_{row['cap']}"
    metadata_path = producer / f"{stage}.metadata.json"
    metadata = resume.read(metadata_path)
    fresh.certificate.validate_markdown_budget_forcing(
        {"metadata": metadata, "attempt": row["attempt"], "cap": row["cap"],
         "request_timeout_sec": metadata["config"]["timeout_seconds"]},
        expected_stage=stage, expected_model=base.DEFAULT_QWEN_MODEL, canonical_markdown=text)
    binding = {"source_run": str(source), "detection_sha256": base.sha256_text(text),
        "producer_metadata_sha256": base.sha256_file(metadata_path),
        "input_artifacts": current["input_artifacts"], "new_detection_calls": 0,
        "old_matcher_reused": False}
    rewrite.write_record(output / "01_acquisition/01_detection/reuse.json", binding)
    return text, parsed


def reuse_acquisition(source, output, config):
    """Reuse both bound, validated model producers, without calling a model."""
    import shutil
    source=source.resolve()
    detection_text,detection=reuse_detection(source,output)
    if not detection['call_requested']:
        raise ValueError('saved detection did not request a tool')
    root=source/'01_acquisition'
    allowed=matcher_operations(config.excluded_operations)
    previous=resume.read(root/'manifest.json')
    if previous['allowed_matcher_operations'] != list(allowed):
        raise ValueError('saved matcher operation menu differs')
    problem=resume.read(output/'input/problem.json')
    if ((root/'input/original_theorem.md').read_text().strip()!=problem['statement'].strip()
            or (root/'input/resolver1_proof.md').read_text().strip()
               !=(output/'input/source_proof.md').read_text().strip()):
        raise ValueError('saved acquisition source drift')
    text=(root/'02_matcher/matcher.md').read_text().strip()
    matcher=parse_matcher(text,detection['desired_exact_fact'],allowed)
    if not matcher['call_requested']:
        raise ValueError('saved matcher did not request a tool')
    budget=resume.read(root/'model_budget.json')
    stage='direct_laurent_operation_matcher'
    rows=[r for r in budget['calls'] if r['stage']==stage and r['state']=='completed']
    if len(rows)!=1:
        raise ValueError('saved matcher lacks a unique completed producer')
    row=rows[0]
    metadata_path=root/'02_matcher/model'/f"attempt_{row['attempt']:02d}_cap_{row['cap']}"/f'{stage}.metadata.json'
    metadata=resume.read(metadata_path)
    fresh.certificate.validate_markdown_budget_forcing(
        {'metadata':metadata,'attempt':row['attempt'],'cap':row['cap'],
         'request_timeout_sec':metadata['config']['timeout_seconds']},
        expected_stage=stage,expected_model=base.DEFAULT_QWEN_MODEL,canonical_markdown=text)
    destination=output/'01_acquisition'
    for name in ['01_detection','02_matcher']:
        shutil.copytree(root/name,destination/name,dirs_exist_ok=True)
    for name in ['original_theorem.md','resolver1_proof.md']:
        base.write_text(destination/'input'/name,(root/'input'/name).read_text().strip())
    rewrite.write_record(destination/'manifest.json',{**previous,'reuse_source':str(source),
        'problem_file':str(output/'input/problem.json'),'resolver1_proof':str(output/'input/source_proof.md')})
    rewrite.write_record(destination/'model_budget.json',{**budget,'max_model_stages':0,
        'new_model_calls':0,'calls':[{**r,'reused':True} for r in budget['calls']]})
    binding={'source_run':str(source),'new_detection_calls':0,'new_matcher_calls':0,
        'input_artifacts':resume.read(output/'manifest.json')['input_artifacts'],
        'detection_sha256':base.sha256_text(detection_text),'matcher_sha256':base.sha256_text(text),
        'matcher_metadata_sha256':base.sha256_file(metadata_path)}
    rewrite.write_record(destination/'reuse.json',binding)
    return {'decision':'CALL_TOOL','record':matcher,'reuse':binding}


def acquire(output, *, config, seed, documents, caller=None, detection_from=None, acquisition_from=None):
    """Match once, optionally reusing detection for an explicit menu experiment."""
    if acquisition_from:
        return reuse_acquisition(acquisition_from,output,config)
    root = output / "01_acquisition"
    problem_path, proof_path = output / "input/problem.json", output / "input/source_proof.md"
    problem = acquisition.v0220.load_problem(problem_path)
    proof = proof_path.read_text().strip()
    base.write_text(root / "input/original_theorem.md", problem.statement)
    base.write_text(root / "input/resolver1_proof.md", proof)
    manifest = {"problem_id": problem.problem_id, "problem_file": str(problem_path),
        "resolver1_proof": str(proof_path), "problem_file_sha256": base.sha256_file(problem_path),
        "resolver1_proof_sha256": base.sha256_text(proof),
        "allowed_matcher_operations": list(matcher_operations(config.excluded_operations)),
        "excluded_matcher_operations": list(config.excluded_operations)}
    rewrite.write_record(root / "manifest.json", manifest)
    calls = caller or rewrite.BudgetedCalls(root / "model_budget.json", max_stages=1 if detection_from else 2)
    allowed = matcher_operations(config.excluded_operations)
    if detection_from:
        detection_text, detection = reuse_detection(detection_from, output)
    else:
        detection_text, detection, call = calls(role=config.qwen(), system_prompt=base.DETECTOR_SYSTEM,
            user_prompt=base.detection_prompt(problem, proof, acquisition.protocol.compression_candidates(proof))
                + detection_capabilities(allowed) + associated_context(documents), destination=root / "01_detection/model",
            stage="direct_laurent_gap_detection", master_seed=seed, parser=acquisition.protocol.parse_detection)
    base.write_text(root / "01_detection/detection.md", detection_text)
    if not detection["call_requested"]:
        return {"decision": "NO_TOOL", "stage": "detection", "record": detection}
    matcher_text, matcher, call = calls(role=config.qwen(),
        system_prompt=matcher_system(allowed) + MATCHER_RESPONSE_TEMPLATE,
        user_prompt=matcher_prompt(problem, proof, detection, allowed) + associated_context(documents),
        destination=root / "02_matcher/model", stage="direct_laurent_operation_matcher", master_seed=seed,
        parser=lambda text: parse_matcher(text, detection["desired_exact_fact"], allowed))
    base.write_text(root / "02_matcher/matcher.md", matcher_text)
    if not matcher["call_requested"]:
        return {"decision": "NO_TOOL", "stage": "matcher", "record": matcher}
    if matcher["operation"] not in EXECUTABLE_OPERATIONS:
        return {"decision": "UNSUPPORTED_OPERATION", "record": matcher}
    return {"decision": "CALL_TOOL", "record": matcher}


def publish(output, status):
    """A whole-proof PASS is separate from verified conditional algebra."""
    selected = status.get("selected", {})
    packaged = selected.get("result", {})
    synthesis = packaged.get("synthesis", {})
    status.update(proof_audit_passed=False, strict_score=None)
    if packaged.get("state") == "completed" and synthesis.get("proof_audit_passed") is True:
        source = Path(synthesis["terminal_proof"])
        if base.sha256_text(source.read_text().strip()) != synthesis["terminal_proof_sha256"]:
            raise ValueError("rewritten proof hash mismatch")
        proof = source.read_text().strip()
        base.write_text(output / "rewritten_proof.md", proof)
        status.update(state="completed", outcome="REWRITTEN_AUDIT_PASS", proof_audit_passed=True,
            rewritten_proof=str(output / "rewritten_proof.md"),
            rewritten_proof_sha256=base.sha256_text(proof))
        if "final_qwen_revision" in synthesis:
            status["final_qwen_revision"] = synthesis["final_qwen_revision"]
    elif selected:
        status.update(state="failed_closed", outcome="CERTIFIED_LEMMA_REWRITE_NOT_ACCEPTED")
    else:
        status.setdefault("outcome", "NO_CERTIFIED_REWRITE")
    rewrite.write_record(output / "status.json", status)
    rewrite.write_record(output / "result.json", status)
    return status


def run(*, problem_file, proof_file, output, problem_id=None, seed=1,
        config=None, associated=(), execute_models=False, detection_from=None, fusion_result=None,
        acquisition_from=None):
    if detection_from and acquisition_from:
        raise ValueError('choose detection-only or complete acquisition reuse')
    config = config or Config()
    output = output.resolve()
    manifest, documents = prepare(problem_file, proof_file, output, problem_id=problem_id,
        config=config, seed=seed, associated=associated, fusion_result=fusion_result)
    if acquisition_from:
        reuse_acquisition(acquisition_from,output,config)
        manifest.update(acquisition_from=str(acquisition_from.resolve()),
            max_logical_model_stages=manifest['max_logical_model_stages']-2)
        rewrite.write_record(output/'manifest.json',manifest)
        rewrite.write_record(output/'status.json',manifest)
    if detection_from:
        reuse_detection(detection_from, output)
        manifest.update(detection_from=str(detection_from.resolve()),
            max_logical_model_stages=manifest["max_logical_model_stages"] - 1)
        rewrite.write_record(output / "manifest.json", manifest)
        rewrite.write_record(output / "status.json", manifest)
    if not execute_models:
        return manifest
    status = {"schema": SCHEMA, "state": "running",
              "stage": "formalization_audit_tools" if acquisition_from else "matching" if detection_from else "detection", "samples": []}
    rewrite.write_record(output / "status.json", status)
    stop, selection_lock = threading.Event(), threading.Lock()
    peer_board = None

    def validate_inputs():
        if {name: base.sha256_file(output / name) for name in manifest["input_artifacts"]} != manifest["input_artifacts"]:
            raise ValueError("frozen harness input drift")

    def select(request_path, operation):
        with selection_lock:
            if stop.is_set():
                return {"state": "superseded_by_verified_candidate"}
            validate_inputs()
            stop.set()
            status.update(stage="proof_synthesis", selected={"request_path": str(request_path), "state": "running"})
            rewrite.write_record(output / "selection.json", status["selected"])
            rewrite.write_record(output / "status.json", status)
        result = operation()
        with selection_lock:
            status["selected"].update(state=result["state"], result=result)
            rewrite.write_record(output / "selection.json", status["selected"])
            rewrite.write_record(output / "status.json", status)
        return result

    def track(index):
        if stop.is_set():
            return {"sample": index, "state": "superseded_by_verified_candidate"}
        root = output / "02_formalizations" / f"sample_{index:02d}"
        track_seed = base.stable_seed(seed, f"guarded-formalization-sample:{index}")
        feedback = peer_board.lane(index) if peer_board else None
        if status['acquisition']['record']['operation'] in DISCRETE_OPERATIONS:
            from . import discrete_workflow
            result=discrete_workflow.run_track(output,root,config=config,seed=track_seed,
                matcher=status['acquisition']['record'],select=select,should_stop=stop.is_set,feedback=feedback)
            return {'sample':index,'output':str(root),**result}
        if status['acquisition']['record']['operation'] in ROOT_OPERATIONS:
            from . import root_workflow
            result=root_workflow.run_track(output,root,config=config,seed=track_seed,
                matcher=status['acquisition']['record'],select=select,should_stop=stop.is_set,feedback=feedback)
            return {'sample':index,'output':str(root),**result}
        if status['acquisition']['record']['operation'] in GEOMETRY_OPERATIONS:
            from . import geometry_workflow
            result=geometry_workflow.run_track(output,root,config=config,seed=track_seed,
                matcher=status['acquisition']['record'],select=select,should_stop=stop.is_set,feedback=feedback)
            return {'sample':index,'output':str(root),**result}
        row = fresh.run(output / "01_acquisition", root, track_seed, False,
            auditor="gemma", cycles=config.cycles, domain_ledger=True,
            formalizer_temperature=config.formalizer_temperature)
        contract = (root / "formalizer_user.md").read_text().replace(
            "The backend is guarded rational substitution and polynomial division only.",
            "The backend is the deterministic checked algebra cascade described in the system contract.")
        base.write_text(root / "formalizer_user.md", contract)
        base.write_text(root / "formalizer_system.md", FORMALIZER_SYSTEM)
        row.update(backend="checked_algebra_cascade", tool_timeout_seconds=config.algebra_timeout,
                   backend_order=list(algebra_workflow.ORDER),
                   peer_feedback_to_formalizer_retries=feedback is not None, auditor_peer_feedback=False)
        rewrite.write_record(root / "manifest.json", row)
        calls = rewrite.BudgetedCalls(root / "model_budget.json", max_stages=2 * config.cycles)

        def call(**kwargs):
            validate_inputs()
            role = kwargs["role"]
            kwargs["role"] = replace(role, endpoint=config.gemma_endpoint if role.model == base.DEFAULT_GEMMA_MODEL else config.qwen_endpoint)
            kwargs["user_prompt"] += associated_context(documents)
            return calls(**kwargs)

        result = fresh.execute(root, row, contract, track_seed, auditor="gemma", cycles=config.cycles,
            caller=call, formalizer_system=FORMALIZER_SYSTEM, should_stop=stop.is_set, feedback=feedback,
            tool=lambda parsed, destination: algebra_workflow.execute(parsed, destination,
                config=config, seed=track_seed, documents=documents, select=select, should_stop=stop.is_set))
        return {"sample": index, "output": str(root), **result}

    try:
        decision = acquire(output, config=config, seed=seed, documents=documents,
                           detection_from=detection_from,acquisition_from=acquisition_from)
        status["acquisition"] = decision
        if decision["decision"] != "CALL_TOOL":
            status.update(state="completed", outcome=decision["decision"], input_proof_unchanged=True)
        else:
            status.update(stage="formalization_audit_tools")
            rewrite.write_record(output / "status.json", status)
            if config.shared_lane_feedback:
                peer_board = shared_feedback.Board(output/'shared_feedback',
                    input_artifacts={**manifest['input_artifacts'], **{
                        str(p.relative_to(output)):base.sha256_file(p) for p in (
                            output/'01_acquisition/01_detection/detection.md',
                            output/'01_acquisition/02_matcher/matcher.md')}},
                    samples=config.batch_size, cycles=config.cycles, master_seed=seed)
            with ThreadPoolExecutor(max_workers=config.workers) as pool:
                jobs = [pool.submit(track, index) for index in range(1, config.batch_size + 1)]
                for future in as_completed(jobs):
                    result = future.result()
                    with selection_lock:
                        status["samples"].append(result)
                        rewrite.write_record(output / "status.json", status)
            failed = any(row.get("state") == "failed_closed" for row in status["samples"])
            if failed:
                # In particular, do not publish a selected proof after a late
                # contradiction or broken binding in that candidate's worker.
                selected_path = status.get("selected", {}).get("request_path", "")
                if any(row.get("state") == "failed_closed" and selected_path.startswith(row.get("output", "\0") + "/")
                       for row in status["samples"]):
                    status["selected"]["result"] = {"state": "failed_closed"}
            status.update(state="failed_closed" if failed and not status.get("selected") else "completed")
        validate_inputs()
        return publish(output, status)
    except Exception as error:
        status.update(state="failed_closed", error=f"{type(error).__name__}: {error}")
        rewrite.write_record(output / "status.json", status)
        rewrite.write_record(output / "result.json", status)
        return status


def run_matched_tool(*, operation, arguments_markdown, output, timeout_seconds=60, memory_mb=2048):
    """Explicit deterministic handoff after selection and formalization.

    This entry does not acquire model decisions or enter theorem synthesis. Its
    local/conditional evidence still needs the caller's source-semantic audit.
    """
    from . import matched_tools

    return matched_tools.run(operation=operation, arguments_markdown=arguments_markdown,
        output=output, timeout_seconds=timeout_seconds, memory_mb=memory_mb)


def resume_certified(trial, output, *, seed, appendix_from=None, config=None):
    """Explicit certified-checkpoint entry: no detection, formalization or solver search."""
    output = output.resolve()
    config = config or Config()
    config.validate()
    # The existing loader reparses the accepted draft and binds the exact input,
    # semantic audit, coefficient certificate, guards and any required source lift.
    result = resume.run(trial.resolve(), output, seed, no_time_limit=True,
        with_appendix=True, appendix_attach_only=True,
        gemma=config.proof_writer(), qwen=config.qwen(),
        appendix_from=appendix_from.resolve() if appendix_from else None)
    return publish(output, {"schema": SCHEMA, "state": result["state"],
        "mode": "resume_certified", "config": asdict(config),
        "selected": {"certified_trial": str(trial), "result": result}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem-file", type=Path)
    parser.add_argument("--problem-id")
    parser.add_argument("--proof-file", type=Path)
    parser.add_argument("--associated", type=Path, action="append", default=[],
        help="Deprecated: arbitrary associated files are rejected before reading")
    parser.add_argument("--fusion-result", type=Path,
        help="Verified effective Fusion artifact bound to the same problem and proof")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, required=True)
    parser.add_argument("--execute-models", action="store_true")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--formalizer-temperature", type=float, default=.1)
    parser.add_argument("--no-shared-feedback", action="store_true",
        help="Disable same-run peer feedback on formalizer retries")
    parser.add_argument("--gemma-endpoint", default=Config.gemma_endpoint)
    parser.add_argument("--qwen-endpoint", default=Config.qwen_endpoint)
    parser.add_argument("--proof-rewriter", choices=("gemma", "qwen"), default=Config.proof_rewriter)
    parser.add_argument("--exclude-operation", action="append", default=[])
    parser.add_argument("--detection-from", type=Path, help="Reuse detection from a bound harness run; rerun matching")
    parser.add_argument("--acquisition-from",type=Path,help="Reuse both bound detection and matching; start with formalization")
    parser.add_argument("--resume-certified-trial", type=Path)
    parser.add_argument("--appendix-from", type=Path)
    args = parser.parse_args()
    config = Config(batch_size=args.batch_size, workers=args.workers if args.workers is not None else args.batch_size,
        cycles=args.cycles, formalizer_temperature=args.formalizer_temperature,
        gemma_endpoint=args.gemma_endpoint, qwen_endpoint=args.qwen_endpoint,
        proof_rewriter=args.proof_rewriter, excluded_operations=tuple(args.exclude_operation),
        shared_lane_feedback=not args.no_shared_feedback)
    if args.resume_certified_trial:
        if not args.execute_models or args.problem_file or args.proof_file or args.associated or args.detection_from or args.fusion_result or args.acquisition_from:
            parser.error("certified resume requires --execute-models and uses its bound original inputs")
        result = resume_certified(args.resume_certified_trial, args.output_dir,
            seed=args.master_seed, appendix_from=args.appendix_from, config=config)
    else:
        if not args.problem_file or not args.proof_file or args.appendix_from:
            parser.error("fresh mode needs --problem-file and --proof-file; --appendix-from is resume-only")
        result = run(problem_file=args.problem_file, proof_file=args.proof_file, problem_id=args.problem_id,
            output=args.output_dir, seed=args.master_seed, config=config, associated=args.associated,
            execute_models=args.execute_models, detection_from=args.detection_from, fusion_result=args.fusion_result,
            acquisition_from=args.acquisition_from)
    print(f"{result['state']}: {result.get('outcome', 'prepared')}")
    print(args.output_dir.resolve() / "status.json")
    return int(result["state"] == "failed_closed")


if __name__ == "__main__":
    raise SystemExit(main())
