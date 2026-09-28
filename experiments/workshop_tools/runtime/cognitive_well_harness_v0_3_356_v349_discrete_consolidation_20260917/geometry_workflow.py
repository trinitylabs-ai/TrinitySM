"""Audited geometry program -> replayed exact certificate -> existing proof audits."""
from __future__ import annotations

import copy
import json
import multiprocessing as mp
import resource
import time
from dataclasses import replace
from pathlib import Path
import sympy as sp

from . import geometry_program as compiler
from . import rewrite, certificate, division_audit_repair as audit
from . import radical_certificate as radical, appendix_synthesis, rational_division as division
from . import shared_feedback, source_binding, geometry_domain_feedback as domain_feedback
from . import real_branches
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import EvidenceBundle, TaskInputs
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT

base = rewrite.pipeline.base


def read(path):
    return json.loads(Path(path).read_text())
FORMALIZER_SYSTEM = '''You are a mathematical formalizer. Read the original theorem,
submitted proof and model-selected obligation. Author a small faithful geometry
program using the generic contract. Derive all mathematics from the theorem;
the proof and detected gap are untrusted. Never assume the target or invent a
guard. No reference, saved formalization, successful certificate or operator
mathematical hint is supplied. The mathematical task is the matcher's Immutable
Claim. When that claim is a local lemma, formalize that lemma and its necessary
definitions and conditions. Do not replace its target with the conclusion of
the entire theorem. The original theorem supplies trusted context; assertions
in the submitted proof still require justification. Explicitly explain how the
program's target establishes the Immutable Claim, including parameter meanings
and original domains. Hypotheses irrelevant to this local implication may be
retained with an explanation. Retained prose is not an equation, sign fact, or
nonzero proof. After a domain rejection, use the structured feedback to review
which source conditions were encoded and which remain only prose. Any added
premise must follow from the original theorem and undergo independent semantic
audit; a failed guard is not permission to assume it. Subsequent whole-proof
audits determine whether
the certified lemma actually repairs the submitted proof. Return Markdown only,
following the contract.'''
AUDIT_EXTRA = '''Independently inventory ALL source hypotheses, including relations
between constructed points. Check every premise against its source, normalization
without losing branches, geometric angle interpretation and the exact target.
The source-quote check does NOT establish entailment or inventory completeness.
The deterministic compilation below is unaudited mathematical input, not a tool
success. Check its mapping to the theorem, every retained/relaxed hypothesis,
every construction precondition and the orientation of each angle. Missing
equations enlarge the algebraic domain: that may make a certificate harder to
find, but success on an honestly documented weaker domain suffices. An invented
assumption or an incorrect target must be rejected. Do not supply a replacement
formalization. All compiled polynomial and positivity identities are replayed
by deterministic code; natural-language semantics still require your judgment.
Check that the target establishes precisely the matcher's Immutable Claim.
For a local claim, reject substitution of the full theorem's conclusion or an
unrelated intermediate result. Check the local parameters and assumptions
against their stated definitions; do not inherit unsupported proof assertions.
Inventory source hypotheses relative to this selected implication: retaining an
irrelevant condition is permitted with an honest explanation. Certification of
a local lemma does not certify the remaining proof or its downstream use.'''


def _compile_worker(connection, function, arguments, memory):
    try:
        resource.setrlimit(resource.RLIMIT_AS,(memory*1024**2,)*2)
        connection.send({'ok':True,'value':function(*arguments)})
    except domain_feedback.DomainFailure as error:
        connection.send({'ok':False,'error':f'ValueError: {error}',
                         'domain_diagnostics':error.domain_diagnostics})
    except Exception as error:
        connection.send({'ok':False,'error':f'{type(error).__name__}: {error}'})
    finally:
        connection.close()


def bounded(function, arguments, timeout=120, memory=4096):
    ctx=mp.get_context('spawn');parent,child=ctx.Pipe(duplex=False)
    process=ctx.Process(target=_compile_worker,args=(child,function,arguments,memory))
    process.start();child.close()
    try:
        if not parent.poll(timeout):raise TimeoutError('bounded exact computation timeout')
        try:result=parent.recv()
        except EOFError as error:raise ValueError('geometry compiler worker exited without a result') from error
        if not result['ok']:
            if 'domain_diagnostics' in result:
                raise domain_feedback.DomainFailure(result['error'],result['domain_diagnostics'])
            raise ValueError(result['error'])
        return result['value']
    finally:
        parent.close()
        process.join(timeout=1)
        if process.is_alive():process.kill();process.join()


def compile_bounded(text, theorem, timeout=120, memory=4096):
    try:return bounded(compiler.compile_program,(text,theorem),timeout,memory)
    except TimeoutError as error:raise ValueError('geometry compilation timeout') from error


def division_request(system):
    symbols,equations,target,guards=radical.backends.integration._decode_transform_payload(system)
    names=list(map(str,symbols));encode=lambda value:division.encode(value,names)
    generators={};index=1
    for _,value in equations:
        while f'D{index}' in names:index+=1
        generators[f'D{index}']=encode(value);index+=1
    return {'arguments':{'symbols':names,'generators':generators,'target':encode(target)},
            'guard_program':{'provenance_divisions':{},'source_nonzero':{k:encode(v) for k,v in guards.items()}}}


def replay_certificate(system, saved):
    if saved.get('schema')==real_branches.SCHEMA:
        return real_branches.replay(system,saved)
    if saved.get('schema')==division.BACKEND:
        result=division.replay(division_request(system),saved)
        if not result['target_proved']:raise ValueError('division witness did not prove target')
        return {**result,'verified':True,'conditional_target_proved':True}
    return radical.replay(system,saved)


def inspect(text, theorem):
    normalized, normalization = compiler.geometry_normalization.normalize(text)
    provenance = {'normalized_markdown':normalized,'normalization':normalization}
    try:
        result=compile_bounded(text,theorem)
        return {'parser_valid':True,'proposal':result,**provenance}
    except domain_feedback.DomainFailure as error:
        return {'parser_valid':False,'parser_error':str(error),
                'parser_feedback':domain_feedback.render_failure(error,error.domain_diagnostics),
                'domain_diagnostics':error.domain_diagnostics,**provenance}
    except ValueError as error:
        return {'parser_valid':False,'parser_feedback':str(error),**provenance}


def audit_view(compiled):
    import json
    return '# Deterministic Geometry Compilation\n\n```json\n'+json.dumps(compiled['report'],separators=(',',':'))+'\n```'


def certificate_search(compiled, output, *, timeout, memory, should_stop=lambda:False):
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();stages=[]
    if 'real_conditions' in compiled['system'] and not should_stop():
        try:
            real_result=bounded(real_branches.solve,(compiled['system'],),min(20,max(1,timeout/3)),memory)
        except TimeoutError:
            real_result={'verified':False,'verdict':'INCONCLUSIVE','reason':'real branch timeout'}
        except ValueError as error:
            # Unsupported/oversized systems remain eligible for the existing
            # algebraic routes, whose certificates prove a stronger implication.
            real_result={'verified':False,'verdict':'INCONCLUSIVE','reason':str(error)}
        stage={'backend':real_branches.SCHEMA,**{k:v for k,v in real_result.items() if k!='certificate'}}
        stages.append(stage)
        rewrite.write_record(output/'real_branch_search.json',stage)
        if real_result['verified']:
            saved=real_result['certificate']
            checked=replay_certificate(compiled['system'],saved)
            # Ensure every branch and sign deduction can be delivered as an
            # explicit mathematical appendix before selecting this result.
            real_branches.render(compiled['system'],saved)
            destination=output/'real_branches';destination.mkdir()
            rewrite.write_record(destination/'system.json',compiled['system'])
            rewrite.write_record(destination/'certificate.json',saved)
            rewrite.write_record(destination/'independent_replay.json',checked)
            rewrite.write_record(output/'search.json',{'stages':stages,'total_budget_seconds':timeout})
            return {'exact_verified':True,'certificate_root':str(destination),'stages':stages}
    # Cheap guarded linear elimination first. Its explicit substitution and
    # quotient witness is replayed all the way back to the unmodified target.
    if not should_stop():
        try:
            remaining=max(0,timeout-(time.monotonic()-started))
            if remaining<1:raise TimeoutError('certificate budget exhausted')
            reduced=bounded(division.solve,(division_request(compiled['system']),),min(10,remaining),memory)
        except TimeoutError:
            reduced={'verified':False,'verdict':'INCONCLUSIVE','reason':'division timeout'}
        stages.append({'backend':'guarded_division','verified':reduced['verified']})
        if reduced['verified']:
            destination=output/'division';destination.mkdir()
            rewrite.write_record(destination/'system.json',compiled['system'])
            rewrite.write_record(destination/'certificate.json',reduced['certificate'])
            rewrite.write_record(destination/'independent_replay.json',replay_certificate(compiled['system'],reduced['certificate']))
            rewrite.write_record(output/'search.json',{'stages':stages,'total_budget_seconds':timeout})
            return {'exact_verified':True,'certificate_root':str(destination),'stages':stages}
    sets=compiler.guard_subsets(compiled['system'])
    # A short first pass covers the full pool; longer retries are reserved for
    # timed-out subsets, in the same deterministic order and total time budget.
    queue=[(labels,1) for labels in sets]
    for index,(labels,limit) in enumerate(queue):
        if should_stop():break
        remaining=timeout-(time.monotonic()-started)
        if remaining<1:break
        system=copy.deepcopy(compiled['system'])
        system['guards']={key:system['guards'][key] for key in labels}
        destination=output/f'guards_{index:02d}'
        budget=max(1,int(min(limit,remaining)))
        result=radical.export(system,destination,timeout=budget,memory=memory)
        stages.append({'guard_labels':list(labels),'output':str(destination),'result':result})
        if result.get('state')=='certificate_timeout' and limit < 20:
            queue.append((labels,5 if limit==1 else 20))
        rewrite.write_record(output/'search.json',{'stages':stages,'total_budget_seconds':timeout})
        if result.get('verified'):
            saved=read(destination/'certificate.json')
            replay=replay_certificate(system,saved)
            rewrite.write_record(destination/'independent_replay.json',replay)
            return {'exact_verified':True,'certificate_root':str(destination),'stages':stages}
    return {'exact_verified':False,'verdict':'INCONCLUSIVE','stages':stages}


class GeometryProvider:
    provider_id='checked_geometry_program_certificate_v1'

    def __init__(self, *, inputs, cycle, certificate_root, matcher, config):
        paths={**inputs,'draft':cycle/'formalization.md','compilation':cycle/'compilation.json',
               'semantic_audit':cycle/'audit.md','audit_record':cycle/'audit.json',
               'audit_call':cycle/'audit_call.json','formalizer_call':cycle/'formalizer_call.json',
               'system':certificate_root/'system.json','certificate':certificate_root/'certificate.json',
               'normalization':cycle/'normalization.json','normalized_draft':cycle/'formalization.normalized.md'}
        self.hashes={k:base.sha256_file(p) for k,p in paths.items()}
        self.paths=paths
        text=paths['draft'].read_text().strip()
        theorem=paths['theorem'].read_text().strip()
        normalized, normalization = compiler.geometry_normalization.normalize(text)
        if (read(paths['normalization']) != normalization
                or paths['normalized_draft'].read_text().strip() != normalized.strip()):
            raise ValueError('geometry normalization replay mismatch')
        compiled=compile_bounded(text,theorem)
        if compiled != read(paths['compilation']):raise ValueError('geometry compilation replay mismatch')
        record=read(paths['audit_record'])
        decision=audit.formal.parse_post_singular_audit(paths['semantic_audit'].read_text().strip())
        if (not decision['accepted'] or record['decision']!=decision
                or record['formalization_sha256']!=base.sha256_text(text)
                or record['compiled_sha256']!=radical.backends.division.exact_tools.stable_hash(compiled)
                or record['exact_result_supplied'] is not False):raise ValueError('unbound geometry semantic audit')
        certificate.validate_markdown_budget_forcing(read(paths['audit_call']),
            expected_stage='geometry_semantic_audit',expected_model=config.gemma().model,
            canonical_markdown=paths['semantic_audit'].read_text().strip())
        certificate.validate_markdown_budget_forcing(read(paths['formalizer_call']),
            expected_stage='geometry_formalization',expected_model=config.gemma().model,
            canonical_markdown=text)
        system=read(paths['system']);saved=read(paths['certificate'])
        expected=copy.deepcopy(compiled['system'])
        if not set(system['guards'])<=set(expected['guards']):raise ValueError('certificate added a guard')
        expected['guards']={key:expected['guards'][key] for key in system['guards']}
        if system!=expected:raise ValueError('certificate target/source mismatch')
        verified=replay_certificate(system,saved)
        if saved.get('schema')==real_branches.SCHEMA:
            body,rendering=real_branches.render(system,saved)
        elif saved.get('schema')==division.BACKEND:
            body,rendering=verified['markdown'],verified
        else:
            body,rendering=radical.render(system,saved,table_multipliers=True)
        symbols,equations,target,guards=radical.backends.integration._decode_transform_payload(system)
        label=rendering['target_label_latex']
        statement='## Algebraic lemma\n\nFor the real variables '+', '.join(sp.latex(s) for s in symbols)+', assume:\n\n'
        statement+='\n\n'.join('\\['+sp.latex(value)+'=0.\\]' for _,value in equations)
        statement+='\n\n'+'\n\n'.join('\\['+sp.latex(value)+'\\ne0.\\]' for value in guards.values())
        if system.get('real_conditions'):
            for condition in system['real_conditions']:
                value=radical.payload_polynomial(condition['polynomial'],symbols).as_expr()
                operator={'gt':'>','ge':r'\ge','ne':r'\ne'}[condition['relation']]
                statement+='\n\n\\['+sp.latex(value)+operator+'0.\\]'
        statement+='\n\nThen \\('+label+'='+sp.latex(target)+'=0\\).'
        appendix='# Appendix A — Proof of the algebraic lemma\n\n'+body
        self.bundle=EvidenceBundle(self.provider_id,'VERIFIED_SUPPORT',statement,
            {**verified,**rendering,'source_artifact_sha256':self.hashes,'target_label_latex':label,
             'appendix_sha256':base.sha256_text(appendix),'certificate_derivation_supplied':True,
             'model_must_prove_inserted_lemma':False,'presentation_kind':'statement_with_verified_appendix',
             'geometry_compilation_replayed':True,'geometry_source_binding':'independent_model_audit'},
            {'operation':matcher['operation'],'claim':matcher['claim'],'decision':'PROVED',
             'scope':'compiled_original_target_under_proved_guards'},paths,
            appendix_markdown=appendix,appendix_in_rewriter_prompt=False)

    def materialize(self):
        if {k:base.sha256_file(p) for k,p in self.paths.items()}!=self.hashes:raise ValueError('geometry evidence source drift')
        # Exact witness replay is independent of the saved success flag.
        replay_certificate(read(self.paths['system']),read(self.paths['certificate']))
        return self.bundle


def run_track(output, root, *, config, seed, matcher, select, should_stop, caller=None, feedback=None):
    root.mkdir(parents=True,exist_ok=False)
    acq=output/'01_acquisition'
    paths={'theorem':acq/'input/original_theorem.md','proof':acq/'input/resolver1_proof.md',
           'detection':acq/'01_detection/detection.md','matcher':acq/'02_matcher/matcher.md'}
    inputs={name:p.read_text().strip() for name,p in paths.items()}
    hashes={k:base.sha256_file(p) for k,p in paths.items()}
    contract='\n\n'.join('# '+name+'\n\n'+text for name,text in inputs.items())+'\n\n# Program Contract\n\n'+compiler.CONTRACT
    source_spans = source_binding.inventory(inputs['theorem'])
    contract += '\n\n' + source_binding.render(source_spans)
    rewrite.write_record(root/'source_spans.json', source_spans)
    base.write_text(root/'formalizer_system.md',FORMALIZER_SYSTEM);base.write_text(root/'formalizer_user.md',contract)
    status={'state':'running','route':'exact_geometry','cycles':[],'exact_verified':False}
    rewrite.write_record(root/'manifest.json',{'input_sha256':hashes,'config':{'cycles':config.cycles},
        'prior_drafts_supplied':False,'gold_inputs':False,
        'source_binding_policy':source_binding.POLICY,
        'domain_feedback_policy':domain_feedback.POLICY,
        'source_spans_sha256':base.sha256_file(root/'source_spans.json'),
        'peer_feedback_to_formalizer_retries':feedback is not None,'auditor_peer_feedback':False})
    calls=caller or rewrite.BudgetedCalls(root/'model_budget.json',max_stages=2*config.cycles)
    prompt=contract
    text=''
    try:
        for index in range(1,config.cycles+1):
            if should_stop():break
            cycle=root/'cycles'/f'cycle_{index:02d}'
            row={'cycle':index,'stage':'formalization'};status['cycles'].append(row)
            rewrite.write_record(root/'status.json',status)
            cycle_seed=base.stable_seed(seed,f'geometry-cycle:{index}')
            text=''
            current_prompt=feedback.augment(prompt,index,cycle) if feedback else prompt
            text,inspection,call=calls(role=replace(config.gemma(),temperature=config.formalizer_temperature),
                system_prompt=FORMALIZER_SYSTEM,user_prompt=current_prompt,destination=cycle/'formalizer',
                stage='geometry_formalization',master_seed=cycle_seed,
                parser=lambda text:inspect(text,inputs['theorem']))
            certificate.validate_markdown_budget_forcing(call,expected_stage='geometry_formalization',
                expected_model=config.gemma().model,canonical_markdown=text)
            base.write_text(cycle/'formalization.md',text);rewrite.write_record(cycle/'formalizer_call.json',call)
            base.write_text(cycle/'formalization.normalized.md',inspection['normalized_markdown'])
            rewrite.write_record(cycle/'normalization.json',inspection['normalization'])
            rewrite.write_record(cycle/'parser.json',inspection)
            if feedback:
                if inspection['normalization']['applied']:
                    feedback.publish(index,'syntax_normalized',json.dumps(inspection['normalization'],indent=2),text,
                        shared_feedback.normalization_summary(inspection['normalization']))
                feedback.publish(index,'parser_accepted' if inspection['parser_valid'] else 'parser_rejected',
                    'Parser accepted; semantic interpretation remains unaudited.' if inspection['parser_valid'] else inspection['parser_feedback'],text)
            if not inspection['parser_valid']:
                row.update(stage='parser_rejected',reason=inspection['parser_feedback'])
                prompt=contract+'\n\n# Current draft\n\n'+text+'\n\n# Deterministic feedback\n\n'+inspection['parser_feedback']
                continue
            compiled=inspection['proposal']
            if not compiled['call_requested']:
                if feedback:feedback.publish(index,'model_declined',compiled['reason'],text)
                row.update(stage='model_declined',reason=compiled['reason']);break
            rewrite.write_record(cycle/'compilation.json',compiled)
            row['stage']='semantic_audit';rewrite.write_record(root/'status.json',status)
            oldnames={'theorem.md':inputs['theorem'],'source_proof.md':inputs['proof'],'detection.md':inputs['detection'],'matcher.md':inputs['matcher']}
            review,decision,audit_call=calls(role=replace(config.gemma(),temperature=.1),
                system_prompt=audit.AUDIT_SYSTEM+'\n\n'+AUDIT_EXTRA,
                user_prompt=audit.audit_prompt(oldnames,text)+'\n\n'+compiler.CONTRACT+'\n\n'+audit_view(compiled),
                destination=cycle/'auditor',stage='geometry_semantic_audit',master_seed=cycle_seed,
                parser=audit.formal.parse_post_singular_audit)
            certificate.validate_markdown_budget_forcing(audit_call,expected_stage='geometry_semantic_audit',
                expected_model=config.gemma().model,canonical_markdown=review)
            base.write_text(cycle/'audit.md',review);rewrite.write_record(cycle/'audit_call.json',audit_call)
            rewrite.write_record(cycle/'audit.json',{'decision':decision,'formalization_sha256':base.sha256_text(text),
                'compiled_sha256':radical.backends.division.exact_tools.stable_hash(compiled),'exact_result_supplied':False})
            if feedback:
                feedback.publish(index,'semantic_accepted' if decision['accepted'] else 'semantic_rejected',
                    review,text,shared_feedback.audit_summary(decision))
            if not decision['accepted']:
                row.update(stage='semantic_rejected')
                prompt=contract+'\n\n# Current draft\n\n'+text+'\n\n# Independent audit\n\n'+review
                continue
            row['stage']='certificate_search';rewrite.write_record(root/'status.json',status)
            if {k:base.sha256_file(p) for k,p in paths.items()}!=hashes:raise ValueError('geometry source changed')
            result=certificate_search(compiled,cycle/'tools',timeout=config.algebra_timeout,memory=config.memory_mb,should_stop=should_stop)
            if feedback:
                feedback.publish(index,'tool_verified' if result['exact_verified'] else 'tool_inconclusive',
                    shared_feedback.tool_summary(result),text)
            row.update(result,stage='certificate_verified' if result['exact_verified'] else 'inconclusive')
            if result['exact_verified']:
                provider=GeometryProvider(inputs=paths,cycle=cycle,certificate_root=Path(result['certificate_root']),matcher=matcher,config=config)
                task=TaskInputs(read(output/'input/problem.json')['problem_id'],inputs['theorem'],inputs['proof'],
                    {DETECTION_DOCUMENT:inputs['detection'],MATCHER_DOCUMENT:inputs['matcher']})
                def synthesize():
                    return appendix_synthesis.run(task=task,provider=provider,
                        formalization=text+'\n\n'+audit_view(compiled),bindings=compiled['bindings'],
                        target_label=provider.bundle.verification['target_label_latex'],output=cycle/'synthesis',
                        gemma=config.proof_writer(),qwen=config.qwen(),seed=cycle_seed)
                status['exact_verified']=True
                row['synthesis']=select(cycle/'tools',synthesize)
                break
            prompt=contract+'\n\n# Current draft\n\n'+text+'\n\n# Tool feedback\n\nNo certificate was found within the fixed budget. This is inconclusive; reassess the encoding without adding assumptions.'
        status['state']='completed'
    except Exception as error:
        status.update(state='failed_closed',error=f'{type(error).__name__}: {error}')
        if feedback and status['cycles']:
            feedback.publish(status['cycles'][-1]['cycle'],'worker_error',status['error'],text)
    rewrite.write_record(root/'status.json',status);rewrite.write_record(root/'result.json',status)
    return status
