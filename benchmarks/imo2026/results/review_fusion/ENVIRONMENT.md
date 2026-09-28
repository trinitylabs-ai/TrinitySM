# Historical environment provenance

This experiment predates automatic pre-launch environment snapshots. Its saved configuration is in [generation/harness_and_models.json](generation/harness_and_models.json), original per-problem manifests in [generation/](generation), and grader model/rubric records in [grading/](grading). An exact historical hardware, package, driver or cache-state snapshot is unavailable unless present in those original records.

The repository ENVIRONMENT.md describes the current Advanced setup. It must not be applied retrospectively to this experiment: historical Basic solver policies changed, and the Basic no-budget-forcing run used Gemma on both GPUs rather than the current Gemma/Qwen placement. Existing saved proof/grade files are unchanged.
