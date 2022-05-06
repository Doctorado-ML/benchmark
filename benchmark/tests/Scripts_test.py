import os
import sys
import glob
import pathlib
from importlib import import_module
from io import StringIO
from unittest.mock import patch
from .TestBase import TestBase


class ScriptsTest(TestBase):
    def setUp(self):
        self.scripts_folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "scripts"
        )
        sys.path.append(self.scripts_folder)

    def search_script(self, name):
        py_files = glob.glob(os.path.join(self.scripts_folder, "*.py"))
        for py_file in py_files:
            module_name = pathlib.Path(py_file).stem
            if name == module_name:
                module = import_module(module_name)
                return module

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    def execute_script(self, script, args, stderr, stdout):
        module = self.search_script(script)
        module.main(args)
        return stdout, stderr

    def test_be_pair_check(self):
        stdout, stderr = self.execute_script(
            "be_pair_check", ["-m1", "ODTE", "-m2", "STree"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "paircheck.test")

    def test_be_pair_check_no_data_a(self):
        stdout, stderr = self.execute_script(
            "be_pair_check", ["-m1", "SVC", "-m2", "ODTE"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "** No results found **\n")

    def test_be_pair_check_no_data_b(self):
        stdout, stderr = self.execute_script(
            "be_pair_check", ["-m1", "STree", "-m2", "SVC"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "** No results found **\n")
