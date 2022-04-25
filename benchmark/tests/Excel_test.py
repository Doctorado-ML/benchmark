import os
import csv
import unittest
from openpyxl import load_workbook
from xlsxwriter import Workbook
from ..Results import Excel
from ..Utils import Folders


class ExcelTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

    def tearDown(self) -> None:
        files = [
            "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.xlsx",
            "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0.xlsx",
            "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.xlsx",
        ]
        for file_name in files:
            file_name = os.path.join(Folders.results, file_name)
            if os.path.exists(file_name):
                os.remove(file_name)
        return super().tearDown()

    @staticmethod
    def generate_excel_sheet(test, sheet, file_name):
        with open(os.path.join("test_files", file_name), "w") as f:
            for row in range(1, sheet.max_row + 1):
                for col in range(1, sheet.max_column + 1):
                    value = sheet.cell(row=row, column=col).value
                    if value is not None:
                        print(f'{row};{col};"{value}"', file=f)

    @staticmethod
    def check_excel_sheet(test, sheet, file_name):
        with open(os.path.join("test_files", file_name), "r") as f:
            expected = csv.reader(f, delimiter=";")
            for row, col, value in expected:
                if value.isdigit():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                test.assertEqual(sheet.cell(int(row), int(col)).value, value)

    def test_report_excel_compared(self):
        file_name = "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json"
        report = Excel(file_name, compare=True)
        report.report()
        file_output = report.get_file_name()
        book = load_workbook(file_output)
        sheet = book["STree"]
        self.check_excel_sheet(self, sheet, "excel_compared.test")

    def test_report_excel(self):
        file_name = "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json"
        report = Excel(file_name, compare=False)
        report.report()
        file_output = report.get_file_name()
        book = load_workbook(file_output)
        sheet = book["STree"]
        self.check_excel_sheet(self, sheet, "excel.test")

    def test_Excel_Add_sheet(self):
        file_name = "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0.json"
        excel_file_name = file_name.replace(".json", ".xlsx")
        book = Workbook(os.path.join(Folders.results, excel_file_name))
        excel = Excel(file_name=file_name, book=book)
        excel.report()
        report = Excel(
            file_name="results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json",
            book=book,
        )
        report.report()
        book.close()
        book = load_workbook(os.path.join(Folders.results, excel_file_name))
        sheet = book["STree"]
        self.check_excel_sheet(self, sheet, "excel_add_STree.test")
        sheet = book["ODTE"]
        self.check_excel_sheet(self, sheet, "excel_add_ODTE.test")
