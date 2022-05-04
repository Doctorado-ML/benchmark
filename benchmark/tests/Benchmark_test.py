import os
from io import StringIO
from unittest.mock import patch
from openpyxl import load_workbook
from .TestBase import TestBase
from ..Utils import Folders, Files
from ..Results import Benchmark


class BenchmarkTest(TestBase):
    def tearDown(self) -> None:
        benchmark = Benchmark("accuracy", visualize=False)
        files = [
            "exreport_accuracy.csv",
            "exreport_accuracy.txt",
            "exreport_accuracy.xlsx",
            "exreport_err_accuracy.txt",
            "exreport_err_unknown.txt",
            "exreport_unknown.csv",
            "exreport_unknown.txt",
            "Rplots.pdf",
            benchmark.get_tex_file(),
        ]
        self.remove_files(files, Folders.exreport)
        self.remove_files(files, ".")
        return super().tearDown()

    def test_csv(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        self.check_file_file(
            benchmark.get_result_file_name(), "exreport_csv.test"
        )

    def test_exreport_report(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch(self.output, new=StringIO()) as fake_out:
            benchmark.report(tex_output=False)
        self.check_output_file(fake_out, "exreport_report.test")

    def test_exreport(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch(self.output, new=StringIO()) as fake_out:
            benchmark.exreport()
        with open(os.path.join(self.test_files, "exreport.test")) as f:
            expected_t = f.read()
        computed_t = fake_out.getvalue()
        computed_t = computed_t.split("\n")
        computed_t.pop(0)
        for computed, expected in zip(computed_t, expected_t.split("\n")):
            self.assertEqual(computed, expected)

    def test_exreport_remove_previous(self):
        os.makedirs(Folders.report)
        with open(os.path.join(Files.exreport_pdf), "w") as f:
            print("x", file=f)
        self.assertTrue(os.path.exists(Files.exreport_pdf))
        self.assertTrue(os.path.exists(Folders.report))
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch(self.output, new=StringIO()):
            benchmark.exreport()
        self.assertFalse(os.path.exists(Files.exreport_pdf))
        self.assertFalse(os.path.exists(Folders.report))

    def test_exreport_error(self):
        benchmark = Benchmark("unknown", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch(self.output, new=StringIO()) as fake_out:
            benchmark.exreport()
        self.check_output_file(fake_out, "exreport_error.test")

    def test_tex_output(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch(self.output, new=StringIO()) as fake_out:
            benchmark.report(tex_output=True)
        with open(os.path.join(self.test_files, "exreport_report.test")) as f:
            expected = f.read()
        self.assertEqual(fake_out.getvalue(), expected)
        self.assertTrue(os.path.exists(benchmark.get_tex_file()))
        self.check_file_file(benchmark.get_tex_file(), "exreport_tex.test")

    def test_excel_output(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch(self.output, new=StringIO()):
            benchmark.exreport()
        benchmark.excel()
        file_name = benchmark.get_excel_file_name()
        book = load_workbook(file_name)
        for sheet_name in book.sheetnames:
            sheet = book[sheet_name]
            self.check_excel_sheet(sheet, f"exreport_excel_{sheet_name}.test")
            # ExcelTest.generate_excel_sheet(
            #     self, sheet, f"exreport_excel_{sheet_name}.test"
            # )
