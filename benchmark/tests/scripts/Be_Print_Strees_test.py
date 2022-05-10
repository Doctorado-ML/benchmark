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

    def tearDown(self) -> None:
        self.remove_files(self.files, ".")
        return super().tearDown()

    def test_be_print_strees_dataset_bn(self):
        for name in self.datasets:
            stdout, _ = self.execute_script(
                "be_print_strees",
                ["-d", name, "-q", "1"],
            )
            file_name = os.path.join(Folders.img, f"stree_{name}.png")
            self.files.append(file_name)
            self.assertTrue(os.path.exists(file_name))
            self.assertEqual(
                stdout.getvalue(), f"File {file_name} generated\n"
            )
            computed_size = os.path.getsize(file_name)
            self.assertGreater(computed_size, 25000)

    def test_be_print_strees_dataset_color(self):
        for name in self.datasets:
            stdout, _ = self.execute_script(
                "be_print_strees",
                ["-d", name, "-q", "1", "-c", "1"],
            )
            file_name = os.path.join(Folders.img, f"stree_{name}.png")
            self.files.append(file_name)
            self.assertEqual(
                stdout.getvalue(), f"File {file_name} generated\n"
            )
            computed_size = os.path.getsize(file_name)
            self.assertGreater(computed_size, 30000)
