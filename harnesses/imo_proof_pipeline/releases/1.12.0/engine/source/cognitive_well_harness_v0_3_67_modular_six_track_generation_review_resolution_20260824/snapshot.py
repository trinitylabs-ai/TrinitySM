from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent

# The modular harness reuses these implementations directly. Pinning them makes
# "v0.3.48 through v0.3.54" a reproducible protocol rather than a moving import.
PINNED_UPSTREAM_SHA256 = {
    "cognitive_well_harness_v0_3_35_cap_continuation_recovery_20260822/pipeline.py": "928527511b99b9699e168fc386ff0706e39676bfcb50b8cec7ced9a277198895",
    "cognitive_well_harness_v0_3_36_p4_dual_block_replay_snapshot_20260822/cold_prompts.py": "3baf094b8eb12b27a9a1eceb5592d3c12c9996ef1d31ed378b74c0af7f119efe",
    "cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822/pipeline.py": "28ff5acaef78c6d9dd4c0ae5c132e01e9b2839d77a8cd5e92aaad47762c77076",
    "cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822/runtime.py": "840ec87faddd20b3510810ada2553a1b5ab52ec9b7c7686b5585fa6db10f2a4b",
    "cognitive_well_harness_v0_3_42_gemma4_dual_prompt_max_thinking_coldsolve_20260823/run.py": "0ab85dd126ac482863453318f64dffa0ad579201dded7134ef903c2bf9e8821f",
    "cognitive_well_harness_v0_3_44_gemma4_high_stakes_gate_coldsolve_20260823/run.py": "b7c3cee1dd1f9d41a3c6408a64d1ca8367f70d9609a979f28dd3e48bc1e35a95",
    "cognitive_well_harness_v0_3_45_gemma4_high_stakes_no_checklist_coldsolve_20260823/run.py": "ce2604fe1c223ef140574100d3ca232d5eae9bc8c96e9706cc82a7ea5b6b7e84",
    "cognitive_well_harness_v0_3_46_gemma4_temperature_portfolio_20260823/run.py": "c02d41311197f096bbcb3df4afc6d966064072f315de3c45ceb32397a2911861",
    "cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823/contracts.py": "4bd3849a5af74815e54bfb0f994eede289a8ec1a0159863db480ece43e318590",
    "cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823/lazy_expansion.py": "ebd50df6d173e4f38ceef4baa4334add3d4630c2c8e14ef623375c1ba3235f89",
    "cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823/run_six_candidate_lazy_test.py": "409f548edc897f0211353528a27d676d5157efee761c7e7878be563e195fc3ec",
    "cognitive_well_harness_v0_3_48_multi_problem_six_candidate_20260823/run.py": "822e9bdb3c54fd1cc8f6aa5f2af36da136d1a85d522fef88e63307d62d5e1db0",
    "cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823/protocol.py": "0088a37c39159f8a23a9a13ce6d68b283979bcd2acd0a018a7dc2adecf54d518",
    "cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823/run.py": "f1add78a1187384439e9f388e9462f7c292d9f583fab90a505e573f9f1f49d20",
    "cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823/protocol.py": "911f7011d0a02f8b5c05fdd5366b40c76cf09b2ea90ce56cf6028fdafe41093a",
    "cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823/run.py": "14b7dee7e11808fa18f906ab40b5cc6939e88e15311e1155c8aed133d06986df",
    "cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823/protocol.py": "eccb6918c5464d2b64f396bcf782d89d99818399d7922dcfc151226f660a8879",
    "cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823/run.py": "2a50a37fc83923e647036a7be02e3afc876cebb189467456614660e8854e1ce4",
    "cognitive_well_harness_v0_3_52_fusion_20260823/protocol.py": "ccb74e5bfc28f72766f36208b0a9d1be3941b3c0994f69422b00e7020a995725",
    "cognitive_well_harness_v0_3_52_fusion_20260823/run.py": "a9857ff093722c8b488d918f5cfe0ce0eceeee4481161e12609bdbf36ff6555c",
    "cognitive_well_harness_v0_3_53_fusion_20260823/protocol.py": "82200768ec47b6c0167aabf5aab47f2706d80aad0d1384a513f33cac5b7b6f64",
    "cognitive_well_harness_v0_3_53_fusion_20260823/run.py": "066bfa3c739983a7e6d05a9458f46ed9f002e68f0514d6e00d60fa5987bd086a",
    "cognitive_well_harness_v0_3_54_resolver_20260823/protocol.py": "ee1c019ff3f8ad6e2b87d6b16e1cab995936eccb688606047cc57ae9aac58780",
    "cognitive_well_harness_v0_3_54_resolver_20260823/run.py": "c931793eb6c30434c852a1b0ae74d4dbe52591e8e4246b3c14a36eae8436d35a",
}


def assert_frozen_upstream() -> dict[str, Any]:
    observed: dict[str, str] = {}
    for relative, expected in PINNED_UPSTREAM_SHA256.items():
        path = REPO_ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"missing frozen upstream file: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        observed[relative] = digest
        if digest != expected:
            raise RuntimeError(
                f"frozen upstream changed at {relative}: expected {expected}, "
                f"observed {digest}"
            )
    aggregate = hashlib.sha256()
    for relative in sorted(observed):
        aggregate.update(relative.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(observed[relative].encode("ascii"))
        aggregate.update(b"\0")
    return {
        "files": observed,
        "aggregate_sha256": aggregate.hexdigest(),
    }
