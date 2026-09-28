"""Replay the original selected geometry, root or discrete certificate and retry synthesis."""
import argparse
from pathlib import Path

from . import HARNESS_REVISION, proof_harness as harness, discrete_workflow
from .synthesis_core import tool_purpose

read = discrete_workflow.read
write = harness.rewrite.write_record
sha = harness.base.sha256_file
POLICY = 'selected-typed-certificate-synthesis-resume-v1'


def prepare(source, problem_file, proof_file):
    source = source.resolve()
    native = read(source/'manifest.json')
    if native.get('schema') != harness.SCHEMA or native.get('gold_inputs') is not False:
        raise ValueError('unsupported source manifest')
    if read(source.parent/'completion.json').get('worker_exited') is not True:
        raise ValueError('source worker must have exited')
    for name, digest in native['input_artifacts'].items():
        if not (source/name).resolve().is_relative_to(source) or sha(source/name) != digest:
            raise ValueError('source input drift')
    problem = harness.acquisition.v0220.load_problem(problem_file, explicit_problem_id=None)
    saved_problem = read(source/'input/problem.json')
    if (problem.problem_id != saved_problem['problem_id'] or problem.statement != saved_problem['statement']
            or proof_file.read_text().strip() != (source/'input/source_proof.md').read_text().strip()
            or native.get('associated_documents')):
        raise ValueError('selected task differs from source inputs')
    selected = read(source/'selection.json')
    request = Path(selected['request_path']).resolve()
    if not request.is_relative_to(source/'02_formalizations') or request.name != 'tools':
        raise ValueError('selected certificate must belong to source run')
    cycle, lane = request.parent, request.parent.parent.parent
    lane_result = read(lane/'result.json')
    sample_index = int(lane.name.removeprefix('sample_'))
    cycle_index = int(cycle.name.removeprefix('cycle_'))
    row = next(r for r in lane_result['cycles'] if r['cycle'] == cycle_index)
    if lane_result['state'] not in ('completed', 'failed_closed') or not row.get('exact_verified'):
        raise ValueError('originally selected certificate was not verified')
    config = harness.Config.from_saved(native['config'])
    config.validate()
    acq = source/'01_acquisition'
    paths = {'theorem': acq/'input/original_theorem.md', 'proof': acq/'input/resolver1_proof.md',
             'detection': acq/'01_detection/detection.md', 'matcher': acq/'02_matcher/matcher.md'}
    if {k: sha(p) for k,p in paths.items()} != read(lane/'manifest.json')['input_sha256']:
        raise ValueError('selected formalizer source drift')
    if (paths['theorem'].read_text().strip() != problem.statement
            or paths['proof'].read_text().strip() != proof_file.read_text().strip()):
        raise ValueError('acquisition source differs from selected task')
    detection = harness.acquisition.protocol.parse_detection(paths['detection'].read_text().strip())
    matcher = harness.parse_matcher(paths['matcher'].read_text().strip(), detection['desired_exact_fact'],
        harness.matcher_operations(config.excluded_operations))
    if not detection['call_requested'] or not matcher['call_requested']:
        raise ValueError('selected request did not call a tool')
    operation = matcher['operation']
    kwargs = dict(inputs=paths, cycle=cycle, matcher=matcher, config=config)
    if operation in harness.GEOMETRY_OPERATIONS:
        from . import geometry_workflow as workflow
        certificate_root = Path(row['certificate_root']).resolve()
        if not certificate_root.is_relative_to(request):
            raise ValueError('certificate is outside the selected request')
        provider = workflow.GeometryProvider(**kwargs, certificate_root=certificate_root)
        route, target_label = 'geometry', provider.bundle.verification['target_label_latex']
    elif operation in harness.ROOT_OPERATIONS:
        from . import root_workflow as workflow
        provider = workflow.RootProvider(**kwargs)
        route, target_label = 'root', 'R'
    elif operation in harness.DISCRETE_OPERATIONS:
        workflow = discrete_workflow
        if row['certified_operation'] != operation:
            raise ValueError('selected request changed the certified operation')
        provider = workflow.DiscreteProvider(**kwargs)
        route, target_label = 'discrete', 'D'
    else:
        raise ValueError('selected request has no supported typed certificate provider')
    task = workflow.TaskInputs(problem.problem_id, problem.statement, proof_file.read_text().strip(),
        {tool_purpose.DETECTION_DOCUMENT: paths['detection'].read_text().strip(),
         tool_purpose.MATCHER_DOCUMENT: paths['matcher'].read_text().strip()})
    # Run the actual purpose/quote binding before any new model calls.
    tool_purpose.explicit_update_source(task, provider.materialize())
    compiled = read(cycle/'compilation.json')
    seed = harness.base.stable_seed(native['master_seed'], f'guarded-formalization-sample:{sample_index}')
    seed = harness.base.stable_seed(seed, f'{route}-cycle:{cycle_index}')
    bound = {str(p): sha(p) for p in (source/'manifest.json', source/'selection.json',
        source.parent/'completion.json', lane/'manifest.json', lane/'result.json')}
    record = {'schema': POLICY, 'source_run': str(source), 'source_harness_revision': native['harness_revision'],
        'selected_sample': sample_index, 'selected_cycle': cycle_index, 'operation': matcher['operation'],
        'route': route, 'target_label': target_label,
        'source_selection_reused': True, 'certificate_replayed': True,
        'source_record_sha256': bound, 'source_artifact_sha256': provider.hashes,
        'new_detection_calls': 0, 'new_matcher_calls': 0, 'new_formalization_calls': 0,
        'new_semantic_audit_calls': 0, 'new_certificate_searches': 0,
        'prior_external_scores_supplied': False, 'synthesis_master_seed': seed,
        'max_logical_model_stages': 8, 'mandatory_budget_forcing': True}
    return native, config, provider, task, compiled, record, workflow


def run(*, source, problem_file, proof_file, output, execute_models=False):
    native, config, provider, task, compiled, record, workflow = prepare(source, problem_file, proof_file)
    output = output.resolve()
    if output.is_relative_to(source.resolve()):
        raise ValueError('resume output must be separate from source run')
    manifest, _ = harness.prepare(problem_file, proof_file, output, problem_id=task.problem_id,
        config=config, seed=native['master_seed'])
    manifest.update(resume=record, max_logical_model_stages=8, preloaded_certificate=True,
        certificate_origin='same_source_model_formalization_and_audit')
    write(output/'manifest.json', manifest)
    write(output/'resume.json', record)
    bundle = provider.materialize()
    harness.base.write_text(output/'export/lemma.md', bundle.markdown)
    harness.base.write_text(output/'export/appendix.md', bundle.appendix_markdown)
    write(output/'export/verification.json', bundle.verification)
    status = {'state': 'prepared', 'harness_revision': HARNESS_REVISION, 'stage': 'proof_synthesis',
        'resume': record, 'proof_audit_passed': False,
        'selected': {'request_path': str(provider.paths['certificate'].parent), 'state': 'prepared'},
        'samples': [{'sample': record['selected_sample'], 'exact_verified': True, 'reused': True}]}
    write(output/'status.json', status)
    if not execute_models:
        return status
    def validate():
        provider.materialize()
        for name, digest in record['source_record_sha256'].items():
            if sha(Path(name)) != digest:
                raise ValueError('source resume record drift')
        for name, digest in manifest['input_artifacts'].items():
            if sha(output/name) != digest:
                raise ValueError('resumed task input drift')
    calls = harness.rewrite.BudgetedCalls(output/'model_budget.json', max_stages=8)
    def checked_call(**kwargs):
        validate()
        return calls(**kwargs)
    def stage_changed(stage):
        status.update(state='running', stage=stage)
        write(output/'status.json', status)
    try:
        validate()
        status['selected']['state'] = 'running'
        packaged = workflow.appendix_synthesis.run(task=task, provider=provider,
            formalization=provider.paths['draft'].read_text().strip()+'\n\n'+workflow.audit_view(compiled),
            bindings=compiled['bindings'], target_label=record['target_label'], output=output/'synthesis',
            gemma=config.proof_writer(), qwen=config.qwen(), seed=record['synthesis_master_seed'],
            model_call=checked_call, on_stage=stage_changed)
        validate()
        status['selected'].update(state=packaged['state'], result=packaged)
        status.update(state='completed', stage='completed')
    except Exception as error:
        status['selected'].update(state='failed_closed', result={'state': 'failed_closed'})
        status.update(state='failed_closed', error=f'{type(error).__name__}: {error}')
    return harness.publish(output, status)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-run', 'problem-file', 'proof-file', 'output-dir'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--execute-models', action='store_true')
    args = parser.parse_args()
    result = run(source=args.source_run, problem_file=args.problem_file, proof_file=args.proof_file,
        output=args.output_dir, execute_models=args.execute_models)
    print(result.get('outcome', result['state']))
    raise SystemExit(int(result['state'] == 'failed_closed'))


if __name__ == '__main__':
    main()
