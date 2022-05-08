import os
import hashlib
from ...Utils import Folders
from ..TestBase import TestBase


class BePrintStrees(TestBase):
    def setUp(self):
        self.prepare_scripts_env()
        self.score = "accuracy"
        self.files = []
        self.datasets = ["balloons", "balance-scale"]
        self.expected = {
            "balloons": {
                "color": "b2342cc27a4ab495970616346bedf73b",
                "gray": "a9bc4d2041f2869a93164a548f6ad986",
            },
            "balance-scale": {
                "color": "2e85d66de1ae838d01a3f327397a50c8",
                "gray": "30f325134d4b5153c9e6ecbcae7b6d1f",
            },
        }

    def tearDown(self) -> None:
        self.remove_files(self.files, ".")
        return super().tearDown()

    def hash_file(self, name):
        file_name = os.path.join(Folders.img, f"{name}.png")
        self.files.append(file_name)
        self.assertTrue(os.path.exists(file_name))
        with open(file_name, "rb") as f:
            return hashlib.md5(f.read()).hexdigest(), file_name

    def test_be_print_strees_dataset_bn(self):
        for name in self.datasets:
            stdout, _ = self.execute_script(
                "be_print_strees",
                ["-d", name, "-q", "1"],
            )
            computed_hash, file_name = self.hash_file(f"stree_{name}")
            self.assertEqual(
                stdout.getvalue(), f"File {file_name} generated\n"
            )
            self.assertEqual(computed_hash, self.expected[name]["gray"])

    def test_be_print_strees_dataset_color(self):
        for name in self.datasets:
            stdout, _ = self.execute_script(
                "be_print_strees",
                ["-d", name, "-q", "1", "-c", "1"],
            )
            computed_hash, file_name = self.hash_file(f"stree_{name}")
            self.assertEqual(
                stdout.getvalue(), f"File {file_name} generated\n"
            )
            self.assertEqual(computed_hash, self.expected[name]["color"])

    # def test_be_benchmark_complete(self):
    #     stdout, _ = self.execute_script(
    #         "be_main",
    #         ["-s", self.score, "-m", "STree", "--title", "test", "-r", "1"],
    #     )
    #     # keep the report name to delete it after
    #     report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
    #     self.files.append(report_name)
    #     self.check_output_lines(
    #         stdout, "be_main_complete", [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14]
    #     )

    # def test_be_benchmark_no_report(self):
    #     stdout, _ = self.execute_script(
    #         "be_main",
    #         ["-s", self.score, "-m", "STree", "--title", "test"],
    #     )
    #     # keep the report name to delete it after
    #     report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
    #     self.files.append(report_name)
    #     report = Report(file_name=report_name)
    #     with patch(self.output, new=StringIO()) as stdout:
    #         report.report()
    #     self.check_output_lines(
    #         stdout,
    #         "be_main_complete",
    #         [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14],
    #     )

    # def test_be_benchmark_best_params(self):
    #     stdout, _ = self.execute_script(
    #         "be_main",
    #         [
    #             "-s",
    #             self.score,
    #             "-m",
    #             "STree",
    #             "--title",
    #             "test",
    #             "-f",
    #             "1",
    #             "-r",
    #             "1",
    #         ],
    #     )
    #     # keep the report name to delete it after
    #     report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
    #     self.files.append(report_name)
    #     self.check_output_lines(
    #         stdout, "be_main_best", [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14]
    #     )

    # def test_be_benchmark_grid_params(self):
    #     stdout, _ = self.execute_script(
    #         "be_main",
    #         [
    #             "-s",
    #             self.score,
    #             "-m",
    #             "STree",
    #             "--title",
    #             "test",
    #             "-g",
    #             "1",
    #             "-r",
    #             "1",
    #         ],
    #     )
    #     # keep the report name to delete it after
    #     report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
    #     self.files.append(report_name)
    #     self.check_output_lines(
    #         stdout, "be_main_grid", [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14]
    #     )

    # def test_be_benchmark_no_data(self):
    #     stdout, _ = self.execute_script(
    #         "be_main", ["-m", "STree", "-d", "unknown", "--title", "test"]
    #     )
    #     self.assertEqual(stdout.getvalue(), "Unknown dataset: unknown\n")
