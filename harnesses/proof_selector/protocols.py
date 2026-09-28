"""Read-only reuse of pinned proof-review contracts; no legacy runtime imports."""
from __future__ import annotations

import ast
from functools import lru_cache
import hashlib
import importlib.util
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / 'harnesses/imo_proof_pipeline/releases/1.7.0/engine/source'
SOURCES = {
    'reviewer_1': ('cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823/protocol.py',
                   '0088a37c39159f8a23a9a13ce6d68b283979bcd2acd0a018a7dc2adecf54d518'),
    'reviewer_2': ('cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823/protocol.py',
                   '5aef28d9aa4785ca7e3854b73c20c54910d4ccddc5709025ff373ce0c1e262d0'),
    'reviewer_3': ('cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823/protocol.py',
                   'eccb6918c5464d2b64f396bcf782d89d99818399d7922dcfc151226f660a8879'),
    'fusion': ('cognitive_well_harness_v0_3_53_fusion_20260823/protocol.py',
               '82200768ec47b6c0167aabf5aab47f2706d80aad0d1384a513f33cac5b7b6f64'),
    'acceptance': ('cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906/repair_boundary.py',
                   '869cf1e280e0537e727e572f3b14887ad4791beb59af43a8f38a695ba5475f7d'),
}


def sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _source(name):
    relative, expected = SOURCES[name]
    path = ENGINE / relative
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(f'Pinned selector protocol changed: {relative}')
    return path, raw.decode('utf-8')


@lru_cache(maxsize=4)
def _protocol(name):
    path, source = _source(name)
    # These protocol files contain only constants and pure parsers/builders.
    # Loading a file directly avoids importing the legacy package initializers,
    # stage runners, transport wrappers, or their process-wide monkeypatches.
    spec = importlib.util.spec_from_file_location('_proof_selector_' + name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


def reviewer(index):
    if index not in (1, 2, 3):
        raise ValueError('Reviewer index must be 1, 2 or 3')
    return _protocol(f'reviewer_{index}')


def fusion():
    return _protocol('fusion')


def _acceptance_contract():
    path, source = _source('acceptance')
    names = {'ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT', 'sha256_text',
             '_markdown_section', 'parse_acceptance_certification_markdown',
             '_acceptance_user_prompt'}
    selected, found = [], set()
    for node in ast.parse(source).body:
        name = node.name if isinstance(node, ast.FunctionDef) else (
            node.targets[0].id if isinstance(node, ast.Assign)
            and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) else None)
        if name in names:
            selected.append(node)
            found.add(name)
    if found != names:
        raise ValueError('Pinned acceptance contract is incomplete')
    # Execute exactly these pure definitions, not repair_boundary's imports or
    # top-level backend state. Their complete source file is hash checked above.
    namespace = {'re': re, 'hashlib': hashlib, 'Any': Any}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


_acceptance = _acceptance_contract()
ACCEPTANCE_SYSTEM = _acceptance['ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT']
acceptance_user_prompt = _acceptance['_acceptance_user_prompt']


def parse_acceptance(value):
    parsed = _acceptance['parse_acceptance_certification_markdown'](value)
    # The pinned parser matches verdicts case-insensitively but its semantic
    # checks require uppercase. Reject other spellings here so the client can
    # retry formatting; uppercasing afterward would skip those semantic checks.
    if parsed.get('verdict') not in {'CERTIFIED', 'REJECTED'}:
        parsed = {**parsed, 'valid': False,
                  'errors': [*parsed.get('errors', []), 'Use uppercase CERTIFIED or REJECTED']}
    return parsed

CRITIQUE_SYSTEM = """You independently audit a Fusion assessment of an Olympiad proof.
Read the entire problem and unchanged submitted proof. The Fusion assessment is
untrusted. Check its precise alleged defect or unresolved obligation against the
proof, including later justifications and valid standard Olympiad mathematics.
Try to refute the criticism before endorsing it. Verify any witness, quantifier,
calculation, missing case, and claimed effect on the conclusion. Do not invent a
new nontrivial lemma or repair and credit it to the submitted proof.

SUPPORTED means the assessment and its stated uncertainty are justified by the
written evidence. A supported REPAIR_NEEDED assessment still identifies a flawed
proof; it does not certify the proof or a hypothetical repair. CHALLENGED means
you have a concrete reason that the assessment is mistaken. UNRESOLVED means
you cannot settle the decisive issue. Do not infer correctness from agreement,
confidence, report length, or a proposed repair. Do not use a reference solution.

Return exactly this record, with one nonempty physical line per field:
CRITIQUE_AUDIT
verdict: SUPPORTED or CHALLENGED or UNRESOLVED
target: <precise disputed claim or obligation>
proof_evidence: <relevant written support or its absence>
independent_check: <your mathematical check of the assessment>
consequence: <effect on the assessment, with any remaining uncertainty>
END_CRITIQUE_AUDIT"""

COMPARE_SYSTEM = """Select the stronger of two unchanged Olympiad proof candidates
using their independently produced assessment records. You receive the problem
and two evidence packets, not the complete proofs. These model assessments are
fallible; compare their concrete mathematical grounds and preserve uncertainty.

Prefer evidence for a complete valid route to the required conclusion. Allow
genuinely routine omissions, but never credit an unwritten nontrivial repair.
If both candidates are flawed, compare the meaningful progress actually supported
and the importance of the unresolved obligations. Do not count objections or use
confidence, verbosity, stylistic polish, or the number of agreeing reviewers as
a proxy for correctness. Do not invent unseen proof passages. Choose UNDECIDED
when these packets do not support a mathematical preference.

If earlier comparisons are supplied, treat their reasons as disputed claims.
Resolve their mathematical disagreement from the evidence; do not take a vote.
You must select an existing candidate or remain undecided, never combine proofs.
Do not use reference solutions or external grades.

Return exactly this record, with one nonempty physical line per field:
PROOF_COMPARISON
winner: A or B or UNDECIDED
decisive_obligation: <the obligation that determines the comparison>
evidence_a: <candidate A's relevant support and uncertainty>
evidence_b: <candidate B's relevant support and uncertainty>
reason: <why one is stronger, or why no preference is established>
END_PROOF_COMPARISON"""

CONTINUATIONS = {
    'reviewer_1': (
        'Wait. I should check whether the apparent first break is justified later '
        'in the proof or by a valid standard result. If I found no break, I should '
        'retrace the load-bearing implications and boundary cases. I must identify '
        'the earliest genuine failure without inventing a repair, then finish in '
        'the original required format.'),
    'reviewer_2': (
        'Wait. I should verify that my proposed witness satisfies every hypothesis '
        'and actually defeats the target claim. I should try to refute my own attack '
        'using the submitted proof. If no decisive attack survives, I should say so. '
        'I must distinguish a false objection from a real flaw and finish in the '
        'original required format.'),
    'reviewer_3': (
        'Wait. I should reconstruct the complete route to the conclusion and check '
        'every critical obligation. I must distinguish a routine completion from '
        'a new nontrivial lemma, and check that apparent gaps cannot be closed by '
        'the written material. I should reconsider both acceptance and rejection, '
        'then finish in the original required format.'),
    'fusion': (
        'Wait. I should test each decisive criticism against the actual proof and '
        'reconsider any unsupported acceptance. I must resolve disagreements using '
        'the stated hypotheses, witnesses, and implications, not reviewer agreement '
        'or confidence. Any routine completion must really be routine. I should '
        'retain uncertainty where necessary and finish in the original Fusion format.'),
    'acceptance': (
        'Wait. I should independently recheck the implications carrying the '
        'acceptance decision, especially quantifiers, boundary cases, and transitions '
        'from local facts to the full conclusion. I must not supply a new proof '
        'idea and count it as written support. I should verify any alleged defect '
        'as carefully as acceptance, then finish in the required audit format.'),
    'critique': (
        'Wait. I should try to disprove the assessment using the complete submitted '
        'proof, then test whether its criticism really changes the conclusion. '
        'An unsupported criticism does not establish that the proof is correct. '
        'I must preserve this distinction, check the decisive mathematical evidence, '
        'and finish in the original audit format.'),
    'comparison': (
        'Wait. I should compare the support for the decisive obligation in both '
        'packets again. A proposed repair is not part of the submitted proof, and '
        'a confident assessment is not additional evidence. I should select only '
        'when there is a concrete mathematical preference; otherwise remain '
        'UNDECIDED. I must finish in the original comparison format.'),
    'arbitration': (
        'Wait. I should isolate the mathematical disagreement between the two '
        'comparisons and check which premises are supported by the candidate '
        'records. I must not resolve it by voting or inventing missing proof '
        'details. If the evidence cannot distinguish the candidates, I should '
        'remain UNDECIDED and finish in the original comparison format.'),
}


def critique_user_prompt(*, problem, proof, fusion_record):
    return (f'## Problem\n{problem}\n\n## Submitted proof\n{proof}\n\n'
            f'## Untrusted Fusion assessment\n{fusion_record}')


def compare_user_prompt(*, problem, record_a, record_b, decisions=None):
    text = (f'## Problem\n{problem}\n\n## Candidate A evidence\n{record_a}\n\n'
            f'## Candidate B evidence\n{record_b}')
    if decisions:
        text += f'\n\n## Disputed comparison reasons\n{decisions}'
    return text


def _record(value, header, names, choice_field, allowed):
    text = value.strip()
    lines, errors, fields = text.splitlines(), [], {}
    if len(lines) != len(names) + 2 or not lines or lines[0] != header or lines[-1] != 'END_' + header:
        errors.append(f'Expected exactly one {header} record with one physical line per field')
    else:
        for line, name in zip(lines[1:-1], names):
            prefix = name + ': '
            if not line.startswith(prefix):
                errors.append(f'Expected field {name}')
                continue
            content = line[len(prefix):].strip()
            if not content or (content.startswith('<') and content.endswith('>')):
                errors.append(f'Empty or placeholder field {name}')
            fields[name] = content
    if fields.get(choice_field) not in allowed:
        errors.append(f'Invalid {choice_field}')
    return {'valid': not errors, 'errors': errors, 'fields': fields,
            choice_field: fields.get(choice_field) if not errors else None, 'text': text}


def parse_critique(value):
    return _record(value, 'CRITIQUE_AUDIT',
                   ('verdict', 'target', 'proof_evidence', 'independent_check', 'consequence'),
                   'verdict', {'SUPPORTED', 'CHALLENGED', 'UNRESOLVED'})


def parse_compare(value):
    return _record(value, 'PROOF_COMPARISON',
                   ('winner', 'decisive_obligation', 'evidence_a', 'evidence_b', 'reason'),
                   'winner', {'A', 'B', 'UNDECIDED'})


def protocol_identity():
    source_rows = {}
    for name, (relative, expected) in SOURCES.items():
        _source(name)
        source_rows[name] = {'path': str((ENGINE / relative).relative_to(ROOT)), 'sha256': expected}
    prompts = {f'reviewer_{i}': reviewer(i).SYSTEM_PROMPT for i in (1, 2, 3)}
    prompts.update(fusion=fusion().SYSTEM_PROMPT, acceptance=ACCEPTANCE_SYSTEM,
                   critique=CRITIQUE_SYSTEM, comparison=COMPARE_SYSTEM)
    return {'sources': source_rows,
            'system_prompts': {k: {'sha256': sha(v), 'words': len(v.split())} for k, v in prompts.items()},
            'continuations': {k: {'text': v, 'sha256': sha(v), 'words': len(v.split())}
                              for k, v in CONTINUATIONS.items()}}
