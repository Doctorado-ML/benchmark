import json
from .TestBase import TestBase
from ..Experiments import Experiment, Datasets


class ExperimentTest(TestBase):
    def setUp(self):
        self.exp = self.build_exp()

    def build_exp(self, hyperparams=False, grid=False):
        params = {
            "score_name": "accuracy",
            "model_name": "STree",
            "stratified": "0",
            "datasets": Datasets(),
            "hyperparams_dict": "{}",
            "hyperparams_file": hyperparams,
            "grid_paramfile": grid,
            "platform": "test",
            "title": "Test",
            "progress_bar": False,
            "folds": 2,
        }
        return Experiment(**params)

    def tearDown(self) -> None:
        self.remove_files(
            [
                self.exp.get_output_file(),
            ],
            ".",
        )
        return super().tearDown()

    def test_build_hyperparams_file(self):
        expected = {
            "balance-scale": [
                0.98,
                {"splitter": "iwss", "max_features": "auto"},
                "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0.json",
            ],
            "balloons": [
                0.86,
                {
                    "C": 7,
                    "gamma": 0.1,
                    "kernel": "rbf",
                    "max_iter": 10000.0,
                    "multiclass_strategy": "ovr",
                },
                "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json",
            ],
        }
        exp = self.build_exp(hyperparams=True)
        self.assertSequenceEqual(exp.hyperparameters_dict, expected)

    def test_build_grid_file(self):
        expected = {
            "balance-scale": [
                0.9199946751863685,
                {
                    "C": 1.0,
                    "kernel": "liblinear",
                    "multiclass_strategy": "ovr",
                },
                "",
            ],
            "balloons": [
                0.625,
                {"C": 1.0, "kernel": "linear", "multiclass_strategy": "ovr"},
                "",
            ],
        }
        exp = self.build_exp(grid=True)
        computed = exp.hyperparameters_dict
        # Remove generation string as it is dynamic through time
        for name in ["balance-scale", "balloons"]:
            computed[name][2] = ""
        self.assertSequenceEqual(exp.hyperparameters_dict, expected)

    def test_get_output_file(self):
        file_name = self.exp.get_output_file()
        self.assertTrue(
            file_name.startswith("results/results_accuracy_STree_test_")
        )
        self.assertTrue(file_name.endswith("_0.json"))

    def test_exception_n_fold_crossval(self):
        self.exp.do_experiment()
        with self.assertRaises(ValueError):
            self.exp._n_fold_crossval([], [], {})

    def test_do_experiment(self):
        self.exp.do_experiment()
        file_name = self.exp.get_output_file()
        with open(file_name) as f:
            data = json.load(f)
        # Check Header
        expected = {
            "score_name": "accuracy",
            "title": "Test",
            "model": "STree",
            "stratified": False,
            "folds": 2,
            "seeds": [57, 31, 1714, 17, 23, 79, 83, 97, 7, 1],
            "platform": "test",
        }
        for key, value in expected.items():
            self.assertEqual(data[key], value)
        # Check Results
        expected_results = [
            {
                "dataset": "balance-scale",
                "samples": 625,
                "features": 4,
                "classes": 3,
                "hyperparameters": {},
            },
            {
                "dataset": "balloons",
                "samples": 16,
                "features": 4,
                "classes": 2,
                "hyperparameters": {},
            },
        ]

        for expected_result, computed_result in zip(
            expected_results, data["results"]
        ):
            for key, value in expected_result.items():
                self.assertEqual(computed_result[key], value)
