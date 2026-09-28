"""Keep earlier strict results alongside newly graded attempts; no model calls."""
from collections import defaultdict
from pathlib import Path
from scripts.run_v263_v290 import read,write


def report_history(root: Path, current_rows: list[dict]) -> dict:
    previous=read(root/'prior_strict_summary.json')
    by_key={}
    for row in previous['rows']+current_rows:
        # A different run is a different attempt, including identical proof text.
        identity=(row['problem_number'],row['candidate_id'],row.get('source_summary','no_saved_proof'))
        by_key[identity]=row
    rows=sorted(by_key.values(),key=lambda r:(r['problem_number'],r.get('source_summary',''),r['candidate_id']))
    attempts=defaultdict(list)
    best={}
    for row in rows:
        attempts[(row['problem_number'],row.get('source_summary','no_saved_proof'))].append(row)
        grade=row.get('grade')
        if grade:
            number=str(row['problem_number'])
            best[number]=max(best.get(number,0),grade['score'])
    result={'policy_sha256':previous['policy_sha256'],'model':previous['model'],'reasoning_effort':previous['reasoning_effort'],
            'rows':rows,'attempt_count':len(attempts),'scored_proof_rows':sum('grade' in r for r in rows),
            'per_problem_best_across_attempts':best,'sum_per_problem_best_across_attempts':sum(best.values()),
            'problems_with_scores':len(best)}
    write(root/'strict_attempt_history.json',result)
    lines=['# Strict scores by saved attempt','',
           'Previous grades are preserved. Each new proof is graded once; matching proof hashes reuse existing grades.','',
           '| Problem | Attempt source | t10_r01 | t10_r02 | t07_r01 | t07_r02 | Best |',
           '|---|---|---:|---:|---:|---:|---:|']
    for (number,source),group in sorted(attempts.items()):
        keyed={r['candidate_id']:r for r in group}
        values=[keyed.get(c,{}).get('grade',{}).get('score') for c in ('t10_r01','t10_r02','t07_r01','t07_r02')]
        name=Path(source).parent.parent.parent.name if source!='no_saved_proof' else source
        available=[s for s in values if s is not None]
        lines.append(f'| {number} | [{name}]({source}) | '+' | '.join('pending' if s is None else str(s) for s in values)+f" | {max(available) if available else 'pending'} |")
    lines+=['',f'Best across attempts: {sum(best.values())}/{7*len(best)} across {len(best)} problems with scores.','']
    (root/'strict_attempt_history.md').write_text('\n'.join(lines))
    return result
