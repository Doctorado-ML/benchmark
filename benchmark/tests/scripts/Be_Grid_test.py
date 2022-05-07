import os
import json
from ...Utils import Folders, Files
from ..TestBase import TestBase


class BeGridTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self) -> None:
        self.remove_files(
            [
                Files.grid_input("f1-macro", "STree"),
                Files.grid_output("accuracy", "SVC"),
            ],
            Folders.results,
        )
        return super().tearDown()

    def test_be_build_grid(self):
        stdout, stderr = self.execute_script(
            "be_build_grid", ["-m", "STree", "-s", "f1-macro"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(
            stdout.getvalue(),
            "Generated grid input file to results/grid_input_f1-macro_STree."
            "json\n",
        )
        name = Files.grid_input("f1-macro", "STree")
        file_name = os.path.join(Folders.results, name)
        self.check_file_file(file_name, "be_build_grid")

    def test_be_grid_(self):
        stdout, stderr = self.execute_script(
            "be_grid",
            ["-m", "SVC", "-s", "accuracy", "--n_folds", "2"],
        )
        expected = "Perform grid search with SVC model\n"
        self.assertTrue(stdout.getvalue().startswith(expected))
        name = Files.grid_output("accuracy", "SVC")
        file_name = os.path.join(Folders.results, name)
        with open(file_name, "r") as f:
            computed_data = json.load(f)
        expected_data = {
            "balance-scale": [
                0.9167895469812403,
                {"C": 5.0, "kernel": "linear"},
                "v. -, Computed on iMac27 on 2022-05-07 at 23:55:03 took",
            ],
            "balloons": [
                0.6875,
                {"C": 5.0, "kernel": "rbf"},
                "v. -, Computed on iMac27 on 2022-05-07 at 23:55:03 took",
            ],
        }
        for computed, expected in zip(computed_data, expected_data):
            self.assertEqual(computed, expected)
        for key, value in expected_data.items():
            self.assertIn(key, computed_data)
            self.assertEqual(computed_data[key][0], value[0])
            self.assertEqual(computed_data[key][1], value[1])

    def test_be_grid_no_input(self):
        stdout, stderr = self.execute_script(
            "be_grid",
            ["-m", "ODTE", "-s", "f1-weighted", "-q", "1"],
        )
        self.assertEqual(stderr.getvalue(), "")
        grid_file = os.path.join(
            Folders.results, Files.grid_input("f1-weighted", "ODTE")
        )
        expected = f"** The grid input file [{grid_file}] could not be found\n"
        self.assertEqual(stdout.getvalue(), expected)
