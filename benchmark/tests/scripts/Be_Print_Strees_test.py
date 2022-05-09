import os
import hashlib
from ...Utils import Folders
from ..TestBase import TestBase


class BePrintStrees(TestBase):
    def setUp(self):
        self.prepare_scripts_env()
        self.score = "accuracy"
        self.files = []
        self.datasets = ["balloons", "balance-scale"]
        self.expected = {
            "balloons": {
                "color": "b2342cc27a4ab495970616346bedf73b",
                "gray": "a9bc4d2041f2869a93164a548f6ad986",
            },
            "balance-scale": {
                "color": "2e85d66de1ae838d01a3f327397a50c8",
                "gray": "30f325134d4b5153c9e6ecbcae7b6d1f",
            },
        }

    def tearDown(self) -> None:
        self.remove_files(self.files, ".")
        return super().tearDown()

    def hash_file(self, name):
        file_name = os.path.join(Folders.img, f"{name}.png")
        self.files.append(file_name)
        self.assertTrue(os.path.exists(file_name))
        with open(file_name, "rb") as f:
            return hashlib.md5(f.read()).hexdigest(), file_name

    def test_be_print_strees_dataset_bn(self):
        for name in self.datasets:
            stdout, _ = self.execute_script(
                "be_print_strees",
                ["-d", name, "-q", "1"],
            )
            computed_hash, file_name = self.hash_file(f"stree_{name}")
            self.assertEqual(
                stdout.getvalue(), f"File {file_name} generated\n"
            )
            self.assertEqual(computed_hash, self.expected[name]["gray"])

    def test_be_print_strees_dataset_color(self):
        for name in self.datasets:
            stdout, _ = self.execute_script(
                "be_print_strees",
                ["-d", name, "-q", "1", "-c", "1"],
            )
            computed_hash, file_name = self.hash_file(f"stree_{name}")
            self.assertEqual(
                stdout.getvalue(), f"File {file_name} generated\n"
            )
            self.assertEqual(computed_hash, self.expected[name]["color"])
