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
                "color": "107a73552a9ad66dee34a825d613a792",
                "gray": "d2a1746459298e9a625f8c96264a6841",
            },
            "balance-scale": {
                "color": "0ba25cfe6a64d01187dfd3106b0cea7a",
                "gray": "ce51aa4680e73af44b93ca717621d728",
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
