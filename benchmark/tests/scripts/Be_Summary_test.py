import os
from openpyxl import load_workbook
from ...Utils import Folders
from ..TestBase import TestBase


class BeSummaryTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self) -> None:
        pass

    def test_be_summary_list_results_model(self):
        stdout, stderr = self.execute_script("be_summary", ["-m", "STree"])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "be_summary_list_model")

    def test_be_summary_list_results_score(self):
        stdout, stderr = self.execute_script("be_summary", ["-s", "accuracy"])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "be_summary_list_score")

    def test_be_summary_list_results_score_all(self):
        stdout, stderr = self.execute_script("be_summary", ["-s", "all"])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "be_summary_list_score_all")

    def test_summary_list_results_model_score(self):
        stdout, stderr = self.execute_script(
            "be_summary", ["-s", "accuracy", "-m", "ODTE"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "be_summary_list_score_model")
