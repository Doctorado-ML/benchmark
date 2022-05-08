import shutil
from io import StringIO
from unittest.mock import patch
from ...Results import Report
from ...Utils import Files
from ..TestBase import TestBase


class BePrintStrees(TestBase):
    def setUp(self):
        self.prepare_scripts_env()
        source = Files.grid_output("accuracy", "STree")
        target = Files.grid_output("accuracy", "STree")
        shutil.copy(source, target)
        self.score = "accuracy"
        self.files = [target]

    def tearDown(self) -> None:
        self.remove_files(self.files, ".")
        return super().tearDown()

    # def test_be_benchmark_dataset(self):
    #     stdout, _ = self.execute_script(
    #         "be_main",
    #         ["-m", "STree", "-d", "balloons", "--title", "test"],
    #     )
    #     self.check_output_lines(
    #         stdout=stdout,
    #         file_name="be_main_dataset",
    #         lines_to_compare=[0, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13],
    #     )

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
