"""All run records here are synthetic test data, not agent evaluations."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("score", ROOT / "evals" / "score.py")
score = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(score)


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.suite = {
            "schema_version": 1,
            "cases": [{"id": "A", "control": False, "category": "example",
                       "prompt": "Invented test prompt", "setup": "Synthetic setup",
                       "criteria": [
                           {"id": "cause", "text": "Checks cause", "critical": True},
                           {"id": "scope", "text": "Keeps scope", "critical": False},
                       ]}],
        }
        self.serial = 0

    def run_record(self, condition, values=(True, True), pair="one", case="A"):
        self.serial += 1
        artifact = f"run-{self.serial}.md"
        (self.root / artifact).write_text("Invented test artifact, not an agent run.", encoding="utf-8")
        return {"case_id": case, "pair_id": pair, "condition": condition,
                "model": "synthetic-test-model", "setup_id": "synthetic-setup",
                "artifact": artifact,
                "criteria": {key: {"passed": value, "evidence": "Synthetic test evidence."}
                             for key, value in zip(("cause", "scope"), values)}}

    def pair(self, baseline=(False, True), skill=(True, True), **kwargs):
        return [self.run_record("baseline", baseline, **kwargs),
                self.run_record("skill", skill, **kwargs)]

    def summarize(self, runs):
        return score.summarize(self.suite, {"schema_version": 1, "runs": runs}, self.root)

    def test_empty_is_explicitly_unmeasured(self):
        result = self.summarize([])
        self.assertEqual(result["status"], "not_measured")
        self.assertIsNone(result["conditions"])
        self.assertNotIn("skill_minus_baseline", result)

    def test_valid_pair_reports_scores_and_critical_failures_separately(self):
        result = self.summarize(self.pair())
        self.assertEqual(result["conditions"]["baseline"]["mean_criterion_score"], 0.5)
        self.assertEqual(result["conditions"]["baseline"]["critical_failure_rate"], 1)
        self.assertEqual(result["conditions"]["skill"]["critical_failure_rate"], 0)
        self.assertEqual(result["skill_minus_baseline"], 0.5)

    def test_tie_is_not_reported_as_improvement(self):
        result = self.summarize(self.pair(baseline=(True, True)))
        self.assertEqual(result["skill_minus_baseline"], 0)

    def test_cases_have_equal_weight_despite_uneven_trial_counts(self):
        second = deepcopy(self.suite["cases"][0])
        second.update(id="B", control=True)
        self.suite["cases"].append(second)
        runs = []
        for trial in range(4):
            runs += self.pair(baseline=(False, False), pair=str(trial))
        runs += self.pair(baseline=(True, True), skill=(False, False), case="B")
        result = self.summarize(runs)
        self.assertEqual(result["conditions"]["baseline"]["mean_criterion_score"], 0.5)
        self.assertEqual(result["conditions"]["skill"]["mean_criterion_score"], 0.5)
        self.assertTrue(result["per_case"]["B"]["control"])
        self.assertEqual(result["groups"]["target_cases"]["skill_minus_baseline"], 1)
        self.assertEqual(result["groups"]["control_cases"]["skill_minus_baseline"], -1)

    def test_incomplete_pair_is_rejected(self):
        with self.assertRaisesRegex(score.ScoreError, "incomplete pair"):
            self.summarize([self.run_record("baseline")])

    def test_duplicate_condition_is_rejected(self):
        with self.assertRaisesRegex(score.ScoreError, "duplicate condition"):
            self.summarize([self.run_record("baseline"), self.run_record("baseline")])

    def test_different_model_or_setup_within_pair_is_rejected(self):
        for field in ("model", "setup_id"):
            with self.subTest(field=field):
                runs = self.pair()
                runs[1][field] = "different"
                with self.assertRaisesRegex(score.ScoreError, f"different {field}"):
                    self.summarize(runs)

    def test_models_cannot_be_pooled_across_pairs(self):
        runs = self.pair()
        another = self.pair(pair="two")
        for run in another:
            run["model"] = "another-model"
        with self.assertRaisesRegex(score.ScoreError, "separate score file"):
            self.summarize(runs + another)

    def test_missing_extra_and_nonboolean_grades_are_rejected(self):
        for change in ("missing", "extra", "string"):
            with self.subTest(change=change):
                runs = self.pair()
                if change == "missing":
                    del runs[0]["criteria"]["cause"]
                elif change == "extra":
                    runs[0]["criteria"]["extra"] = {"passed": True, "evidence": "Invented."}
                else:
                    runs[0]["criteria"]["cause"]["passed"] = "true"
                with self.assertRaises(score.ScoreError):
                    self.summarize(runs)

    def test_blank_evidence_note_is_rejected(self):
        runs = self.pair()
        runs[0]["criteria"]["cause"]["evidence"] = " "
        with self.assertRaisesRegex(score.ScoreError, "missing evidence"):
            self.summarize(runs)

    def test_artifact_must_exist_be_nonempty_and_stay_inside_results(self):
        for path in ("missing.md", "../outside.md", "C:/outside.md", "folder\\run.md", "empty.md"):
            with self.subTest(path=path):
                (self.root / "empty.md").write_text("", encoding="utf-8")
                runs = self.pair()
                runs[0]["artifact"] = path
                with self.assertRaises(score.ScoreError):
                    self.summarize(runs)

    def test_each_run_needs_a_distinct_artifact(self):
        runs = self.pair()
        runs[1]["artifact"] = runs[0]["artifact"]
        with self.assertRaisesRegex(score.ScoreError, "distinct artifact"):
            self.summarize(runs)

    def test_unknown_case_and_condition_are_rejected(self):
        for field, value in (("case_id", "unknown"), ("condition", "candidate")):
            with self.subTest(field=field):
                runs = self.pair()
                runs[0][field] = value
                with self.assertRaises(score.ScoreError):
                    self.summarize(runs)

    def test_invalid_suite_is_rejected_even_for_empty_scores(self):
        for mutation in ("duplicate_case", "duplicate_criterion", "boolean_version"):
            with self.subTest(mutation=mutation):
                suite = deepcopy(self.suite)
                if mutation == "duplicate_case":
                    suite["cases"].append(deepcopy(suite["cases"][0]))
                elif mutation == "duplicate_criterion":
                    suite["cases"][0]["criteria"].append(deepcopy(suite["cases"][0]["criteria"][0]))
                else:
                    suite["schema_version"] = True
                with self.assertRaises(score.ScoreError):
                    score.summarize(suite, {"schema_version": 1, "runs": []}, self.root)

    def test_cli_empty_template_and_invalid_json_exit_codes(self):
        template = ROOT / "evals" / "scores.template.json"
        valid = subprocess.run([sys.executable, str(ROOT / "evals" / "score.py"), str(template)],
                               capture_output=True, text=True, check=False)
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(json.loads(valid.stdout)["status"], "not_measured")
        invalid = self.root / "invalid.json"
        invalid.write_text("{broken", encoding="utf-8")
        failed = subprocess.run([sys.executable, str(ROOT / "evals" / "score.py"), str(invalid)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, "")
        self.assertIn("Invalid evaluation:", failed.stderr)

    def test_cli_accepts_utf8_bom_and_rejects_duplicate_json_fields(self):
        scores_path = self.root / "scores.json"
        scores_path.write_text('{"schema_version": 1, "runs": []}', encoding="utf-8-sig")
        command = [sys.executable, str(ROOT / "evals" / "score.py"), str(scores_path)]
        accepted = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        scores_path.write_text('{"schema_version": 1, "runs": [], "runs": []}', encoding="utf-8")
        rejected = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(rejected.returncode, 2)
        self.assertEqual(rejected.stdout, "")
        self.assertIn("Duplicate JSON field", rejected.stderr)

    def test_partial_coverage_is_reported(self):
        unmeasured = deepcopy(self.suite["cases"][0])
        unmeasured["id"] = "B"
        self.suite["cases"].append(unmeasured)
        result = self.summarize(self.pair())
        self.assertEqual(result["coverage"], {"represented": 1, "total": 2, "missing": ["B"]})


if __name__ == "__main__":
    unittest.main()
