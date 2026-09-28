#!/usr/bin/env python3
"""Verify the portable score snapshot and recompute its published matrices.

Uses only the Python standard library and files alongside this script.
Makes no inference, grading, network, or original-workspace calls.
"""
from collections import Counter
from fractions import Fraction
from html import escape
from pathlib import Path
import hashlib
import json
import math


ROOT = Path(__file__).resolve().parent
MATRIX_GROUPS = {
    "IMOBENCH": ("IMO-ProofBench", ("Basic", "Advanced", "All IMOBench")),
    "IMO2026": ("IMO 2026", ("IMO 2026",)),
}
CHECKPOINT_PRIORITY = ("R1-C3", "R1-C2", "R1-C1", "lazy_checked", "raw")


def read(relative):
    return json.loads((ROOT / relative).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group_rows(rows, group):
    if group.startswith("imo2026_p"):
        return [r for r in rows if r["problem_id"] == group]
    if group == "All IMOBench":
        return [r for r in rows if r["benchmark"] != "IMO 2026"]
    return [r for r in rows if r["benchmark"] == group]


def compute(rows, group):
    all_rows = group_rows(rows, group)
    included = [r for r in all_rows if r["included"]]
    problems = sorted({r["problem_id"] for r in all_rows})
    result = {"group": group, "problems": len(problems),
              "scored_lanes": len(included), "possible_lanes": len(all_rows),
              "maximum_points": 7 * len(problems)}
    for mode, prefix in [("baseline", "before"), ("with_tools", "including_tools")]:
        scores = [[r[mode]["score"] for r in included if r["problem_id"] == p]
                  for p in problems]
        assert all(scores), f"A problem has no eligible grade: {group}"
        total = sum((Fraction(sum(s), len(s)) for s in scores), Fraction())
        best = sum(max(s) for s in scores)
        result[prefix + "_average_score"] = float(total / len(problems))
        result[prefix + "_best_score"] = best / len(problems)
        result[prefix + "_average_points"] = float(total)
        result[prefix + "_best_points"] = best
        result[prefix + "_average_percent"] = float(100 * total / result["maximum_points"])
        result[prefix + "_best_percent"] = 100 * best / result["maximum_points"]
    return result


def points(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def v2_grading_passes(rows):
    """Validate and expand both complete IMO grading passes."""
    assert rows and all(row['benchmark'] == 'IMO 2026' for row in rows)
    passes = []
    totals = []
    for repeat in range(2):
        selected = []
        for row in rows:
            value = dict(row)
            for mode in ('baseline', 'with_tools'):
                scores = row[mode]['scores']
                assert len(scores) == 2 and all(type(x) is int and 0 <= x <= 7 for x in scores)
                value[mode] = {'score': scores[repeat]}
            selected.append(value)
        passes.append(selected)
        total = compute(selected, 'IMO 2026')
        totals.append(dict(repeat=repeat + 1,
                           average_points=total['before_average_points'],
                           oracle_at_4_points=total['before_best_points'],
                           maximum_points=total['maximum_points']))
    return passes, totals


def select_v2_lower_pass(rows):
    """Select one complete IMO pass by total Average; ties use the first pass."""
    passes, totals = v2_grading_passes(rows)
    index = min(range(2), key=lambda i: (totals[i]['average_points'], i))
    selection = dict(rule='lower_total_average', tie_break='first_pass',
                     selected_repeat=index + 1, pass_totals=totals)
    return passes[index], selection


def compute_v2_lower_pass(rows, group):
    selected, selection = select_v2_lower_pass(rows)
    result = compute(selected, group)
    result['selected_repeat'] = selection['selected_repeat']
    result['grading_scheme'] = f"Strict v2 (pass {selection['selected_repeat']})"
    return result


def v2_pass_caption(selection):
    index = selection['selected_repeat'] - 1
    chosen, other = selection['pass_totals'][index], selection['pass_totals'][1 - index]
    maximum = chosen['maximum_points']
    return (f"Reported: the complete pass with the lower total Average across two separate automated "
            f"v2 grading passes using the same evaluator (**pass {chosen['repeat']}**): "
            f"**{chosen['average_points']:.2f}/{maximum} Average, "
            f"{points(chosen['oracle_at_4_points'])}/{maximum} Oracle@4**. "
            f"Other pass (**pass {other['repeat']}**): **{other['average_points']:.2f}/{maximum} Average, "
            f"{points(other['oracle_at_4_points'])}/{maximum} Oracle@4**.")


def verify_imo_v2(snapshot):
    """Verify both original IMO passes, retaining v1 evidence as historical data."""
    pointer = snapshot['imo2026_reporting']
    assert pointer['aggregation'] == 'complete_pass_with_lower_total_average'
    assert pointer['evidence'] in snapshot['artifacts']
    evidence = read(pointer['evidence'])
    assert evidence['schema'] == 'imo2026-v2-two-pass-report-v2'
    assert evidence['selected_repetitions'] == [1, 2]
    policy = snapshot['grading_schemes']['strict-v2']
    assert evidence['policy_sha256'] == policy['policy_sha256']
    source = {(r['problem_id'], r['candidate']): r for r in snapshot['lanes']
              if r['benchmark'] == 'IMO 2026'}
    records = evidence['records']
    assert len(records) == len(source) == 24
    assert {(r['problem_id'], r['candidate']) for r in records} == set(source)
    distinct = set()
    for row in records:
        assert row['benchmark'] == 'IMO 2026' and row['included'] is True
        old = source[row['problem_id'], row['candidate']]
        mathematical_input = read(old['baseline']['grade'])
        for mode in ('baseline', 'with_tools'):
            item = row[mode]
            assert item['proof_sha256'] == old[mode]['proof_sha256'], 'V2 proof selection mismatch'
            previous = read(old[mode]['grade'])
            assert len(item['grades']) == len(set(item['grades'])) == len(item['scores']) == 2
            for repeat, (name, score) in enumerate(zip(item['grades'], item['scores']), 1):
                assert name in snapshot['artifacts']
                grade = read(name)
                assert grade['schema'] == 'workshop-v2-independent-grade-v1'
                assert grade['repeat'] == repeat, 'V2 grading repetition mismatch'
                assert grade['problem_id'] == row['problem_id']
                assert grade['proof_sha256'] == previous['proof_sha256'], 'V2 proof_sha256 mismatch'
                for identity in ('problem_sha256', 'reference_sha256'):
                    assert grade[identity] == mathematical_input[identity], f'V2 {identity} mismatch'
                assert grade['policy_sha256'] == policy['policy_sha256']
                assert grade['model'] == policy['grader'] == 'gpt-5.6-sol'
                assert grade['reasoning_effort'] == policy['reasoning_effort'] == 'xhigh'
                assert grade['isolation_audit']['tool_calls'] == 0
                assert grade['isolation_audit']['successful_processes_audited'] is True
                assert grade['grade']['score'] == score and type(score) is int and 0 <= score <= 7
                distinct.add(name)
    assert len(distinct) == 54  # Two grades for each of 24 core proofs and three rewrites.
    _, selection = select_v2_lower_pass(records)
    assert selection == pointer['core_pass_selection'] == evidence['core_pass_selection']
    return records


def reported_tool_examples(records, imo_records):
    """Use two-pass v2 minima for IMO trials, retaining B.5 scores elsewhere."""
    lookup = {(r['problem_id'], r['candidate']): r for r in imo_records}
    result = []
    for row in records:
        if row['benchmark'] != 'IMO 2026':
            result.append(row)
            continue
        repeated = lookup[row['problem_id'], row['candidate']]
        value = dict(row)
        for mode, key in [('input', 'baseline'), ('rewrite', 'with_tools')]:
            assert row[mode]['proof_sha256'] == repeated[key]['proof_sha256']
            value[mode] = dict(row[mode], score=min(repeated[key]['scores']))
        result.append(value)
    return result


def verify_imo_ablation(snapshot, core):
    evidence = read(snapshot['imo2026_reporting']['evidence'])
    records = evidence['ablation_records']
    assert len(records) == 72
    core_lookup = {(r['problem_id'], r['candidate']): r for r in core}
    schemes = [('raw_no_bf', 'Raw without budget forcing'),
               ('raw_bf', 'Raw with budget forcing'), ('full_harness', 'BF + full harness')]
    summaries = []
    for cohort, label in schemes:
        selected = [r for r in records if r['cohort'] == cohort]
        assert len(selected) == 24
        assert {(r['problem_id'], r['candidate']) for r in selected} == set(core_lookup)
        rows = []
        for row in selected:
            assert row['proof'] in snapshot['artifacts']
            assert sha(ROOT / row['proof']) == row['proof_sha256']
            baseline = core_lookup[row['problem_id'], row['candidate']]['baseline']
            expected = read(baseline['grades'][0])
            assert len(row['grades']) == len(set(row['grades'])) == len(row['scores']) == 2
            for repeat, (name, score) in enumerate(zip(row['grades'], row['scores']), 1):
                assert name in snapshot['artifacts']
                grade = read(name)
                assert grade['repeat'] == repeat and grade['problem_id'] == row['problem_id']
                assert grade['proof_sha256'] == row['proof_sha256']
                for key in ('problem_sha256', 'reference_sha256', 'policy_sha256', 'model', 'reasoning_effort'):
                    assert grade[key] == expected[key], f'IMO ablation identity mismatch: {key}'
                assert grade['grade']['score'] == score
                assert grade['isolation_audit']['tool_calls'] == 0
                assert grade['isolation_audit']['successful_processes_audited'] is True
            if cohort == 'full_harness':
                assert row['proof_sha256'] == baseline['proof_sha256']
                assert row['grades'] == baseline['grades'] and row['scores'] == baseline['scores']
            rows.append(dict(problem_id=row['problem_id'], benchmark='IMO 2026', included=True,
                             baseline={'scores': row['scores']}, with_tools={'scores': row['scores']}))
        passes, totals = v2_grading_passes(rows)
        selection = dict(rule='fixed_pass', selected_repeat=1, pass_totals=totals)
        assert selection == evidence['ablation_pass_selections'][cohort]
        summaries.append(dict(compute(passes[0], 'IMO 2026'), selected_repeat=1,
                              grading_scheme='Strict v2 (pass 1)', label=label))
    return summaries


def imo_grading_variation(evidence):
    """Describe observed differences between the two retained IMO grading passes."""
    metrics, agreements = [], []
    for cohort, label in [('raw_no_bf', 'Raw without budget forcing'),
                          ('raw_bf', 'Raw with budget forcing'),
                          ('full_harness', 'Full harness / benchmark')]:
        records = [r for r in evidence['ablation_records'] if r['cohort'] == cohort]
        rows = [dict(problem_id=r['problem_id'], benchmark='IMO 2026', included=True,
                     baseline={'scores': r['scores']}, with_tools={'scores': r['scores']})
                for r in records]
        _, totals = v2_grading_passes(rows)
        for key, metric in [('average_points', 'Average'), ('oracle_at_4_points', 'Oracle@4')]:
            metrics.append([label, metric, *[f"{points(t[key])}/{t['maximum_points']}" for t in totals]])
        differences = [abs(r['scores'][0] - r['scores'][1]) for r in records]
        agreements.append([label, f"{differences.count(0)}/{len(records)}",
                           f"{sum(differences) / len(records):.3f}", str(max(differences))])
    return (render_table(['Configuration', 'Metric', 'Pass 1', 'Pass 2'], metrics)
            + '\n\n' + render_table(['Configuration', 'Identical grades',
                                     'Mean absolute grade difference', 'Largest grade difference'], agreements))


def display_label(label):
    # Preserve archived labels for exact evidence verification; rename display only.
    return {'Raw without budget forcing': 'Raw without extended reasoning',
            'Raw with budget forcing': 'Raw with extended reasoning',
            'BF + full harness': 'Extended reasoning + full harness'}.get(label, label)


def table(summary, per_problem=False, as_html=False, mode="baseline", label_column=None):
    prefixes = {"baseline": ("before",), "with_tools": ("including_tools",),
                "comparison": ("before", "including_tools")}[mode]
    label_column = label_column or ("Problem" if per_problem else "Set")
    metric_headers = ["Average", "Oracle@4"]
    headers = [label_column, "Grading scheme", *metric_headers]
    rows = []
    for s in summary:
        scheme = s.get('grading_scheme', "Strict Olympiad" if per_problem else "IMOBench B.5")
        label = ("P" + s["group"].removeprefix("imo2026_p")
                 if s["group"].startswith("imo2026_p")
                 else f"{s['group']} ({s['problems']})")
        cells = []
        for metric in ("average", "best"):
            values = []
            for prefix in prefixes:
                score = f"{points(s[f'{prefix}_{metric}_points'])}/{s['maximum_points']}"
                values.append(score if per_problem else
                              f"{s[f'{prefix}_{metric}_percent']:.2f}% ({score})")
            cells.append(" → ".join(values))
        rows.append([display_label(s.get("label", label)), scheme, *cells])
    return render_table(headers, rows, as_html)


def render_table(headers, rows, as_html=False):
    if as_html:
        # Shared HTML widths keep both GitHub tables aligned without custom CSS.
        alignments = ("left", "left", "right", "right")
        widths = (200,) * 4
        lines = ['<table width="800">', "  <thead>", "    <tr>"]
        lines.extend(f'      <th width="{width}" align="{align}">{escape(header)}</th>'
                     for header, align, width in zip(headers, alignments, widths))
        lines.extend(["    </tr>", "  </thead>", "  <tbody>"])
        for row in rows:
            cells = ''.join(f'<td align="{align}">{escape(value)}</td>'
                            for value, align in zip(row, alignments))
            lines.append(f"    <tr>{cells}</tr>")
        lines.extend(["  </tbody>", "</table>"])
    else:
        lines = [f"| {' | '.join(headers)} |", "|---|---|---:|---:|"]
        lines.extend(f"| {' | '.join(row)} |" for row in rows)
    return "\n".join(lines)


def matrices(summary, per_problem, as_html=False):
    groups = {s['group']: s for s in summary}
    assert len(groups) == len(summary), 'Duplicate summary groups'
    assert set(groups) == {g for _, names in MATRIX_GROUPS.values() for g in names}
    assert [s['group'] for s in per_problem] == [f'imo2026_p{i}' for i in range(1, 7)]
    result = {}
    for key, (_, names) in MATRIX_GROUPS.items():
        is_imo = names == ("IMO 2026",)
        selected = (per_problem if is_imo else []) + [groups[g] for g in names]
        result[key] = table(selected, per_problem=is_imo, as_html=as_html,
                            mode="comparison" if key.endswith("_TOOLS") else "baseline")
    return result


def first_scored_checkpoint(candidates):
    """Choose by checkpoint order; a higher score never changes the priority."""
    for checkpoint in CHECKPOINT_PRIORITY:
        candidate = candidates.get(checkpoint)
        if candidate and candidate["scored"]:
            return checkpoint
    return None


def verify_ablation(snapshot):
    """Bind the two saved raw cohorts to the same Basic evaluation as the core."""
    study = read("ablation_snapshot.json")
    assert study["schema"] == "public-release-basic-ablation-v1"
    assert study["full_harness_selection"] == "baseline"
    core = group_rows(snapshot["lanes"], "Basic")
    cohort = {(r["problem_id"], r["candidate"]) for r in core if r["included"]}
    assert len(core) == len(cohort) == 120
    assert {p for p, _ in cohort} == {f"PB-Basic-{i:03}" for i in range(1, 31)}
    identities = {(r["problem_id"], r["candidate"]): read(r["baseline"]["grade"])
                  for r in core}
    identity_keys = ("problem_sha256", "reference_sha256", "guidelines_sha256",
                     "dataset_sha256", "prompt_template_sha256", "policy_mode",
                     "reasoning_effort", "isolation_verified")
    benchmark_root = ROOT.parents[1] / "benchmarks"
    summaries, manifests = [], []
    for source in study["raw_sources"]:
        manifest_path = (ROOT.parents[1] / source["manifest"]).resolve()
        assert manifest_path.is_relative_to(benchmark_root)
        assert sha(manifest_path) == source["sha256"], "Ablation manifest hash mismatch"
        archive = manifest_path.parent
        manifest = json.loads(manifest_path.read_text())
        assert manifest["benchmark"] == "imo-proofbench/basic"
        assert manifest["snapshot_count"] == 120 and not manifest["pending_or_unavailable"]
        inventory = manifest["copied_artifact_inventory"]

        def checked(relative):
            path = (archive / relative).resolve()
            assert path.is_relative_to(archive)
            key = path.relative_to(benchmark_root).as_posix()
            assert sha(path) == inventory[key]["sha256"], f"Ablation artifact hash mismatch: {key}"
            return path

        # Generation records substantiate the configuration labels and caveats.
        for key in inventory:
            path = benchmark_root / key
            if path.is_relative_to(archive / "generation"):
                checked(path.relative_to(archive))
        raw_rows = []
        for row in manifest["rows"]:
            key = row["problem_id"], row["candidate_id"]
            grade = json.loads(checked(row["grade_directory"] + "/result.json").read_text())
            proof = checked(row["proof"]).read_text(encoding="utf-8")
            assert row["proof_hash_mode"] == "stripped_text"
            assert hashlib.sha256(proof.strip().encode()).hexdigest() == row["proof_sha256"]
            assert grade["proof_sha256"] == row["proof_sha256"]
            assert (grade["problem_id"], grade["candidate_id"]) == key
            assert grade["state"] == "completed" and grade["isolation_verified"] is True
            assert grade["model"] == row["grader_model"] == identities[key]["grader"] == "gpt-5.6-sol"
            assert all(grade[k] == identities[key][k] for k in identity_keys), "Ablation grading identity mismatch"
            score = grade["grade"]["score"]
            assert score == row["score"] and score in (0, 1, 6, 7)
            raw_rows.append(dict(problem_id=key[0], candidate=key[1], benchmark="Basic",
                                 included=True, baseline={"score": score}, with_tools={"score": score}))
        assert len(raw_rows) == len(cohort)
        assert {(r["problem_id"], r["candidate"]) for r in raw_rows} == cohort
        summaries.append(dict(compute(raw_rows, "Basic"), label=source["label"]))
        manifests.append(archive)

    no_bf, bf = manifests
    prompts = {name: (no_bf / "generation/harness_snapshot/prompts" / name).read_text()
               for name in ("system.txt", "user_prefix.txt", "user_suffix.txt")}
    seed_differences = []
    for pid in sorted({p for p, _ in cohort}):
        plain = json.loads((no_bf / f"generation/records/{pid}/queue_manifest.json").read_text())
        forced = json.loads((bf / f"generation/records/{pid}/queue_manifest.json").read_text())
        frontend = json.loads((bf / f"generation/records/{pid}/frontend_manifest.json").read_text())
        config = plain["config"]
        assert config["budget_forcing"] is False and config["requests_per_candidate"] == 1
        assert forced["budget_forcing"] is True
        assert config["model"] == frontend["raw_generation"]["model"] == "google/gemma-4-31B-it"
        assert config["mtp_speculative_tokens"] == frontend["raw_generation"]["mtp_speculative_tokens"] == 4
        assert config["max_tokens"] == frontend["raw_generation"]["max_tokens"] == 65536
        statement = next(p["problem"] for p in plain["problems"] if p["problem_id"] == pid).strip()
        user = prompts["user_prefix.txt"] + statement + prompts["user_suffix.txt"]
        identity = frontend["prompt_identity"]
        assert hashlib.sha256(prompts["system.txt"].encode()).hexdigest() == identity["system_prompt_sha256"]
        assert hashlib.sha256(user.encode()).hexdigest() == identity["user_prompt_sha256"]
        if config["raw_seed_offset"] != forced.get("raw_seed_offset", 0):
            seed_differences.append(pid)
    assert seed_differences == study["raw_seed_offset_differences"]
    summaries.append(dict(compute(core, "Basic"), label="BF + full harness"))
    for actual, expected in zip(summaries, study["summary"]):
        assert all(actual[k] == v for k, v in expected.items()), "Ablation summary mismatch"
    assert len(summaries) == len(study["summary"]) == 3
    return summaries


def verify_proofbench_ablation(snapshot):
    """Keep Basic/Advanced ablations on B.5, including the seed-matched reruns."""
    evidence = read('proofbench_ablation_b5.json')
    assert evidence['schema'] == 'proofbench-ablation-b5-v1'
    assert evidence['policy_mode'] == 'imobench-proof-autograder-b5-v1'
    policy = snapshot['grading_schemes'][evidence['policy_mode']]
    core = {(r['problem_id'], r['candidate']): r for r in snapshot['lanes']
            if r['benchmark'] != 'IMO 2026'}
    identities = {r['problem_id']: read(r['baseline']['grade']) for r in core.values() if r['included']}
    records = evidence['records']
    assert len(records) == 718
    assert len({(r['cohort'], r['problem_id'], r['candidate']) for r in records}) == len(records)
    raw = {(r['problem_id'], r['candidate']): r for r in records if r['cohort'] == 'raw_no_bf'}
    new_keys = {key for key, row in raw.items() if row['benchmark'] == 'Advanced'
                or row['problem_id'] in evidence['seed_matched_replacements']}
    assert len(new_keys) == 128
    repo = ROOT.parents[1]
    bindings = evidence['new_grade_bindings']
    assert len(bindings) == len(new_keys)
    assert {(r['problem_id'], r['candidate']) for r in bindings} == new_keys
    for binding in bindings:
        row = raw[binding['problem_id'], binding['candidate']]
        assert binding['proof_sha256'] == row['proof_sha256']
        assert hashlib.sha256((repo / binding['proof']).read_text().strip().encode()).hexdigest() == row['proof_sha256']
        assert sha(repo / binding['grade']) == binding['grade_sha256'] == sha(ROOT / row['grade'])
    generation = read(evidence['new_generation_records'])['records']
    assert len(generation) == len(new_keys)
    assert {(r['problem_id'], r['candidate']) for r in generation} == new_keys
    for entry in generation:
        row = raw[entry['problem_id'], entry['candidate']]
        assert entry['proof_sha256'] == row['proof_sha256']
        assert entry['budget_forcing'] is entry['config']['budget_forcing'] is False
        assert entry['generation_requests'] == entry['config']['requests_per_candidate'] == 1
        assert entry['continuation_requests'] == 0
        if entry['problem_id'] in evidence['seed_matched_replacements']:
            source = repo / entry['bf_seed_source']
            assert sha(source) == entry['bf_seed_source_sha256']
            forced = json.loads(source.read_text())
            spec = next(s for s in forced['candidate_specs'] if s['candidate_id'] == entry['candidate'])
            material = f"v048:p{forced['problem']['problem_number']}:{entry['candidate']}:{spec['seed']}:cold_draft"
            seed = int.from_bytes(hashlib.sha256(material.encode()).digest()[:4], 'big') or 1
            assert entry['request']['seed'] == seed, 'Basic replacement request seed mismatch'
            for role in ('system', 'user'):
                assert entry['prompt_sha256'][role] == forced['prompt_identity'][f'{role}_prompt_sha256']
    summaries = {name: [] for name in ['Basic', 'Advanced', 'All IMOBench']}
    for cohort, label in [('raw_no_bf', 'Raw without budget forcing'),
                          ('raw_bf', 'Raw with budget forcing'), ('full_harness', 'BF + full harness')]:
        selected = [r for r in records if r['cohort'] == cohort]
        eligible = {key for key, row in core.items() if row['included'] or cohort == 'raw_no_bf'}
        assert {(r['problem_id'], r['candidate']) for r in selected} == eligible
        rows = []
        for row in selected:
            previous = core[row['problem_id'], row['candidate']]
            assert row['benchmark'] == previous['benchmark']
            assert row['proof'] in snapshot['artifacts'] and row['grade'] in snapshot['artifacts']
            grade = read(row['grade'])
            assert sha(ROOT / row['proof']) == grade['proof_sha256'] == row['proof_sha256']
            assert grade['problem_id'] == row['problem_id']
            assert grade['grader'] == 'gpt-5.6-sol' and grade['reasoning_effort'] == 'xhigh'
            assert grade['policy_mode'] == evidence['policy_mode'], 'ProofBench ablation requires B.5'
            assert grade['prompt_template_sha256'] == policy['prompt_template_sha256']
            assert grade['isolation_verified'] is True
            for key in ['problem_sha256', 'reference_sha256', 'guidelines_sha256', 'dataset_sha256']:
                assert grade[key] == identities[row['problem_id']][key], f'B.5 ablation identity mismatch: {key}'
            score = grade['grade']['score']
            assert score == row['score'] and score in (0, 1, 6, 7)
            if cohort == 'full_harness':
                assert row['proof_sha256'] == previous['baseline']['proof_sha256']
                assert score == previous['baseline']['score']
            rows.append(dict(problem_id=row['problem_id'], benchmark=row['benchmark'], included=True,
                             baseline={'score': score}, with_tools={'score': score}))
        for key, old in core.items():
            if key not in eligible:
                rows.append(dict(problem_id=old['problem_id'], benchmark=old['benchmark'], included=False))
        for name in summaries:
            summaries[name].append(dict(compute(rows, name), label=label))
    assert summaries == evidence['summary']
    return summaries


def verify_tool_examples(snapshot):
    repo = ROOT.parents[1]
    study = json.loads((repo / "experiments/workshop_tools/score_snapshot.json").read_text())
    assert study["schema"] == "workshop-tools-submitted-proof-comparison-v1"
    for name, expected in study["artifacts"].items():
        path = (repo / name).resolve()
        assert path.is_relative_to(repo)
        assert sha(path) == expected, f"Tool example artifact hash mismatch: {name}"
    assert study["bindings"] in study["artifacts"]
    bindings = json.loads((repo / study["bindings"]).read_text())["records"]
    bound = {(r["problem_id"], r["candidate"]): r for r in bindings}
    selected = {(r["problem_id"], r["candidate"]): r for r in snapshot["lanes"]
                if r.get("with_tools", {}).get("checkpoint") == "tool_rewrite"}
    records = study["records"]
    keys = {(r["problem_id"], r["candidate"]) for r in records}
    assert len(keys) == len(records) == len(bound) == len(bindings) == 7
    assert keys == set(selected) == set(bound)
    for r in records:
        key = r["problem_id"], r["candidate"]
        assert r["operation"] == bound[key]["operation"]
        assert r["benchmark"] == selected[key]["benchmark"]
        assert r["rewrite"]["proof_sha256"] == selected[key]["with_tools"]["proof_sha256"]
        assert r["rewrite"]["score"] == selected[key]["with_tools"]["score"]
        grades = []
        for mode in ("input", "rewrite"):
            item = r[mode]
            assert item["proof"] in study["artifacts"] and item["grade"] in study["artifacts"]
            assert sha(repo / item["proof"]) == item["proof_sha256"] == bound[key][mode + "_proof_sha256"], "Tool input/rewrite binding mismatch"
            grade = json.loads((repo / item["grade"]).read_text())
            assert grade["problem_id"] == r["problem_id"]
            assert grade["proof_sha256"] == item["proof_sha256"]
            assert grade["grade"]["score"] == item["score"]
            assert grade["grader"] == "gpt-5.6-sol" and grade["reasoning_effort"] == "xhigh"
            policy = snapshot["grading_schemes"][grade["policy_mode"]]
            assert item["score"] in policy["allowed_scores"]
            identity = "policy_sha256" if grade["policy_mode"] == "strict" else "prompt_template_sha256"
            assert grade[identity] == policy[identity]
            grades.append(grade)
        identity_keys = ("policy_mode", "policy_sha256") if grades[0]["policy_mode"] == "strict" else (
            "policy_mode", "problem_sha256", "reference_sha256", "guidelines_sha256",
            "dataset_sha256", "prompt_template_sha256", "isolation_verified")
        assert all(grades[0][k] == grades[1][k] for k in identity_keys)
    return records


def tool_matrices(records, as_html=False):
    matrices = {}
    for key, is_imo in (("IMOBENCH_TOOLS", False), ("IMO2026_TOOLS", True)):
        rows = []
        for r in records:
            if (r["benchmark"] == "IMO 2026") != is_imo:
                continue
            label = "P2" if is_imo else r["problem_id"].removeprefix("PB-")
            label += f" ({r['candidate']})"
            before, after = r["input"]["score"], r["rewrite"]["score"]
            rows.append([label, r["operation"], f"{before}/7 → {after}/7", f"{after - before:+d}"])
        matrices[key] = render_table(["Problem / input proof", "Tool operation", "Score before → after", "Gain"], rows, as_html)
    return matrices


def main():
    snapshot = read("score_snapshot.json")
    assert snapshot["schema"] == "public-release-evaluation-snapshot-v5"
    assert snapshot["summary_metric"] == "problem_weighted_percentage_of_maximum"
    assert snapshot["checkpoint_priority"] == list(CHECKPOINT_PRIORITY)
    for name, expected in snapshot["artifacts"].items():
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT), name
        assert sha(path) == expected, f"Artifact hash mismatch: {name}"
    for scheme in snapshot["grading_schemes"].values():
        if "prompt" in scheme:
            assert sha(ROOT / scheme["prompt"]) == scheme["prompt_template_sha256"]
        else:
            data = (ROOT / scheme['policy']).read_bytes()
            if scheme.get('policy_hash_mode') == 'stripped_text':
                data = data.decode().strip().encode()
            assert hashlib.sha256(data).hexdigest() == scheme["policy_sha256"]

    rows = snapshot["lanes"]
    assert len({(r['problem_id'], r['candidate']) for r in rows}) == len(rows) == 264
    assert set(Counter(r['problem_id'] for r in rows).values()) == {4}
    assert {r['candidate'] for r in rows} == {'t10_r01', 't10_r02', 't07_r01', 't07_r02'}
    checked_final_manifests = {}
    for r in rows:
        if not r["included"]:
            assert "baseline" not in r and "with_tools" not in r
            continue
        assert r["baseline"]["checkpoint"] in CHECKPOINT_PRIORITY
        assert r["with_tools"]["checkpoint"] in CHECKPOINT_PRIORITY + ("tool_rewrite",)
        if r.get("c3_generation_state") == "completed":
            assert r["baseline"]["checkpoint"] == "R1-C3", "Completed Refinement 3 requires its final proof selection"
        if "final_refinement_provenance" in r:
            provenance = r["final_refinement_provenance"]
            assert r["baseline"]["proof_sha256"] == provenance["proof_sha256"], "Final proof binding mismatch"
            manifest_path = (ROOT.parents[1] / provenance['manifest']).resolve()
            assert manifest_path.is_relative_to(ROOT.parents[1])
            assert sha(manifest_path) == provenance['manifest_sha256'], 'Final refinement manifest hash mismatch'
            if manifest_path not in checked_final_manifests:
                manifest = json.loads(manifest_path.read_text())
                assert manifest['state'] == 'completed' and manifest['checkpoint'] == 'Refinement 3'
                for name, expected in manifest['artifact_sha256'].items():
                    artifact = (manifest_path.parent / name).resolve()
                    assert artifact.is_relative_to(manifest_path.parent)
                    assert sha(artifact) == expected, 'Final refinement artifact hash mismatch'
                checked_final_manifests[manifest_path] = manifest
            binding = next(b for b in checked_final_manifests[manifest_path]['proofs']
                           if (b['problem_id'], b['candidate']) == (r['problem_id'], r['candidate']))
            assert binding['selection'] == r['baseline'], 'Final refinement selection mismatch'
            assert sha(manifest_path.parent / binding['proof']) == provenance['proof_sha256']
        if "fallback_provenance" in r:
            candidates = r["fallback_provenance"]["checkpoints"]
            selected = r["baseline"]
            assert first_scored_checkpoint(candidates) == selected["checkpoint"]
            assert candidates[selected["checkpoint"]]["proof_sha256"] == selected["proof_sha256"]
        for mode in ("baseline", "with_tools"):
            selection = r[mode]
            assert selection['proof'] in snapshot['artifacts']
            assert selection['grade'] in snapshot['artifacts']
            grade = read(selection['grade'])
            assert grade['problem_id'] == r['problem_id']
            assert grade['grade']['score'] == selection['score']
            assert grade['proof_sha256'] == selection['proof_sha256']
            assert grade['proof'] == selection['proof']
            assert sha(ROOT / selection['proof']) == selection['proof_sha256']
            assert grade['grader'] == 'gpt-5.6-sol' and grade['reasoning_effort'] == 'xhigh'
            policy = snapshot['grading_schemes'][grade['policy_mode']]
            assert r['benchmark'] in policy['benchmarks']
            assert selection['score'] in policy['allowed_scores']
            identity = 'policy_sha256' if grade['policy_mode'] == 'strict' else 'prompt_template_sha256'
            assert grade[identity] == policy[identity]

    historical = [compute(rows, s['group']) for s in snapshot['historical_single_grade_summary']]
    for actual, expected in zip(historical, snapshot['historical_single_grade_summary']):
        for k, value in expected.items():
            assert (math.isclose(actual[k], value, abs_tol=1e-12) if isinstance(value, float)
                    else actual[k] == value), (actual['group'], k)
    assert [compute(rows, f'imo2026_p{i}') for i in range(1, 7)] == snapshot['historical_single_grade_imo2026_per_problem']
    imo_records = verify_imo_v2(snapshot)
    summary = [compute_v2_lower_pass(imo_records, s['group']) if s['group'] == 'IMO 2026'
               else s for s in historical]
    assert summary == snapshot['summary']
    per_problem = [compute_v2_lower_pass(imo_records, f'imo2026_p{i}') for i in range(1, 7)]
    assert per_problem == snapshot['imo2026_per_problem']
    imo_total = next(s for s in summary if s['group'] == 'IMO 2026')
    for mode in ('before', 'including_tools'):
        for metric in ('average', 'best'):
            key = f'{mode}_{metric}_points'
            assert sum(row[key] for row in per_problem) == imo_total[key], f'IMO row totals do not add up: {key}'
    rendered = matrices(summary, per_problem, as_html=True)
    historical_ablation = verify_ablation(snapshot)
    expanded = verify_proofbench_ablation(snapshot) if 'proofbench_ablation_b5.json' in snapshot['artifacts'] else None
    ablation = expanded['Basic'] if expanded else historical_ablation
    rendered["BASIC_ABLATION"] = table(ablation, as_html=True, label_column="Configuration")
    if expanded:
        rendered['ADVANCED_ABLATION'] = table(expanded['Advanced'], as_html=True, label_column='Configuration')
    imo_ablation = verify_imo_ablation(snapshot, imo_records)
    rendered['IMO2026_ABLATION'] = table(imo_ablation, per_problem=True, as_html=True, label_column='Configuration')
    evidence = read(snapshot['imo2026_reporting']['evidence'])
    variation_report = (ROOT.parents[1] / evidence['source_study'] / 'REPORT.md').read_text()
    variation = variation_report.split('<!-- BEGIN IMO2026 GRADING VARIATION -->\n', 1)[1].split(
        '\n<!-- END IMO2026 GRADING VARIATION -->', 1)[0]
    assert variation == imo_grading_variation(evidence), 'IMO grading variation report differs from the two passes'
    tool_examples = reported_tool_examples(verify_tool_examples(snapshot), imo_records)
    rendered.update(tool_matrices(tool_examples, as_html=True))
    # Historical matrices live in the full report; the root README presents
    # current results owned by the selector and ProofBench exporters.
    for path in (ROOT.parent / 'public_release_report.md',):
        report = path.read_text()
        assert v2_pass_caption(snapshot['imo2026_reporting']['core_pass_selection']) in report
        for key, expected in rendered.items():
            published = report.split(f'<!-- BEGIN {key} SCORE MATRIX -->\n', 1)[1].split(f'\n<!-- END {key} SCORE MATRIX -->', 1)[0]
            assert published == expected, f'The {key} matrix in {path.name} differs from the score snapshot'
    selected_count = sum(r['included'] for r in rows)
    assert selected_count == snapshot['coverage']['scored_lanes']
    assert len(rows) - selected_count == snapshot['coverage']['excluded_lanes']
    assert dict(Counter(r['baseline']['checkpoint'] for r in rows if r['included'])) == snapshot['coverage']['selected_checkpoints']
    print(f"Verified {len(rows)} lanes, {selected_count} scored selections, and {len(snapshot['artifacts'])} artifact hashes.")
    print("Verified 240 raw ablation grades, their submitted proofs and generation records.")
    if expanded:
        print("Verified 718 current ProofBench ablation selections and 128 new raw generation records without extended reasoning.")
    print("Verified 54 strict-v2 grades for 24 IMO core proofs and three experimental rewrites; core metrics use one complete lower-Average pass.")
    print("\nIMO-ProofBench Basic ablation (30 problems)\n")
    print(table(ablation, label_column="Configuration"))
    if expanded:
        print('\nIMO-ProofBench ablation — Advanced (30 problems)\n')
        print(table(expanded['Advanced'], label_column='Configuration'))
    print('\nIMO 2026 ablation (six problems; strict v2, pass 1 for every configuration)\n')
    print(table(imo_ablation, per_problem=True, label_column='Configuration'))
    for key, matrix in matrices(summary, per_problem).items():
        print(f'\n{MATRIX_GROUPS[key][0]}\n')
        print(matrix)
        if key == 'IMO2026':
            print('\n' + v2_pass_caption(snapshot['imo2026_reporting']['core_pass_selection']))
    for key, matrix in tool_matrices(tool_examples).items():
        title = "IMO 2026" if key.startswith("IMO2026") else "IMO-ProofBench"
        print(f"\n{title} tool examples (actual input → rewrite)\n")
        print(matrix)


if __name__ == '__main__':
    main()
