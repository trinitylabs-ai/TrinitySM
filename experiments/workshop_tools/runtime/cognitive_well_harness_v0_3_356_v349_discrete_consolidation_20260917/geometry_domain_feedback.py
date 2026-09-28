"""Read-only, bounded feedback from a rejected compiler's actual fact context.

This module does not prove, repair, or admit mathematical assertions. It has no
model, theorem catalog, filesystem, or proof-search dependency.
"""
import hashlib
import json

POLICY = 'geometry-domain-context-feedback-v1'
MAX_ITEMS = 16
MAX_TEXT = 1200
MAX_DIAGNOSTIC_CHARACTERS = 96000
MAX_FEEDBACK_CHARACTERS = 9000

GUIDANCE = (
    'A bounded domain proof failed; this does not show that the condition is false '
    'or that any particular hypothesis is missing. Retained prose supplies no algebraic facts. '
    'Review the failed construction and the source hypotheses. If a source condition is needed, '
    'encode its faithful polynomial or sign consequence with its source binding and explain '
    'the derivation in Semantic Bindings. Do not copy the failed guard into a premise unless '
    'the original theorem independently justifies it. A matching quotation alone is not a proof. '
    'A premise cannot justify its own original denominator, even after cancellation; mutually '
    'dependent premises cannot justify each other. Equivalent coordinates with source-justified '
    'defining equations may avoid a problematic rational construction, but must preserve all '
    'domains, branches, and the Immutable Claim within the symbol budget. If these requirements '
    'cannot be met, decline the tool. Every repaired draft must compile again and pass the '
    'independent semantic audit before certificate search.'
)


class DomainFailure(ValueError):
    def __init__(self, message, diagnostics):
        super().__init__(message)
        self.domain_diagnostics = diagnostics


def clipped(value, limit=MAX_TEXT):
    text = str(value)
    return text if len(text) <= limit else text[:limit-14] + ' [truncated]'


def expression(value):
    text = str(value)
    return {'expression':clipped(text), 'expression_truncated':len(text)>MAX_TEXT,
            'expression_sha256':hashlib.sha256(text.encode()).hexdigest()}


def sexpr(node):
    return '('+' '.join(sexpr(x) for x in node)+')' if isinstance(node,list) else str(node)


def condition(value, relation, reason, label=None, *, original=None):
    return {'relation':relation, 'value':value, 'reason':reason, 'source_label':label,
            'original_relation':original.relation if original is not None else relation,
            'original_value':original.residual if original is not None else value}


def build(parsed, evaluator, signs, equations, failures, stage):
    """Serialize observations only; never call the sign prover a second time."""
    report={'schema':POLICY,'stage':stage,'read_only':True,'source_semantics_verified':False,
            'search_result':'unproved_within_existing_policy',
            'equations_used_for_domain_proofs':False,'guidance':GUIDANCE,'counts':{},
            'truncated':False}
    def section(name, values, convert):
        report['counts'][name] = len(values)
        report[name]=[convert(v) for v in values[:MAX_ITEMS]]
        if len(values)>MAX_ITEMS:report['truncated']=True
    def failed(row):
        return {'source_label':clipped(row['source_label'] or '(construction/target)'),
                'reason':clipped(row['reason']),'relation':clipped(row['relation']),
                **expression(row['value'])}
    section('failed_conditions',failures,failed)
    section('retained_only_as_prose',parsed['retained'],
            lambda row:{key:clipped(value) for key,value in row.items()})
    section('available_sign_facts',signs.facts,
            lambda row:{'label':clipped(row[2]),'relation':'gt' if row[1] else 'ge',**expression(row[0])})
    section('available_nonzero_facts',signs.nonzeros,
            lambda row:{'label':clipped(row[1]),'relation':'ne',**expression(row[0])})
    section('encoded_equations_not_used_for_domains',equations,
            lambda row:{'label':clipped(row[0]),'relation':'eq',**expression(row[1]),
                        'domain_status':'not_asserted_by_this_diagnostic'})
    section('source_premises',parsed['premises'],
            lambda row:{'label':clipped(row[0]),'predicate':clipped(sexpr(row[1])),
                        'source_excerpt':clipped(row[2]),'entailment':'not_semantically_audited'})
    failed_domains={(row['original_relation'],str(row['original_value'])) for row in failures}
    definitions=[(name,node) for name,node in parsed['definitions']
                 if any((item['_predicate'].relation,str(item['_predicate'].residual)) in failed_domains
                        for item in evaluator.definition_obligations.get(name,[]))]
    section('definitions_sharing_failed_domain',definitions,
            lambda row:{'label':clipped(row[0]),'expression':clipped(sexpr(row[1]))})
    # Expression truncation is always explicit. Enforce a total IPC/JSON bound
    # by removing tail rows, retaining failed conditions and retained prose last.
    if any('[truncated]' in str(value) for key,value in report.items() if key!='guidance'):
        report['truncated']=True
    drop_order=['source_premises','encoded_equations_not_used_for_domains','available_sign_facts',
                'available_nonzero_facts','definitions_sharing_failed_domain','retained_only_as_prose',
                'failed_conditions']
    while len(json.dumps(report,ensure_ascii=True))>MAX_DIAGNOSTIC_CHARACTERS:
        for name in drop_order:
            if report[name]:report[name].pop();break
        else:raise ValueError('domain diagnostic budget cannot hold metadata')
        report['truncated']=True
    return report


def render(report):
    lines=['Domain-check context (read-only; source semantics remain unaudited).',GUIDANCE]
    def add(title, name, formatter, budget):
        rows=report[name];parts=[];used=0
        for row in rows:
            part=formatter(row)
            if used+len(part)+1>budget:break
            parts.append(part);used+=len(part)+1
        lines.append(title+f' ({len(parts)}/{report["counts"][name]} shown):')
        lines.extend(parts or ['(none shown)'])
    operators={'eq':'=','ne':'!=','gt':'>','ge':'>='}
    def equation(row):return row['label']+': '+clipped(row['expression'],360)+' '+operators.get(row['relation'],row['relation'])+' 0'
    add('Failed conditions','failed_conditions',lambda r:r['source_label']+': '+
        clipped(r['expression'],650)+' '+operators.get(r['relation'],r['relation'])+' 0; '+clipped(r['reason'],200),1900)
    add('Retained only as prose; no constraint is supplied','retained_only_as_prose',
        lambda r:r['label']+': '+clipped(r.get('description',r.get('excerpt','')),300)+
        '; stated reason: '+clipped(r.get('reason',''),220),1600)
    add('Definitions sharing the failed domain','definitions_sharing_failed_domain',
        lambda r:r['label']+' = '+clipped(r['expression'],350),700)
    add('Available sign facts','available_sign_facts',equation,1000)
    add('Available nonzero facts','available_nonzero_facts',equation,1000)
    add('Encoded equations: excluded from this checker’s domain proofs; domains not certified here',
        'encoded_equations_not_used_for_domains',equation,1000)
    lines.append('Source premise labels: '+', '.join(r['label'] for r in report['source_premises']))
    if report['truncated']:lines.append('Structured context is incomplete because of diagnostic limits.')
    lines.append('Displayed sections are bounded; inspect the structured domain_diagnostics for additional rows and source excerpts.')
    return clipped('\n'.join(lines),MAX_FEEDBACK_CHARACTERS)


def render_failure(error, report):
    return clipped(clipped(error)+'\n\n'+render(report),MAX_FEEDBACK_CHARACTERS)
