import os
import json
from io import StringIO
from unittest.mock import patch
from ...Results import Report
from ...Utils import Files, Folders
from ..TestBase import TestBase


class BeMainTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()
        self.score = "accuracy"
        self.files = []

    def tearDown(self) -> None:
        self.remove_files(self.files, ".")
        return super().tearDown()

    def test_be_main_dataset(self):
        stdout, _ = self.execute_script(
            "be_main",
            ["-m", "STree", "-d", "balloons", "--title", "test"],
        )
        self.check_output_lines(
            stdout=stdout,
            file_name="be_main_dataset",
            lines_to_compare=[0, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14],
        )

    def test_be_main_complete(self):
        stdout, _ = self.execute_script(
            "be_main",
            ["-s", self.score, "-m", "STree", "--title", "test", "-r"],
        )
        # keep the report name to delete it after
        report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
        self.files.append(report_name)
        self.check_output_lines(
            stdout,
            "be_main_complete",
            [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14, 15],
        )

    def test_be_main_no_report(self):
        stdout, _ = self.execute_script(
            "be_main",
            ["-s", self.score, "-m", "STree", "--title", "test"],
        )
        # keep the report name to delete it after
        report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
        self.files.append(report_name)
        report = Report(file_name=report_name)
        with patch(self.output, new=StringIO()) as stdout:
            report.report()
        self.check_output_lines(
            stdout,
            "be_main_complete",
            [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14],
        )

    def test_be_main_best_params(self):
        stdout, _ = self.execute_script(
            "be_main",
            [
                "-s",
                self.score,
                "-m",
                "STree",
                "--title",
                "test",
                "-b",
                "-r",
            ],
        )
        # keep the report name to delete it after
        report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
        self.files.append(report_name)
        self.check_output_lines(
            stdout, "be_main_best", [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14]
        )

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    def test_be_main_incompatible_params(self, stdout, stderr):
        m1 = (
            "be_main: error: argument -b/--best_paramfile: not allowed with "
            "argument -p/--hyperparameters"
        )
        m2 = (
            "be_main: error: argument -g/--grid_paramfile: not allowed with "
            "argument -p/--hyperparameters"
        )
        m3 = (
            "be_main: error: argument -g/--grid_paramfile: not allowed with "
            "argument -p/--hyperparameters"
        )
        m4 = m1
        p0 = [
            "-s",
            self.score,
            "-m",
            "SVC",
            "--title",
            "test",
        ]
        pset = json.dumps(dict(C=17))
        p1 = p0.copy()
        p1.extend(["-p", pset, "-b"])
        p2 = p0.copy()
        p2.extend(["-p", pset, "-g"])
        p3 = p0.copy()
        p3.extend(["-p", pset, "-g", "-b"])
        p4 = p0.copy()
        p4.extend(["-b", "-g"])
        parameters = [(p1, m1), (p2, m2), (p3, m3), (p4, m4)]
        for parameter, message in parameters:
            with self.assertRaises(SystemExit) as msg:
                module = self.search_script("be_main")
                module.main(parameter)
            self.assertEqual(msg.exception.code, 2)
            self.assertEqual(stderr.getvalue(), "")
            self.assertRegexpMatches(stdout.getvalue(), message)

    def test_be_main_best_params_non_existent(self):
        model = "GBC"
        stdout, stderr = self.execute_script(
            "be_main",
            [
                "-s",
                self.score,
                "-m",
                model,
                "--title",
                "test",
                "-b",
                "-r",
            ],
        )
        self.assertEqual(stderr.getvalue(), "")
        file_name = os.path.join(
            Folders.results, Files.best_results(self.score, model)
        )
        self.assertEqual(
            stdout.getvalue(),
            f"{file_name} does not exist\n",
        )

    def test_be_main_grid_non_existent(self):
        model = "GBC"
        stdout, stderr = self.execute_script(
            "be_main",
            [
                "-s",
                self.score,
                "-m",
                model,
                "--title",
                "test",
                "-g",
                "-r",
            ],
        )
        self.assertEqual(stderr.getvalue(), "")
        file_name = os.path.join(
            Folders.results, Files.grid_output(self.score, model)
        )
        self.assertEqual(
            stdout.getvalue(),
            f"{file_name} does not exist\n",
        )

    def test_be_main_grid_params(self):
        stdout, _ = self.execute_script(
            "be_main",
            [
                "-s",
                self.score,
                "-m",
                "STree",
                "--title",
                "test",
                "-g",
                "-r",
            ],
        )
        # keep the report name to delete it after
        report_name = stdout.getvalue().splitlines()[-1].split("in ")[1]
        self.files.append(report_name)
        self.check_output_lines(
            stdout, "be_main_grid", [0, 2, 3, 5, 6, 7, 8, 9, 12, 13, 14]
        )

    def test_be_main_no_data(self):
        stdout, _ = self.execute_script(
            "be_main", ["-m", "STree", "-d", "unknown", "--title", "test"]
        )
        self.assertEqual(stdout.getvalue(), "Unknown dataset: unknown\n")
