import os
import glob
import pathlib
import sys
import csv
import unittest
from importlib import import_module
from io import StringIO
from unittest.mock import patch


class TestBase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.test_files = "test_files"
        self.output = "sys.stdout"
        super().__init__(*args, **kwargs)

    def remove_files(self, files, folder):
        for file_name in files:
            file_name = os.path.join(folder, file_name)
            if os.path.exists(file_name):
                os.remove(file_name)

    def generate_excel_sheet(self, sheet, file_name):
        with open(os.path.join(self.test_files, file_name), "w") as f:
            for row in range(1, sheet.max_row + 1):
                for col in range(1, sheet.max_column + 1):
                    value = sheet.cell(row=row, column=col).value
                    if value is not None:
                        print(f'{row};{col};"{value}"', file=f)

    def check_excel_sheet(self, sheet, file_name):
        file_name += ".test"
        with open(os.path.join(self.test_files, file_name), "r") as f:
            expected = csv.reader(f, delimiter=";")
            for row, col, value in expected:
                if value.isdigit():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                self.assertEqual(sheet.cell(int(row), int(col)).value, value)

    def check_output_file(self, output, file_name):
        file_name += ".test"
        with open(os.path.join(self.test_files, file_name)) as f:
            expected = f.read()
        self.assertEqual(output.getvalue(), expected)

    def check_file_file(self, computed_file, expected_file):
        with open(computed_file) as f:
            computed = f.read()
        expected_file += ".test"
        with open(os.path.join(self.test_files, expected_file)) as f:
            expected = f.read()
        self.assertEqual(computed, expected)

    def prepare_scripts_env(self):
        self.scripts_folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "scripts"
        )
        sys.path.append(self.scripts_folder)

    def search_script(self, name):
        py_files = glob.glob(os.path.join(self.scripts_folder, "*.py"))
        for py_file in py_files:
            module_name = pathlib.Path(py_file).stem
            if name == module_name:
                module = import_module(module_name)
                return module

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    def execute_script(self, script, args, stderr, stdout):
        module = self.search_script(script)
        module.main(args)
        return stdout, stderr
