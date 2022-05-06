from io import StringIO
from unittest.mock import patch
from .TestBase import TestBase
from ..Results import Report, BaseReport, ReportBest, ReportDatasets
from ..Utils import Symbols


class ReportTest(TestBase):
    def test_BaseReport(self):
        with patch.multiple(BaseReport, __abstractmethods__=set()):
            file_name = (
                "results/results_accuracy_STree_iMac27_2021-09-30_11:"
                "42:07_0.json"
            )
            a = BaseReport(file_name)
            self.assertIsNone(a.header())
            self.assertIsNone(a.print_line(None))
            self.assertIsNone(a.footer(accuracy=1.0))

    def test_report_with_folder(self):
        report = Report(
            file_name="results/results_accuracy_STree_iMac27_2021-09-30_11:"
            "42:07_0.json"
        )
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "report.test")

    def test_report_without_folder(self):
        report = Report(
            file_name="results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
            ".json"
        )
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "report.test")

    def test_report_compared(self):
        report = Report(
            file_name="results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
            ".json",
            compare=True,
        )
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "report_compared.test")

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
        report = ReportBest("accuracy", "STree", best=True, grid=False)
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "report_best.test")

    def test_report_grid(self):
        report = ReportBest("accuracy", "STree", best=False, grid=True)
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "report_grid.test")

    def test_report_best_both(self):
        report = ReportBest("accuracy", "STree", best=True, grid=True)
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "report_best.test")

    @patch("sys.stdout", new_callable=StringIO)
    def test_report_datasets(self, mock_output):
        report = ReportDatasets()
        report.report()
        self.check_output_file(mock_output, "report_datasets.test")
