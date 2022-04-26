import os
import unittest
from io import StringIO
from unittest.mock import patch
from ..Results import PairCheck


class PairCheckTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

    def build_model(
        self,
        score="accuracy",
        model1="STree",
        model2="RandomForest",
        win=False,
        lose=False,
    ):
        return PairCheck(score, model1, model2, win, lose)

    def test_pair_check(self):
        report = self.build_model(model1="ODTE", model2="STree")
        report.compute()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
        computed = fake_out.getvalue()
        with open(os.path.join("test_files", "PairCheck.test"), "r") as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_pair_check_win(self):
        report = self.build_model(win=True)
        report.compute()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
        computed = fake_out.getvalue()
        with open(os.path.join("test_files", "PairCheck_win.test"), "r") as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_pair_check_lose(self):
        report = self.build_model(
            model1="RandomForest", model2="STree", lose=True
        )
        report.compute()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
        computed = fake_out.getvalue()
        with open(os.path.join("test_files", "PairCheck_lose.test"), "r") as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_pair_check_win_lose(self):
        report = self.build_model(win=True, lose=True)
        report.compute()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            report.report()
        computed = fake_out.getvalue()
        with open(
            os.path.join("test_files", "PairCheck_win_lose.test"), "r"
        ) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_pair_check_store_result(self):
        report = self.build_model(win=True, lose=True)
        report.compute()
        report._store_result(0, "balloons")
        report._store_result(1, "balloons")
        report._store_result(-1, "balloons")
