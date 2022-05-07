import os
from ...Utils import Folders
from ..TestBase import TestBase


class BeGridTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self) -> None:
        self.remove_files(["grid_input_f1-macro_STree.json"], Folders.results)
        return super().tearDown()

    def test_be_build_grid(self):
        stdout, stderr = self.execute_script(
            "be_build_grid", ["-m", "STree", "-s", "f1-macro"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(
            stdout.getvalue(),
            "Generated grid input file to results/grid_input_f1-macro_STree."
            "json\n",
        )
        name = File.grid_input("f1-macro", "STree")
        file_name = os.path.join(Folders.results, name)
        self.check_file_file(file_name, "be_build_grid")

    def test_be_grid_(self):
        stdout, stderr = self.execute_script(
            "be_grid",
            ["-m", "STree", "-s", "accuracy", "--n_folds", 2, "-q", "1"],
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "")
        name = File.grid_output("accuracy", "STree")
        file_name = os.path.join(Folders.results, name)
        self.check_file_file(file_name, "be_grid")
