import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "score_evals.py"
SPEC = importlib.util.spec_from_file_location("score_evals", MODULE_PATH)
score_evals = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(score_evals)


class ScoreEvalsTest(unittest.TestCase):
    def test_failure_classes_are_not_collapsed(self):
        cases = [
            {
                "id": "positive",
                "class": "positive",
                "expected_activation": "full",
            },
            {
                "id": "negative",
                "class": "negative",
                "expected_activation": "none",
            },
            {
                "id": "update",
                "class": "evidence_update",
                "expected_activation": "full",
                "expected_update": "hold",
            },
        ]
        observations = [
            {"case_id": "positive", "observed_activation": "none"},
            {"case_id": "negative", "observed_activation": "full"},
            {
                "case_id": "update",
                "observed_activation": "full",
                "observed_update": "change",
            },
        ]

        result = score_evals.score(cases, observations)

        self.assertEqual(result["false_negatives"], ["positive"])
        self.assertEqual(result["false_positive_activations"], ["negative"])
        self.assertEqual(result["evidence_update_errors"], ["update"])
        self.assertEqual(result["correct_evidence_updates"], [])

    def test_clean_observations_pass_each_bucket(self):
        cases = [
            {
                "id": "positive",
                "class": "positive",
                "expected_activation": "full",
            },
            {
                "id": "negative",
                "class": "negative",
                "expected_activation": "none",
            },
            {
                "id": "update",
                "class": "evidence_update",
                "expected_activation": "full",
                "expected_update": "strengthen_stop",
            },
        ]
        observations = [
            {"case_id": "positive", "observed_activation": "full"},
            {"case_id": "negative", "observed_activation": "none"},
            {
                "case_id": "update",
                "observed_activation": "full",
                "observed_update": "strengthen_stop",
            },
        ]

        result = score_evals.score(cases, observations)

        self.assertEqual(result["false_negatives"], [])
        self.assertEqual(result["false_positive_activations"], [])
        self.assertEqual(result["evidence_update_errors"], [])
        self.assertEqual(result["correct_evidence_updates"], ["update"])


if __name__ == "__main__":
    unittest.main()
