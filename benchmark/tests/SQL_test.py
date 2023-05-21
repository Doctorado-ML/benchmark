import os
from .TestBase import TestBase
from ..ResultsFiles import SQLFile
from ..Utils import Folders, Files


class SQLTest(TestBase):
    def tearDown(self) -> None:
        files = [
            "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.sql",
        ]
        self.remove_files(files, Folders.sql)
        return super().tearDown()

    def test_report_SQL(self):
        file_name = "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json"
        report = SQLFile(file_name)
        report.report()
        file_name = os.path.join(
            Folders.sql, file_name.replace(Files.report_ext, ".sql")
        )
        self.check_file_file(file_name, "sql")
