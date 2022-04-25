import os
import unittest
from ..Results import SQL
from ..Utils import Folders


class SQLTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

    def tearDown(self) -> None:
        files = [
            "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.sql",
        ]
        for file_name in files:
            file_name = os.path.join(Folders.results, file_name)
            if os.path.exists(file_name):
                os.remove(file_name)
        return super().tearDown()

    def test_report_SQL(self):
        file_name = "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json"
        report = SQL(file_name)
        report.report()
        file_name = os.path.join(
            Folders.results, file_name.replace(".json", ".sql")
        )

        with open(file_name, "r") as file:
            computed = file.read()
            with open(os.path.join("test_files", "sql.test")) as f_exp:
                expected = f_exp.read()
        self.assertEqual(computed, expected)
