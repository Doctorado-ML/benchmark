import os
import json
from ...Utils import Folders, Files
from ..TestBase import TestBase


class BeBenchmarkTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self) -> None:
        # self.remove_files(
        #     [Files.best_results("accuracy", "ODTE")],
        #     Folders.results,
        # )
        return super().tearDown()

    def test_be_benchmark(self):
        # stdout, stderr = self.execute_script(
        #     "be_benchmark", ["-s", "accuracy"]
        # )
        # self.assertEqual(stderr.getvalue(), "")
        # self.check_output_file(stdout, "be_best_all")
        pass
