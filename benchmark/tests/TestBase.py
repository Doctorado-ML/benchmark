import os
import csv
import unittest


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
        with open(os.path.join(self.test_files, file_name)) as f:
            expected = f.read()
        self.assertEqual(output.getvalue(), expected)

    def check_file_file(self, computed_file, expected_file):
        with open(computed_file) as f:
            computed = f.read()
        with open(os.path.join(self.test_files, expected_file)) as f:
            expected = f.read()
        self.assertEqual(computed, expected)
