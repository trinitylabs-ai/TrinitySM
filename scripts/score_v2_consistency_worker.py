#!/usr/bin/env python3
"""Strict-v2 worker that retains score/metadata disagreements for measurement."""
import sys

from score_imo_v2 import prepare_runner


def prepare_study_runner():
    runner = prepare_runner()
    strict_validate = runner.validate_grade
    structural_validate = sys.modules['scripts.external_olympiad_scorer.contract'].validate_grade

    def retain_disagreement(value):
        try:
            return strict_validate(value)
        except ValueError as error:
            if str(error) != 'Inconsistent score metadata in evaluator response':
                raise
            # A readable numerical grade is an observation, including when its
            # explanation/metadata disagrees. Resampling would bias consistency.
            return structural_validate(value)

    runner.validate_grade = retain_disagreement
    return runner


if __name__ == '__main__':
    sys.argv.extend(['--policy-mode', 'strict'])
    prepare_study_runner().main()
