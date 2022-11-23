import os
from io import StringIO
from unittest.mock import patch
from .TestBase import TestBase
from ..Results import Report, BaseReport, ReportBest, ReportDatasets, get_input
from ..Utils import Symbols


class ReportTest(TestBase):
    def test_get_input(self):
        self.assertEqual(get_input(is_test=True), "test")

    def test_BaseReport(self):
        with patch.multiple(BaseReport, __abstractmethods__=set()):
            file_name = os.path.join(
                "results",
                "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json",
            )
            a = BaseReport(file_name)
            self.assertIsNone(a.header())
            self.assertIsNone(a.print_line(None))
            self.assertIsNone(a.footer(accuracy=1.0))

    def test_report_with_folder(self):
        report = Report(
            file_name=os.path.join(
                "results",
                "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json",
            )
        )
        with patch(self.output, new=StringIO()) as stdout:
            report.report()
        self.check_output_file(stdout, "report")

    def test_report_without_folder(self):
        report = Report(
            file_name="results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
            ".json"
        )
        with patch(self.output, new=StringIO()) as stdout:
            report.report()
        self.check_output_file(stdout, "report")

    def test_report_compared(self):
        report = Report(
            file_name="results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
            ".json",
            compare=True,
        )
        with patch(self.output, new=StringIO()) as stdout:
            report.report()
        self.check_output_file(stdout, "report_compared")

    def test_compute_status(self):
        file_name = "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0.json"
        report = Report(
            file_name=file_name,
            compare=True,
        )
        with patch(self.output, new=StringIO()):
            report.report()
        res = report._compute_status("balloons", 0.99)
        self.assertEqual(res, Symbols.better_best)
        res = report._compute_status("balloons", 1.0)
        self.assertEqual(res, Symbols.better_best)

    def test_report_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            _ = Report("unknown_file")

    def test_report_best(self):
        report = ReportBest("accuracy", "STree", best=True)
        with patch(self.output, new=StringIO()) as stdout:
            report.report()
        self.check_output_file(stdout, "report_best")

    def test_report_grid(self):
        report = ReportBest("accuracy", "STree", best=False)
        with patch(self.output, new=StringIO()) as stdout:
            report.report()
        file_name = "report_grid.test"
        with open(os.path.join(self.test_files, file_name)) as f:
            expected = f.read().splitlines()
        output_text = stdout.getvalue().splitlines()
        # Compare replacing STree version
        for line, index in zip(expected, range(len(expected))):
            if self.stree_version in line:
                # replace STree version
                line = self.replace_STree_version(line, output_text, index)

            self.assertEqual(line, output_text[index])

    @patch("sys.stdout", new_callable=StringIO)
    def test_report_datasets(self, mock_output):
        report = ReportDatasets()
        report.report()
        file_name = f"report_datasets{self.ext}"
        with open(os.path.join(self.test_files, file_name)) as f:
            expected = f.read()
        output_text = mock_output.getvalue().splitlines()
        for line, index in zip(expected.splitlines(), range(len(expected))):
            if self.benchmark_version in line:
                # replace benchmark version
                line = self.replace_benchmark_version(line, output_text, index)
            self.assertEqual(line, output_text[index])
