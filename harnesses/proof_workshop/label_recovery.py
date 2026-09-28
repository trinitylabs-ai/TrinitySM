"""Narrow, recorded label normalization for otherwise complete engine outputs."""
from contextlib import contextmanager
from contextvars import ContextVar
import fcntl
import functools
import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import ModuleType

POLICY = 'explicit-stage-and-comparison-format-normalization-v2'
TARGETS = {
    'cognitive_well_harness_v0_3_52_fusion_20260823.run': 'write_json',
    'cognitive_well_harness_v0_3_53_fusion_20260823.protocol': 'parse_fusion',
    'cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.lazy_expansion': 'parse_lazy_expansion_output',
}
# Multiple captured policies can be replayed in one collector process. Imported
# parser aliases must dispatch to the current context, not the first snapshot.
_state = sys.modules.setdefault('_workshop_label_dispatch', ModuleType('_workshop_label_dispatch'))
if not hasattr(_state, 'active'):
    _state.active = ContextVar('workshop_label_policy', default=None)
    _state.persistent = None
    _state.finder = None


def configuration():
    return _state.active.get() or _state.persistent


def target_attribute(name):
    if name.endswith('.cross_lane_voter.mechanical_recovery'):
        return 'restore_checks_label'
    return TARGETS.get(name)


@functools.lru_cache(maxsize=1)
def comparison_recovery():
    # Always use the captured file beside this run's adapter, never the current
    # checkout. runtime_policy/sitecustomize verify its hash before activation.
    path = Path(__file__).with_name('comparison_recovery.py')
    spec = importlib.util.spec_from_file_location('captured_comparison_recovery', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def comparison(value, strict_parse):
    return comparison_recovery().restore_checks_label(value, strict_parse)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def receipt(rule, original, normalized, changes):
    return dict(policy=POLICY, rule=rule, original_response_sha256=sha(original),
                normalized_response_sha256=sha(normalized), changed_fields=changes,
                model_calls=0, mathematical_text_changed=False)


def fusion(value, parser):
    parsed = parser(value)
    expected = 'REPAIR_NEEDED requires at least one validated or independently missed defect'
    if parsed.get('valid') or parsed.get('errors') != [expected]:
        return parsed
    fields = parsed['fields']
    if any(fields.get(key, '').strip().upper() in ('', 'NONE', 'N/A')
           for key in ('failed_obligation', 'independent_validation', 'decisive_location')):
        return parsed
    normalized, changes = value, []
    for index in (1, 2, 3):
        key = f'reviewer_{index}_assessment'
        label, _, reason = fields[key].partition(' | ')
        # Require an explicit affirmative statement, not a guess about the math.
        if label != 'NO_DEFECT_REPORTED' or not re.fullmatch(
                r'The reviewer failed to identify (?:the|a|an) [^\r\n]+\.', reason):
            continue
        if re.search(r'\b(?:not|no|possibly|perhaps|might|may|whether|if)\b', reason, re.I):
            continue
        if not re.search(r'\b(?:error|defect|gap|mistake)\b', reason, re.I):
            continue
        pattern = (rf'(?m)^({key}: )(?:NO_DEFECT_REPORTED|NO_UNCLOSED_OBLIGATION_FOUND)'
                   rf'( \| {re.escape(reason)})\r?$')
        matches = list(re.finditer(pattern, normalized))
        if len(matches) != 1:
            return parsed
        match = matches[0]
        start, end = match.end(1), match.start(2)
        changes.append(dict(field=key, old=normalized[start:end], new='REVIEWER_MISSED_DEFECT'))
        normalized = normalized[:start] + 'REVIEWER_MISSED_DEFECT' + normalized[end:]
    if not changes:
        return parsed
    repaired = parser(normalized)
    if not repaired.get('valid'):
        return parsed
    repaired['final'] = value.strip()
    repaired['mechanical_label_recovery'] = receipt('explicit_missed_defect', value, normalized, changes)
    repaired['mechanical_label_recovery']['normalized_final_sha256'] = sha(repaired['normalized_final'])
    return repaired


def lazy(value, parser):
    try:
        return parser(value)
    except ValueError as error:
        if str(error) != 'PRESERVE requires identical normalized original and repaired classifications':
            raise
        original_error = error
    matches = list(re.finditer(r'(?m)^CONCLUSION_ACTION: (PRESERVE)\r?$', value))
    if len(matches) != 1:
        raise original_error
    match = matches[0]
    normalized = value[:match.start(1)] + 'CHANGE' + value[match.end(1):]
    try:
        # Requires distinct classifications, an allowed change basis, and an
        # existing substantive justification. No missing evidence is invented.
        repaired = parser(normalized)
    except ValueError:
        raise original_error
    repaired['raw_sha256'] = sha(value.strip())
    repaired['mechanical_label_recovery'] = receipt('explicit_conclusion_change', value, normalized,
        [dict(field='CONCLUSION_ACTION', old='PRESERVE', new='CHANGE')])
    return repaired


def record_recovery(value, parsed, directory):
    recovery = parsed.get('mechanical_label_recovery')
    if directory is None or recovery is None or not parsed.get('valid'):
        return
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (sha(value) + '.json')
    data = json.dumps(recovery, indent=2) + '\n'
    # Identical responses in concurrent lanes share one immutable receipt.
    with path.open('a+') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        previous = handle.read()
        if not previous:
            handle.write(data)
        elif previous != data:
            raise ValueError('Conflicting label recovery receipt')


def write_fusion_receipt(writer, directory, path, value):
    # Fusion re-parses its normalized final before saving, so restore the receipt
    # only when both the original model hash and normalized final hash match.
    normalization = value.get('final_normalization', {}) if isinstance(value, dict) else {}
    source_hash = normalization.get('model_final_sha256', '')
    if directory is not None and re.fullmatch(r'[0-9a-f]{64}', source_hash):
        receipt_path = directory / (source_hash + '.json')
        if receipt_path.is_file():
            recovery = json.loads(receipt_path.read_text())
            if (recovery.get('rule') == 'explicit_missed_defect'
                    and recovery['normalized_final_sha256'] == sha(value['final'])
                    and value.get('parsed', {}).get('valid')):
                value['parsed']['mechanical_label_recovery'] = recovery
                value['final_normalization']['policy'] = recovery['policy']
    return writer(path, value)


def patch_module(module, engine):
    if not Path(module.__file__).resolve().is_relative_to(engine):
        raise ValueError('Label normalization target is outside the pinned engine')
    name = target_attribute(module.__name__)
    original = getattr(module, name)
    if getattr(original, '_label_recovery_dispatch', False):
        return

    @functools.wraps(original)
    def parse(*args, **kwargs):
        current = configuration()
        if current is None or current[0] != engine or name not in current[1]:
            return original(*args, **kwargs)
        if name == 'restore_checks_label':
            return current[1][name](*args, **kwargs)
        if name == 'write_json':
            return current[1][name](original, current[2], *args, **kwargs)
        value = args[0] if args else next(iter(kwargs.values()))
        parsed = current[1][name](value, original)
        record_recovery(value, parsed, current[2])
        return parsed

    parse._label_recovery_dispatch = True
    setattr(module, name, parse)
    return original, parse


class Loader(importlib.abc.Loader):
    def __init__(self, original, engine):
        self.original, self.engine = original, engine

    def create_module(self, spec):
        return self.original.create_module(spec)

    def exec_module(self, module):
        self.original.exec_module(module)
        patch_module(module, self.engine)


class Finder(importlib.abc.MetaPathFinder):
    comparison_checks_support = True
    engine_scoped = True

    def find_spec(self, fullname, path=None, target=None):
        current = configuration()
        if current is None or target_attribute(fullname) is None:
            return None
        engine = current[0]
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or spec.loader is None:
            raise ImportError('Missing engine validator: ' + fullname)
        if spec.origin is None or not Path(spec.origin).resolve().is_relative_to(engine):
            return None
        spec.loader = Loader(spec.loader, engine)
        return spec


def handlers():
    return {'parse_fusion': fusion, 'parse_lazy_expansion_output': lazy,
            'write_json': write_fusion_receipt, 'restore_checks_label': comparison}


def install(engine, *, persistent=False, receipt_directory=None):
    engine = Path(engine).resolve()
    if persistent:
        _state.persistent = (engine, handlers(), receipt_directory)
    if not getattr(_state.finder, 'engine_scoped', False):
        if _state.finder in sys.meta_path:
            sys.meta_path.remove(_state.finder)
        _state.finder = Finder()
        sys.meta_path.insert(0, _state.finder)
    replacements = {}
    for name, module in list(sys.modules.items()):
        # Other releases may already be loaded by an offline collector. Only
        # select this engine's modules; patch_module still checks each target.
        path = getattr(module, '__file__', None)
        if target_attribute(name) and path and Path(path).resolve().is_relative_to(engine):
            pair = patch_module(module, engine)
            if pair:
                replacements[id(pair[0])] = pair[1]
    # A collector may already have loaded these engine modules for a legacy run.
    # Rebind their exported aliases too; wrappers remain inactive outside context.
    if replacements:
        for module in list(sys.modules.values()):
            path = getattr(module, '__file__', None)
            if path and Path(path).resolve().is_relative_to(engine):
                for name, value in list(vars(module).items()):
                    replacement = replacements.get(id(value))
                    if replacement is not None:
                        setattr(module, name, replacement)


@contextmanager
def enabled(engine):
    engine = Path(engine).resolve()
    install(engine)
    token = _state.active.set((engine, handlers(), None))
    try:
        yield
    finally:
        _state.active.reset(token)
