import os
import unittest
from io import StringIO
from unittest.mock import patch
from ..Results import Summary
from ..Utils import Symbols


class PairCheckTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

    def test_summary_list_results_model(self):
        report = Summary()
        report.acquire()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.list_results(model="STree")
        computed = fake_out.getvalue()
        with open(
            os.path.join("test_files", "summary_list_model.test"), "r"
        ) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_summary_list_results_score(self):
        report = Summary()
        report.acquire()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.list_results(score="accuracy")
        computed = fake_out.getvalue()
        with open(
            os.path.join("test_files", "summary_list_score.test"), "r"
        ) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_summary_list_results_n(self):
        report = Summary()
        report.acquire()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.list_results(score="accuracy", number=3)
        computed = fake_out.getvalue()
        with open(os.path.join("test_files", "summary_list_n.test"), "r") as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_summary_list_hiden(self):
        report = Summary(hidden=True)
        report.acquire()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.list_results(score="accuracy")
        computed = fake_out.getvalue()
        with open(
            os.path.join("test_files", "summary_list_hidden.test"), "r"
        ) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_show_result_no_title(self):
        report = Summary()
        report.acquire()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            title = ""
            best = report.best_result(
                criterion="model", value="STree", score="accuracy"
            )
            report.show_result(data=best, title=title)
        computed = fake_out.getvalue()
        with open(
            os.path.join("test_files", "summary_show_results.test"), "r"
        ) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_show_result_title(self):
        report = Summary()
        report.acquire()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            title = "**Title**"
            best = report.best_result(
                criterion="model", value="STree", score="accuracy"
            )
            report.show_result(data=best, title=title)
        computed = fake_out.getvalue()
        with open(
            os.path.join("test_files", "summary_show_results_title.test"), "r"
        ) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_show_result_no_data(self):
        report = Summary()
        report.acquire()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            title = "**Test**"
            report.show_result(data={}, title=title)
        computed = fake_out.getvalue()
        expected = f"** **Test** has No data **\n"
        self.assertEqual(computed, expected)

    def test_best_results_datasets(self):
        report = Summary()
        report.acquire()
        computed = report.best_results_datasets()
        expected = {
            "balance-scale": (
                0.83616,
                {},
                "results_accuracy_RandomForest_iMac27_2022-01-14_12:39:30_0.json",
                "Test default paramters with RandomForest",
            ),
            "balloons": (
                0.5566666666666668,
                {"max_features": "auto", "splitter": "mutual"},
                "results_accuracy_STree_macbook-pro_2021-11-01_19:17:07_0.json",
                "default B",
            ),
        }
        self.assertSequenceEqual(computed, expected)
