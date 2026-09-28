"""Source-audited discrete certificates with replayed proof-synthesis evidence."""
from dataclasses import replace
import json
from pathlib import Path

from . import discrete_certificates as engine
from . import geometry_workflow as common
from . import rewrite, certificate, division_audit_repair as audit, appendix_synthesis, shared_feedback
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import EvidenceBundle, TaskInputs
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT

base = rewrite.pipeline.base
read = common.read
FORMALIZER_SYSTEM = """You are a mathematical formalizer for checked counting
and modular arithmetic. Encode the matcher's Immutable Claim with the supplied
generic contract. Derive all mathematical inputs yourself from the original
problem and the untrusted submitted proof. No saved solution, successful program,
reference proof, or operator mathematical hint is supplied. Explain parameter
meanings, normalization, every hypothesis and the exact correspondence between
the returned conditional lemma and the missing step. The tool proves only its
stated scope; do not claim it proves an unrelated theorem. Never assume the
missing conclusion. Return Markdown only, in the requested sections."""
AUDIT_EXTRA = """This is a conditional counting or modular-order certificate.
Check the chosen operation's exact contract and the compiled domain. For counting,
check the labeled population, subset size, normalization and nonnegative total.
For modular arithmetic, check integer domains, the original exponential terms,
the proposed modulus and its M >= 2 condition, and whether the infinite exponent
family would supply the actual missing step. The deterministic checker will verify
all polynomial inverse and residual identities; do not prejudge those identities
as tool successes. A conditional local lemma need not prove the whole theorem,
but its hypotheses must be source-justified or explicitly isolated as cases that
the final proof must cover. Reject circular assumptions or irrelevant results.
Do not author a replacement formalization."""


def compile_bounded(text, theorem, config=None):
    return common.bounded(engine.compile_program, (text, theorem), timeout=120,
        memory=config.memory_mb if config else 4096)


def inspect(text, theorem, config):
    try:
        # Production formalizations need source bindings, unlike standalone calls.
        if text.strip().startswith('```'):
            raise ValueError('formalizer must supply Decision and Semantic Bindings sections')
        return {'parser_valid': True, 'proposal': compile_bounded(text, theorem, config)}
    except (ValueError, TimeoutError) as error:
        return {'parser_valid': False, 'parser_feedback': str(error)}


def audit_view(compiled):
    return '# Deterministic Discrete Compilation\n\n```json\n'+json.dumps(compiled['report'], separators=(',', ':'))+'\n```'


def execute(text, config):
    return common.bounded(engine.compute, (text,), timeout=config.algebra_timeout, memory=config.memory_mb)


def replay(text, saved, config):
    actual = execute(text, config)
    if actual != saved or not actual.get('verified'):
        raise ValueError('discrete certificate replay differs from saved evidence')
    return actual


class DiscreteProvider:
    provider_id = 'checked_discrete_certificates_v1'

    def __init__(self, *, inputs, cycle, matcher, config):
        self.config = config
        self.paths = {**inputs, 'draft': cycle/'formalization.md', 'compilation': cycle/'compilation.json',
            'semantic_audit': cycle/'audit.md', 'audit_record': cycle/'audit.json',
            'audit_call': cycle/'audit_call.json', 'formalizer_call': cycle/'formalizer_call.json',
            'certificate': cycle/'tools/certificate.json'}
        self.hashes = {k: base.sha256_file(p) for k, p in self.paths.items()}
        text = self.paths['draft'].read_text().strip()
        compiled = compile_bounded(text, self.paths['theorem'].read_text().strip(), config)
        if compiled['operation'] != matcher['operation'] or compiled != read(self.paths['compilation']):
            raise ValueError('discrete compilation replay mismatch')
        decision = audit.formal.parse_post_singular_audit(self.paths['semantic_audit'].read_text().strip())
        record = read(self.paths['audit_record'])
        if (not decision['accepted'] or record['decision'] != decision
                or record['formalization_sha256'] != base.sha256_text(text)
                or record['compiled_sha256'] != engine.digest(compiled)
                or record['exact_result_supplied'] is not False):
            raise ValueError('unbound discrete semantic audit')
        for key, stage, content in [('audit_call', 'discrete_semantic_audit', self.paths['semantic_audit'].read_text().strip()),
                                    ('formalizer_call', 'discrete_formalization', text)]:
            certificate.validate_markdown_budget_forcing(read(self.paths[key]), expected_stage=stage,
                expected_model=config.gemma().model, canonical_markdown=content)
        result = replay(text, read(self.paths['certificate']), config)
        if result['compilation_sha256'] != engine.digest(compiled):
            raise ValueError('discrete certificate refers to another formalization')
        statement, appendix = engine.render(compiled, result)
        # Proof storage and final revision use canonical stripped Markdown.
        statement, appendix = statement.strip(), appendix.strip()
        self.bundle = EvidenceBundle(self.provider_id, 'VERIFIED_SUPPORT', statement,
            {**result, 'source_artifact_sha256': self.hashes, 'target_label_latex': 'D',
             'appendix_sha256': base.sha256_text(appendix), 'certificate_derivation_supplied': True,
             'model_must_prove_inserted_lemma': False, 'presentation_kind': 'statement_with_verified_appendix',
             'discrete_computation_replayed': True, 'source_binding': 'independent_model_audit'},
            {'operation': matcher['operation'], 'claim': matcher['claim'], 'decision': 'PROVED',
             'scope': compiled['report']['scope']}, self.paths,
            appendix_markdown=appendix, appendix_in_rewriter_prompt=False)

    def materialize(self):
        if {k: base.sha256_file(p) for k, p in self.paths.items()} != self.hashes:
            raise ValueError('discrete evidence source drift')
        replay(self.paths['draft'].read_text().strip(), read(self.paths['certificate']), self.config)
        return self.bundle


def run_track(output, root, *, config, seed, matcher, select, should_stop, caller=None, feedback=None):
    root.mkdir(parents=True, exist_ok=False)
    acq = output/'01_acquisition'
    paths = {'theorem': acq/'input/original_theorem.md', 'proof': acq/'input/resolver1_proof.md',
        'detection': acq/'01_detection/detection.md', 'matcher': acq/'02_matcher/matcher.md'}
    inputs = {k: p.read_text().strip() for k, p in paths.items()}
    hashes = {k: base.sha256_file(p) for k, p in paths.items()}
    contract = '\n\n'.join('# '+k+'\n\n'+v for k, v in inputs.items())+'\n\n# Discrete Program Contract\n\n'+engine.contract(matcher['operation'])
    contract += '\n\n# Bound Immutable Claim\n\n'+matcher['claim']
    base.write_text(root/'formalizer_system.md', FORMALIZER_SYSTEM)
    base.write_text(root/'formalizer_user.md', contract)
    rewrite.write_record(root/'manifest.json', {'route': matcher['operation'], 'input_sha256': hashes,
        'config': {'cycles': config.cycles, 'tool_timeout_seconds': config.algebra_timeout},
        'prior_drafts_supplied': False, 'gold_inputs': False,
        'peer_feedback_to_formalizer_retries': feedback is not None, 'auditor_peer_feedback': False})
    status = {'state': 'running', 'route': matcher['operation'], 'cycles': [], 'exact_verified': False}
    calls = caller or rewrite.BudgetedCalls(root/'model_budget.json', max_stages=2*config.cycles)
    prompt, text = contract, ''
    try:
        for index in range(1, config.cycles+1):
            if should_stop():
                break
            if {k: base.sha256_file(p) for k, p in paths.items()} != hashes:
                raise ValueError('discrete workflow source changed')
            cycle = root/'cycles'/f'cycle_{index:02d}'
            row = {'cycle': index, 'stage': 'formalization'}
            status['cycles'].append(row)
            rewrite.write_record(root/'status.json', status)
            cycle_seed = base.stable_seed(seed, f'discrete-cycle:{index}')
            current = feedback.augment(prompt, index, cycle) if feedback else prompt
            text, inspection, call = calls(role=replace(config.gemma(), temperature=config.formalizer_temperature),
                system_prompt=FORMALIZER_SYSTEM, user_prompt=current, destination=cycle/'formalizer',
                stage='discrete_formalization', master_seed=cycle_seed, parser=lambda text: inspect(text, inputs['theorem'], config))
            certificate.validate_markdown_budget_forcing(call, expected_stage='discrete_formalization', expected_model=config.gemma().model, canonical_markdown=text)
            base.write_text(cycle/'formalization.md', text)
            rewrite.write_record(cycle/'formalizer_call.json', call)
            rewrite.write_record(cycle/'parser.json', inspection)
            if feedback:
                feedback.publish(index, 'parser_accepted' if inspection['parser_valid'] else 'parser_rejected',
                    'Parsed; source semantics unaudited.' if inspection['parser_valid'] else inspection['parser_feedback'], text)
            if not inspection['parser_valid']:
                row.update(stage='parser_rejected', reason=inspection['parser_feedback'])
                prompt = contract+'\n\n# Current draft\n\n'+text+'\n\n# Deterministic feedback\n\n'+inspection['parser_feedback']
                continue
            compiled = inspection['proposal']
            if compiled['call_requested'] and compiled['operation'] != matcher['operation']:
                raise ValueError('formalization changed the matched operation')
            if not compiled['call_requested']:
                row.update(stage='model_declined', reason=compiled['reason'])
                break
            rewrite.write_record(cycle/'compilation.json', compiled)
            row['stage'] = 'semantic_audit'
            rewrite.write_record(root/'status.json', status)
            oldnames = {'theorem.md': inputs['theorem'], 'source_proof.md': inputs['proof'], 'detection.md': inputs['detection'], 'matcher.md': inputs['matcher']}
            review, decision, audit_call = calls(role=replace(config.gemma(), temperature=.1),
                system_prompt=audit.AUDIT_SYSTEM+'\n\n'+AUDIT_EXTRA,
                user_prompt=audit.audit_prompt(oldnames, text)+'\n\n'+engine.contract(matcher['operation'])+'\n\n'+audit_view(compiled),
                destination=cycle/'auditor', stage='discrete_semantic_audit', master_seed=cycle_seed, parser=audit.formal.parse_post_singular_audit)
            certificate.validate_markdown_budget_forcing(audit_call, expected_stage='discrete_semantic_audit', expected_model=config.gemma().model, canonical_markdown=review)
            base.write_text(cycle/'audit.md', review)
            rewrite.write_record(cycle/'audit_call.json', audit_call)
            rewrite.write_record(cycle/'audit.json', {'decision': decision, 'formalization_sha256': base.sha256_text(text),
                'compiled_sha256': engine.digest(compiled), 'exact_result_supplied': False})
            if feedback:
                feedback.publish(index, 'semantic_accepted' if decision['accepted'] else 'semantic_rejected', review, text, shared_feedback.audit_summary(decision))
            if not decision['accepted']:
                row['stage'] = 'semantic_rejected'
                prompt = contract+'\n\n# Current draft\n\n'+text+'\n\n# Independent audit\n\n'+review
                continue
            row['stage'] = 'discrete_certificate'
            rewrite.write_record(root/'status.json', status)
            try:
                result = execute(text, config)
            except (ValueError, TimeoutError) as error:
                row.update(stage='tool_inconclusive', reason=str(error))
                rewrite.write_record(cycle/'tools/result.json', {'exact_verified': False, 'reason': str(error)})
                if feedback:
                    feedback.publish(index, 'tool_inconclusive', str(error), text)
                prompt = contract+'\n\n# Current draft\n\n'+text+'\n\n# Exact-tool feedback\n\n'+str(error)
                continue
            rewrite.write_record(cycle/'tools/certificate.json', result)
            replay(text, result, config)
            rewrite.write_record(cycle/'tools/independent_replay.json', {'verified': True, 'certificate_sha256': engine.digest(result)})
            if {k: base.sha256_file(p) for k, p in paths.items()} != hashes:
                raise ValueError('discrete source changed before evidence admission')
            provider = DiscreteProvider(inputs=paths, cycle=cycle, matcher=matcher, config=config)
            task = TaskInputs(read(output/'input/problem.json')['problem_id'], inputs['theorem'], inputs['proof'],
                {DETECTION_DOCUMENT: inputs['detection'], MATCHER_DOCUMENT: inputs['matcher']})
            def synthesize():
                return appendix_synthesis.run(task=task, provider=provider, formalization=text+'\n\n'+audit_view(compiled),
                    bindings=compiled['bindings'], target_label='D', output=cycle/'synthesis',
                    gemma=config.proof_writer(), qwen=config.qwen(), seed=cycle_seed)
            status['exact_verified'] = True
            row.update(stage='certificate_verified', exact_verified=True, certified_operation=result['operation'])
            if feedback:
                feedback.publish(index, 'tool_verified', 'Exact discrete certificate verified and replayed.', text)
            row['synthesis'] = select(cycle/'tools', synthesize)
            break
        status['state'] = 'completed'
    except Exception as error:
        status.update(state='failed_closed', error=f'{type(error).__name__}: {error}')
        if feedback and status['cycles']:
            feedback.publish(status['cycles'][-1]['cycle'], 'worker_error', status['error'], text)
    rewrite.write_record(root/'status.json', status)
    rewrite.write_record(root/'result.json', status)
    return status
