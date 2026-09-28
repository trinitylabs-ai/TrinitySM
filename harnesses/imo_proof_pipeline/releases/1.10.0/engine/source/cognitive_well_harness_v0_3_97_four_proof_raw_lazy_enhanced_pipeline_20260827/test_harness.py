from __future__ import annotations

import json
from pathlib import Path

import pytest

from .run import (
    RAW_CANDIDATE_IDS,
    RAW_CANDIDATES,
    build_v096_cases_manifest,
    normalize_problem_input,
    run,
    stable_raw_seed,
)


def test_four_candidate_temperature_allocation_is_frozen() -> None:
    assert tuple(row["candidate_id"] for row in RAW_CANDIDATES) == RAW_CANDIDATE_IDS
    assert [row["temperature"] for row in RAW_CANDIDATES] == [1.0, 1.0, 0.7, 0.7]
    assert len({row["seed"] for row in RAW_CANDIDATES}) == 4


def test_local_seed_policy_preserves_frozen_v048_values_without_importing_driver() -> None:
    assert {
        row["candidate_id"]: stable_raw_seed(
            3, str(row["candidate_id"]), int(row["seed"])
        )
        for row in RAW_CANDIDATES
    } == {
        "t10_r01": 163144128,
        "t10_r02": 1694007814,
        "t07_r01": 620124295,
        "t07_r02": 3507849570,
    }


def test_plain_problem_statement_is_normalized(tmp_path: Path) -> None:
    source = tmp_path / "new_problem.txt"
    source.write_text("Prove a generic mathematical assertion.", encoding="utf-8")
    problem = normalize_problem_input(
        source_path=source,
        output_dir=tmp_path / "run",
        problem_id_override="generic_p8",
    )
    assert problem["problem_number"] == 8
    payload = json.loads(Path(problem["path"]).read_text(encoding="utf-8"))
    assert payload["claim"] == "Prove a generic mathematical assertion."


@pytest.mark.parametrize(
    "forbidden_field",
    ["codex_score", "codex_grade", "gold_solution", "reference", "history"],
)
def test_problem_only_input_rejects_external_or_historical_fields(
    tmp_path: Path, forbidden_field: str
) -> None:
    source = tmp_path / "problem.json"
    source.write_text(
        json.dumps(
            {
                "problem_id": "generic_p8",
                "claim": "Prove a generic mathematical assertion.",
                forbidden_field: "POISON",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="auxiliary fields"):
        normalize_problem_input(source_path=source, output_dir=tmp_path / "run")


def test_problem_identity_cannot_be_relabelled_across_problem_boundaries(
    tmp_path: Path,
) -> None:
    source = tmp_path / "problem.json"
    source.write_text(
        json.dumps({"problem_id": "p2", "claim": "Prove P2."}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="problem_id override"):
        normalize_problem_input(
            source_path=source,
            output_dir=tmp_path / "run",
            problem_id_override="p3",
        )


def test_v096_handoff_has_exactly_four_live_checked_proofs(tmp_path: Path) -> None:
    problem_path = tmp_path / "problem.json"
    problem_path.write_text(json.dumps({"claim": "P"}), encoding="utf-8")
    problem = {
        "problem_id": "generic_p2",
        "problem_number": 2,
        "path": problem_path,
    }
    rows = []
    for candidate_id in RAW_CANDIDATE_IDS:
        proof_path = tmp_path / f"{candidate_id}.md"
        proof_path.write_text("proof", encoding="utf-8")
        rows.append({"candidate_id": candidate_id, "checked_proof_path": str(proof_path)})
    manifest = build_v096_cases_manifest(problem=problem, final_rows=rows)
    assert len(manifest["cases"]) == 4
    assert [row["candidate_id"] for row in manifest["cases"]] == list(RAW_CANDIDATE_IDS)


def test_dry_run_records_split_gpu_batch_schedule(tmp_path: Path) -> None:
    problem_path = tmp_path / "problem.json"
    problem_path.write_text(
        json.dumps(
            {
                "problem_id": "generic_p2",
                "problem_number": 2,
                "claim": "Prove a generic mathematical assertion.",
            }
        ),
        encoding="utf-8",
    )
    summary = run(
        problem_file=problem_path,
        output_dir=tmp_path / "run",
        gpu0_gemma_endpoint="http://gpu0.example/v1",
        gpu1_qwen_endpoint="http://gpu1.example/v1",
        seed_namespace="test",
        dry_run=True,
    )
    assert summary["state"] == "dry_run_completed"
    assert summary["review_schedule"]["gpu0"].endswith("reviewer_3_batch_of_4")
    manifest = json.loads((tmp_path / "run" / "manifest.json").read_text())
    assert manifest["device_roles"]["gpu1"]["stages"] == ["reviewer_2"]
