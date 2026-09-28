"""Source-audited root classification with replayed proof-synthesis evidence."""
from dataclasses import replace
import json
from pathlib import Path

from . import root_classification as engine
from . import geometry_workflow as common
from . import rewrite, certificate, division_audit_repair as audit, appendix_synthesis, shared_feedback
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import EvidenceBundle, TaskInputs
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT

base = rewrite.pipeline.base
read = common.read
FORMALIZER_SYSTEM = '''You are a mathematical formalizer for exact real-root
classification. Encode the matcher's Immutable Claim with the supplied generic
root-program contract. The original proof and detected claims are untrusted.
Derive the function, variable and interval from their actual source definitions.
Do not assert the claimed number of roots or simplify away original domains.
For critical points, supply the source function in stationary_points mode: the
tool will differentiate and classify every root by exact derivative signs.
The tool can disprove a uniqueness assertion by returning additional points;
such a result is useful evidence, not a reason to omit those roots. Explain all
source correspondences and any domain restrictions in Semantic Bindings. No
reference proof or operator mathematical hint is supplied. Return Markdown only.'''
AUDIT_EXTRA = '''This is a root-classification request. Check the actual source
function or equation, interval endpoints and open/closed conventions, all original
domains, and correspondence with the matcher's Immutable Claim. Reject invented
parameters, omitted portions of the requested interval, branch changes, and a
different task. The compiler computes the derivative in stationary_points mode;
roots mode classifies the supplied expression only. The computation has not run
yet; never assume a root count or uniqueness assertion. A later complete root
list may contradict the submitted proof. Its use to repair the full proof still
requires the separate whole-proof audit. Do not author a replacement draft.'''


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
    return '# Deterministic Root Compilation\n\n```json\n'+json.dumps(compiled['report'], separators=(',', ':'))+'\n```'


def execute(text, config):
    return common.bounded(engine.compute, (text,), timeout=config.algebra_timeout, memory=config.memory_mb)


def replay(text, saved, config):
    actual = execute(text, config)
    if actual != saved or not actual.get('verified'):
        raise ValueError('root-classification replay differs from saved evidence')
    return actual


class RootProvider:
    provider_id = 'checked_real_root_classification_v1'

    def __init__(self, *, inputs, cycle, matcher, config):
        self.config = config
        self.paths = {**inputs, 'draft': cycle/'formalization.md', 'compilation': cycle/'compilation.json',
            'semantic_audit': cycle/'audit.md', 'audit_record': cycle/'audit.json',
            'audit_call': cycle/'audit_call.json', 'formalizer_call': cycle/'formalizer_call.json',
            'certificate': cycle/'tools/certificate.json'}
        self.hashes = {k: base.sha256_file(p) for k, p in self.paths.items()}
        text = self.paths['draft'].read_text().strip()
        compiled = compile_bounded(text, self.paths['theorem'].read_text().strip(), config)
        if compiled != read(self.paths['compilation']):
            raise ValueError('root compilation replay mismatch')
        decision = audit.formal.parse_post_singular_audit(self.paths['semantic_audit'].read_text().strip())
        record = read(self.paths['audit_record'])
        if (not decision['accepted'] or record['decision'] != decision
                or record['formalization_sha256'] != base.sha256_text(text)
                or record['compiled_sha256'] != engine.digest(compiled)
                or record['exact_result_supplied'] is not False):
            raise ValueError('unbound root semantic audit')
        for key, stage, content in [('audit_call', 'root_semantic_audit', self.paths['semantic_audit'].read_text().strip()),
                                    ('formalizer_call', 'root_formalization', text)]:
            certificate.validate_markdown_budget_forcing(read(self.paths[key]), expected_stage=stage,
                expected_model=config.gemma().model, canonical_markdown=content)
        result = replay(text, read(self.paths['certificate']), config)
        if result['compilation_sha256'] != engine.digest(compiled):
            raise ValueError('root certificate refers to another formalization')
        statement, appendix = engine.render(compiled, result)
        self.bundle = EvidenceBundle(self.provider_id, 'VERIFIED_SUPPORT', statement,
            {**result, 'source_artifact_sha256': self.hashes, 'target_label_latex': 'R',
             'appendix_sha256': base.sha256_text(appendix), 'certificate_derivation_supplied': True,
             'model_must_prove_inserted_lemma': False, 'presentation_kind': 'statement_with_verified_appendix',
             'root_computation_replayed': True, 'source_binding': 'independent_model_audit'},
            {'operation': matcher['operation'], 'claim': matcher['claim'], 'decision': 'PROVED',
             'scope': 'complete_classification_of_audited_expression_and_interval'}, self.paths,
            appendix_markdown=appendix, appendix_in_rewriter_prompt=False)

    def materialize(self):
        if {k: base.sha256_file(p) for k, p in self.paths.items()} != self.hashes:
            raise ValueError('root evidence source drift')
        replay(self.paths['draft'].read_text().strip(), read(self.paths['certificate']), self.config)
        return self.bundle


def run_track(output, root, *, config, seed, matcher, select, should_stop, caller=None, feedback=None):
    root.mkdir(parents=True, exist_ok=False)
    acq = output/'01_acquisition'
    paths = {'theorem': acq/'input/original_theorem.md', 'proof': acq/'input/resolver1_proof.md',
        'detection': acq/'01_detection/detection.md', 'matcher': acq/'02_matcher/matcher.md'}
    inputs = {k: p.read_text().strip() for k, p in paths.items()}
    hashes = {k: base.sha256_file(p) for k, p in paths.items()}
    contract = '\n\n'.join('# '+k+'\n\n'+v for k, v in inputs.items())+'\n\n# Root Program Contract\n\n'+engine.CONTRACT
    base.write_text(root/'formalizer_system.md', FORMALIZER_SYSTEM)
    base.write_text(root/'formalizer_user.md', contract)
    rewrite.write_record(root/'manifest.json', {'route': engine.OPERATION, 'input_sha256': hashes,
        'config': {'cycles': config.cycles, 'tool_timeout_seconds': config.algebra_timeout},
        'prior_drafts_supplied': False, 'gold_inputs': False,
        'peer_feedback_to_formalizer_retries': feedback is not None, 'auditor_peer_feedback': False})
    status = {'state': 'running', 'route': engine.OPERATION, 'cycles': [], 'exact_verified': False}
    calls = caller or rewrite.BudgetedCalls(root/'model_budget.json', max_stages=2*config.cycles)
    prompt, text = contract, ''
    try:
        for index in range(1, config.cycles+1):
            if should_stop():
                break
            if {k: base.sha256_file(p) for k, p in paths.items()} != hashes:
                raise ValueError('root workflow source changed')
            cycle = root/'cycles'/f'cycle_{index:02d}'
            row = {'cycle': index, 'stage': 'formalization'}
            status['cycles'].append(row)
            rewrite.write_record(root/'status.json', status)
            cycle_seed = base.stable_seed(seed, f'root-cycle:{index}')
            current = feedback.augment(prompt, index, cycle) if feedback else prompt
            text, inspection, call = calls(role=replace(config.gemma(), temperature=config.formalizer_temperature),
                system_prompt=FORMALIZER_SYSTEM, user_prompt=current, destination=cycle/'formalizer',
                stage='root_formalization', master_seed=cycle_seed, parser=lambda text: inspect(text, inputs['theorem'], config))
            certificate.validate_markdown_budget_forcing(call, expected_stage='root_formalization', expected_model=config.gemma().model, canonical_markdown=text)
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
            if not compiled['call_requested']:
                row.update(stage='model_declined', reason=compiled['reason'])
                break
            rewrite.write_record(cycle/'compilation.json', compiled)
            row['stage'] = 'semantic_audit'
            rewrite.write_record(root/'status.json', status)
            oldnames = {'theorem.md': inputs['theorem'], 'source_proof.md': inputs['proof'], 'detection.md': inputs['detection'], 'matcher.md': inputs['matcher']}
            review, decision, audit_call = calls(role=replace(config.gemma(), temperature=.1),
                system_prompt=audit.AUDIT_SYSTEM+'\n\n'+AUDIT_EXTRA,
                user_prompt=audit.audit_prompt(oldnames, text)+'\n\n'+engine.CONTRACT+'\n\n'+audit_view(compiled),
                destination=cycle/'auditor', stage='root_semantic_audit', master_seed=cycle_seed, parser=audit.formal.parse_post_singular_audit)
            certificate.validate_markdown_budget_forcing(audit_call, expected_stage='root_semantic_audit', expected_model=config.gemma().model, canonical_markdown=review)
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
            row['stage'] = 'root_classification'
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
                raise ValueError('root source changed before evidence admission')
            provider = RootProvider(inputs=paths, cycle=cycle, matcher=matcher, config=config)
            task = TaskInputs(read(output/'input/problem.json')['problem_id'], inputs['theorem'], inputs['proof'],
                {DETECTION_DOCUMENT: inputs['detection'], MATCHER_DOCUMENT: inputs['matcher']})
            def synthesize():
                return appendix_synthesis.run(task=task, provider=provider, formalization=text+'\n\n'+audit_view(compiled),
                    bindings=compiled['bindings'], target_label='R', output=cycle/'synthesis',
                    gemma=config.proof_writer(), qwen=config.qwen(), seed=cycle_seed)
            status['exact_verified'] = True
            row.update(stage='certificate_verified', exact_verified=True, root_count=result['root_count'])
            if feedback:
                feedback.publish(index, 'tool_verified', 'Complete exact root classification verified and replayed.', text)
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
