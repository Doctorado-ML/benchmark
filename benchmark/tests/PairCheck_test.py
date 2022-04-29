import os
from io import StringIO
from unittest.mock import patch
from .TestBase import TestBase
from ..Results import PairCheck


class PairCheckTest(TestBase):
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
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        computed = fake_out.getvalue()
        with open(os.path.join(self.test_files, "paircheck.test"), "r") as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_pair_check_win(self):
        report = self.build_model(win=True)
        report.compute()
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "paircheck_win.test")

    def test_pair_check_lose(self):
        report = self.build_model(
            model1="RandomForest", model2="STree", lose=True
        )
        report.compute()
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "paircheck_lose.test")

    def test_pair_check_win_lose(self):
        report = self.build_model(win=True, lose=True)
        report.compute()
        with patch(self.output, new=StringIO()) as fake_out:
            report.report()
        self.check_output_file(fake_out, "paircheck_win_lose.test")

    def test_pair_check_store_result(self):
        report = self.build_model(win=True, lose=True)
        report.compute()
        report._store_result(0, "balloons")
        report._store_result(-1, "balance-scale")
        self.assertListEqual(report.winners, ["balance-scale", "balloons"])
        self.assertListEqual(report.losers, ["balance-scale"])
        self.assertListEqual(report.tie, ["balloons"])
