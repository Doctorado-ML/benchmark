import os
from .TestBase import TestBase
from ..Results import SQL
from ..Utils import Folders


class SQLTest(TestBase):
    def tearDown(self) -> None:
        files = [
            "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.sql",
        ]
        self.remove_files(files, Folders.results)
        return super().tearDown()

    def test_report_SQL(self):
        file_name = "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json"
        report = SQL(file_name)
        report.report()
        file_name = os.path.join(
            Folders.results, file_name.replace(".json", ".sql")
        )
        self.check_file_file(file_name, "sql.test")
