import os
import unittest
import shutil
from io import StringIO
from unittest.mock import patch
from openpyxl import load_workbook
from ..Utils import Folders, Files
from ..Results import Benchmark
from .Excel_test import ExcelTest


class BenchmarkTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

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
        for file_name in files:
            if os.path.exists(file_name):
                os.remove(file_name)
            file_name = os.path.join(Folders.exreport, file_name)
            if os.path.exists(file_name):
                os.remove(file_name)
        if os.path.exists(Folders.report):
            shutil.rmtree(Folders.report)
        return super().tearDown()

    def test_csv(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with open(benchmark.get_result_file_name()) as f:
            computed = f.readlines()
        with open(os.path.join("test_files", "exreport_csv.test")) as f_exp:
            expected = f_exp.readlines()
        self.assertEqual(computed, expected)

    def test_exreport_report(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            benchmark.report(tex_output=False)
        with open(os.path.join("test_files", "exreport_report.test")) as f:
            expected = f.read()
        self.assertEqual(fake_out.getvalue(), expected)

    def test_exreport(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            benchmark.exreport()
        with open(os.path.join("test_files", "exreport.test")) as f:
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
        with patch("sys.stdout", new=StringIO()) as fake_out:
            benchmark.exreport()
        self.assertFalse(os.path.exists(Files.exreport_pdf))
        self.assertFalse(os.path.exists(Folders.report))

    def test_exreport_error(self):
        benchmark = Benchmark("unknown", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            benchmark.exreport()
        computed = fake_out.getvalue()
        with open(os.path.join("test_files", "exreport_error.test")) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_tex_output(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            benchmark.report(tex_output=True)
        with open(os.path.join("test_files", "exreport_report.test")) as f:
            expected = f.read()
        self.assertEqual(fake_out.getvalue(), expected)
        self.assertTrue(os.path.exists(benchmark.get_tex_file()))
        with open(benchmark.get_tex_file()) as f:
            computed = f.read()
        with open(os.path.join("test_files", "exreport_tex.test")) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def test_excel_output(self):
        benchmark = Benchmark("accuracy", visualize=False)
        benchmark.compile_results()
        benchmark.save_results()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            benchmark.exreport()
        benchmark.excel()
        file_name = benchmark.get_excel_file_name()
        book = load_workbook(file_name)
        for sheet_name in book.sheetnames:
            sheet = book[sheet_name]
            ExcelTest.check_excel_sheet(
                self, sheet, f"exreport_excel_{sheet_name}.test"
            )
            # ExcelTest.generate_excel_sheet(
            #     self, sheet, f"exreport_excel_{sheet_name}.test"
            # )
