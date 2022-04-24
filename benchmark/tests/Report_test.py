import os
import unittest
from io import StringIO
from unittest.mock import patch
from ..Results import Report, BaseReport, ReportBest
from ..Utils import Symbols


class ReportTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

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
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
            with open("test_files/report.test", "r") as f:
                expected = f.read()
            self.assertEqual(fake_out.getvalue(), expected)

    def test_report_without_folder(self):
        report = Report(
            file_name="results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
            ".json"
        )
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
            with open("test_files/report.test", "r") as f:
                expected = f.read()
            self.assertEqual(fake_out.getvalue(), expected)

    def test_report_compared(self):
        report = Report(
            file_name="results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
            ".json",
            compare=True,
        )
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
            with open("test_files/report_compared.test", "r") as f:
                expected = f.read()
            self.assertEqual(fake_out.getvalue(), expected)

    def test_compute_status(self):
        file_name = "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0.json"
        report = Report(
            file_name=file_name,
            compare=True,
        )
        with patch("sys.stdout", new=StringIO()):
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
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
            with open("test_files/report_best.test", "r") as f:
                expected = f.read()
            self.assertEqual(fake_out.getvalue(), expected)

    def test_report_grid(self):
        report = ReportBest("accuracy", "STree", best=False, grid=True)
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
            with open("test_files/report_grid.test", "r") as f:
                expected = f.read()
            self.assertEqual(fake_out.getvalue(), expected)

    def test_report_best_both(self):
        report = ReportBest("accuracy", "STree", best=True, grid=True)
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
            with open("test_files/report_best.test", "r") as f:
                expected = f.read()

            self.assertEqual(fake_out.getvalue(), expected)
