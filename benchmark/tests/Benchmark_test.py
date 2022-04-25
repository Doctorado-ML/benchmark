import os
import unittest
import shutil
from io import StringIO
from unittest.mock import patch
from ..Utils import Folders
from ..Results import Benchmark


class BenchmarkTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

    def tearDown(self) -> None:
        files = [
            # "exreport_accuracy.csv",
            "exreport_accuracy.txt",
            "exreport_err_accuracy.txt",
        ]
        for file_name in files:
            file_name = os.path.join(Folders.exreport, file_name)
            if os.path.exists(file_name):
                os.remove(file_name)
        if os.path.exists(Folders.report):
            shutil.rmtree(Folders.report)
        if os.path.exists("Rplots.pdf"):
            os.remove("Rplots.pdf")
        return super().tearDown()

    def test_csv(self):
        benchmark = Benchmark("accuracy")
        benchmark.compile_results()
        benchmark.save_results()
        with open(benchmark.get_result_file_name()) as f:
            computed = f.readlines()
        with open(os.path.join("test_files", "exreport_csv.test")) as f_exp:
            expected = f_exp.readlines()
        self.assertEqual(computed, expected)

    def test_exreport(self):
        benchmark = Benchmark("accuracy")
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
