import os
from ..TestBase import TestBase


class BeReportTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def test_be_report(self):
        file_name = os.path.join(
            "results",
            "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json",
        )
        stdout, stderr = self.execute_script("be_report", ["-f", file_name])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report")

    def test_be_report_compare(self):
        file_name = "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json"
        stdout, stderr = self.execute_script(
            "be_report",
            ["-f", file_name, "-c", "1"],
        )
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report_compared")
