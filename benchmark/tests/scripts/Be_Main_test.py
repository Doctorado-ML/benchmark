import os
from ...Utils import Folders
from ..TestBase import TestBase


class BeMainTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()
        self.score = "accuracy"

    def tearDown(self) -> None:
        files = []

        self.remove_files(files, Folders.exreport)
        return super().tearDown()

    def test_be_benchmark_dataset(self):
        stdout, _ = self.execute_script(
            "be_main",
            [
                "-s",
                self.score,
                "-m",
                "STree",
                "-d",
                "balloons",
                "--title",
                "test",
            ],
        )
        with open(os.path.join(self.test_files, "be_main_dataset.test")) as f:
            expected = f.read()
        n_line = 0
        # compare only report lines without date, time, duration...
        lines_to_compare = [0, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13]
        for expected, computed in zip(
            expected.splitlines(), stdout.getvalue().splitlines()
        ):
            if n_line in lines_to_compare:
                self.assertEqual(computed, expected, n_line)
            n_line += 1

    def test_be_benchmark_no_data(self):
        stdout, _ = self.execute_script(
            "be_main", ["-m", "STree", "-d", "unknown", "--title", "test"]
        )
        self.assertEqual(stdout.getvalue(), "Unknown dataset: unknown\n")
