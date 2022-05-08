import os
from io import StringIO
from unittest.mock import patch
from ...Utils import Folders
from ...Results import Report
from ..TestBase import TestBase


class BeMainTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()
        self.score = "accuracy"
        self.files = []

    def tearDown(self) -> None:
        self.remove_files(self.files, ".")
        return super().tearDown()

    def test_be_benchmark_dataset(self):
        stdout, _ = self.execute_script(
            "be_main",
            ["-m", "STree", "-d", "balloons", "--title", "test"],
        )
        with open(os.path.join(self.test_files, "be_main_dataset.test")) as f:
            expected = f.read()
        n_line = 0
        # compare only report lines without date, time, duration...
        lines_to_compare = [0, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13]
        for expected, computed in zip(
            expected.splitlines(), stdout.getvalue().splitlines()
        ):
            if n_line in lines_to_compare:
                self.assertEqual(computed, expected, n_line)
            n_line += 1

    def test_be_benchmark_complete(self):
        stdout, _ = self.execute_script(
            "be_main",
            ["-s", self.score, "-m", "STree", "--title", "test", "-r", "1"],
        )
        with open(os.path.join(self.test_files, "be_main_complete.test")) as f:
            expected = f.read()
        n_line = 0
        # keep the report name to delete it after
        self.files.append(stdout.getvalue().splitlines()[-1].split("in ")[1])
        # compare only report lines without date, time, duration...
        lines_to_compare = [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14]
        for expected, computed in zip(
            expected.splitlines(), stdout.getvalue().splitlines()
        ):
            if n_line in lines_to_compare:
                self.assertEqual(computed, expected, n_line)
            n_line += 1

    def test_be_benchmark_no_report(self):
        stdout, _ = self.execute_script(
            "be_main",
            ["-s", self.score, "-m", "STree", "--title", "test"],
        )
        with open(os.path.join(self.test_files, "be_main_complete.test")) as f:
            expected = f.read()
        # keep the report name to delete it after
        report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
        self.files.append(report_name)
        report = Report(file_name=report_name)
        with patch(self.output, new=StringIO()) as stdout:
            report.report()
        # compare only report lines without date, time, duration...
        lines_to_compare = [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14]
        n_line = 0
        for expected, computed in zip(
            expected.splitlines(), stdout.getvalue().splitlines()
        ):
            if n_line in lines_to_compare:
                self.assertEqual(computed, expected, n_line)
            n_line += 1

    def test_be_benchmark_no_data(self):
        stdout, _ = self.execute_script(
            "be_main", ["-m", "STree", "-d", "unknown", "--title", "test"]
        )
        self.assertEqual(stdout.getvalue(), "Unknown dataset: unknown\n")
