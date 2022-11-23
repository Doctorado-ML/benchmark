import os
import json
from ...Utils import Folders, Files, NO_RESULTS
from ..TestBase import TestBase


class BeBestTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self) -> None:
        self.remove_files(
            [Files.best_results("accuracy", "ODTE")],
            Folders.results,
        )
        return super().tearDown()

    def test_be_best_all(self):
        stdout, stderr = self.execute_script("be_best", ["-s", "all"])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "be_best_all")

    def test_be_build_best_error(self):
        stdout, _ = self.execute_script(
            "be_build_best", ["-s", "accuracy", "-m", "SVC"]
        )
        self.assertEqual(stdout.getvalue(), f"{NO_RESULTS}\n")

    def test_be_build_best(self):
        self.execute_script("be_build_best", ["-s", "accuracy", "-m", "ODTE"])
        expected_data = {
            "balance-scale": [
                0.96352,
                {
                    "base_estimator__C": 57,
                    "base_estimator__gamma": 0.1,
                    "base_estimator__kernel": "rbf",
                    "base_estimator__multiclass_strategy": "ovr",
                    "n_estimators": 100,
                    "n_jobs": -1,
                },
                "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json",
            ],
            "balloons": [
                0.785,
                {
                    "base_estimator__C": 5,
                    "base_estimator__gamma": 0.14,
                    "base_estimator__kernel": "rbf",
                    "base_estimator__multiclass_strategy": "ovr",
                    "n_estimators": 100,
                    "n_jobs": -1,
                },
                "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json",
            ],
        }
        name = Files.best_results("accuracy", "ODTE")
        file_name = os.path.join(Folders.results, name)
        with open(file_name, "r") as f:
            computed_data = json.load(f)
        for computed, expected in zip(computed_data, expected_data):
            self.assertEqual(computed, expected)
        for key, value in expected_data.items():
            self.assertIn(key, computed_data)
            self.assertEqual(computed_data[key][0], value[0])
            self.assertSequenceEqual(computed_data[key][1], value[1])

    def test_be_build_best_report(self):
        stdout, _ = self.execute_script(
            "be_build_best", ["-s", "accuracy", "-m", "ODTE", "-r"]
        )
        expected_data = {
            "balance-scale": [
                0.96352,
                {
                    "base_estimator__C": 57,
                    "base_estimator__gamma": 0.1,
                    "base_estimator__kernel": "rbf",
                    "base_estimator__multiclass_strategy": "ovr",
                    "n_estimators": 100,
                    "n_jobs": -1,
                },
                "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json",
            ],
            "balloons": [
                0.785,
                {
                    "base_estimator__C": 5,
                    "base_estimator__gamma": 0.14,
                    "base_estimator__kernel": "rbf",
                    "base_estimator__multiclass_strategy": "ovr",
                    "n_estimators": 100,
                    "n_jobs": -1,
                },
                "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json",
            ],
        }
        name = Files.best_results("accuracy", "ODTE")
        file_name = os.path.join(Folders.results, name)
        with open(file_name, "r") as f:
            computed_data = json.load(f)
        for computed, expected in zip(computed_data, expected_data):
            self.assertEqual(computed, expected)
        for key, value in expected_data.items():
            self.assertIn(key, computed_data)
            self.assertEqual(computed_data[key][0], value[0])
            self.assertSequenceEqual(computed_data[key][1], value[1])
        self.check_output_file(stdout, "be_build_best_report")
