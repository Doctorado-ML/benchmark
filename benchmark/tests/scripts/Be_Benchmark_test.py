import os
import json
from ...Utils import Folders, Files
from ..TestBase import TestBase


class BeBenchmarkTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self) -> None:
        files = []
        for score in ["accuracy", "unknown"]:
            files.append(Files.exreport(score))
            files.append(Files.exreport_output(score))
            files.append(Files.exreport_err(score))

        files.append(Files.exreport_excel("accuracy"))
        files.append(Files.exreport_pdf)
        files.append(Files.tex_output("accuracy"))
        self.remove_files(files, Folders.exreport)
        self.remove_files(files, ".")
        return super().tearDown()

    def test_be_benchmark(self):
        stdout, stderr = self.execute_script(
            "be_benchmark", ["-s", "accuracy", "-q", "1", "-t", "1", "-x", "1"]
        )
        self.assertEqual(stderr.getvalue(), "")
        # Check output
        self.check_output_file(stdout, "exreport_report")
        # Check csv file
        file_name = os.path.join(Folders.exreport, Files.exreport("accuracy"))
        self.check_file_file(file_name, "exreport_csv")
        # Check tex file
        # Check excel file
