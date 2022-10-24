import os
from openpyxl import load_workbook
from ...Utils import Folders
from ..TestBase import TestBase


class BeReportTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self) -> None:
        files = [
            "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.sql",
            "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.xlsx",
        ]
        self.remove_files(files, Folders.results)
        return super().tearDown()

    def test_be_report(self):
        file_name = os.path.join(
            "results",
            "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json",
        )
        stdout, stderr = self.execute_script("be_report", ["-f", file_name])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report")

    def test_be_report_not_found(self):
        stdout, stderr = self.execute_script("be_report", ["-f", "unknown"])
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "unknown does not exists!\n")

    def test_be_report_compare(self):
        file_name = "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json"
        stdout, stderr = self.execute_script(
            "be_report", ["-f", file_name, "-c", "1"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report_compared")

    def test_be_report_datatsets(self):
        stdout, stderr = self.execute_script("be_report", [])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report_datasets")

    def test_be_report_best(self):
        stdout, stderr = self.execute_script(
            "be_report", ["-s", "accuracy", "-m", "STree", "-b", "1"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report_best")

    def test_be_report_grid(self):
        stdout, stderr = self.execute_script(
            "be_report", ["-s", "accuracy", "-m", "STree", "-g", "1"]
        )
        self.assertEqual(stderr.getvalue(), "")
        file_name = "report_grid.test"
        with open(os.path.join(self.test_files, file_name)) as f:
            expected = f.read().splitlines()
        output_text = stdout.getvalue().splitlines()
        # Compare replacing STree version
        for line, index in zip(expected, range(len(expected))):
            if "1.2.4" in line:
                # replace STree version
                line = self.replace_STree_version(line, output_text, index)
            self.assertEqual(line, output_text[index])

    def test_be_report_best_both(self):
        stdout, stderr = self.execute_script(
            "be_report",
            ["-s", "accuracy", "-m", "STree", "-b", "1", "-g", "1"],
        )
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report_best")

    def test_be_report_excel_compared(self):
        file_name = "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json"
        stdout, stderr = self.execute_script(
            "be_report",
            ["-f", file_name, "-x", "1", "-c", "1"],
        )
        file_name = os.path.join(
            Folders.results, file_name.replace(".json", ".xlsx")
        )
        book = load_workbook(file_name)
        sheet = book["STree"]
        self.check_excel_sheet(sheet, "excel_compared")
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report_compared")

    def test_be_report_excel(self):
        file_name = "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json"
        stdout, stderr = self.execute_script(
            "be_report",
            ["-f", file_name, "-x", "1"],
        )
        file_name = os.path.join(
            Folders.results, file_name.replace(".json", ".xlsx")
        )
        book = load_workbook(file_name)
        sheet = book["STree"]
        self.check_excel_sheet(sheet, "excel")
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "report")

    def test_be_report_sql(self):
        file_name = "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json"
        stdout, stderr = self.execute_script(
            "be_report",
            ["-f", file_name, "-q", "1"],
        )
        file_name = os.path.join(
            Folders.results, file_name.replace(".json", ".sql")
        )
        self.check_file_file(file_name, "sql")
        self.assertEqual(stderr.getvalue(), "")
