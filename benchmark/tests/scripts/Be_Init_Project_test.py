import os
from io import StringIO
from unittest.mock import patch
from ..TestBase import TestBase
from ...Utils import Folders


class BeInitProjectTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def tearDown(self):
        if os.path.exists("test_project"):
            os.system("rm -rf test_project")

    def assertIsFile(self, file_name):
        if not os.path.isfile(file_name):
            raise AssertionError(f"File {str(file_name)} does not exist")

    def assertIsFolder(self, path):
        if not os.path.exists(path):
            raise AssertionError(f"Folder {str(path)} does not exist")

    def test_be_init_project(self):
        test_project = "test_project"
        stdout, stderr = self.execute_script("be_init_project", [test_project])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "be_init_project")
        # check folders
        expected = [
            Folders.results,
            Folders.hidden_results,
            Folders.exreport,
            Folders.report,
            Folders.img,
        ]
        for folder in expected:
            self.assertIsFolder(os.path.join(test_project, folder))
        self.assertIsFile(os.path.join(test_project, ".env"))
        os.system(f"rm -rf {test_project}")

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    def test_be_init_project_no_arguments(self, stdout, stderr):
        with self.assertRaises(SystemExit) as cm:
            module = self.search_script("be_init_project")
            module.main("")
        self.assertEqual(cm.exception.code, 2)
        self.check_output_file(stdout, "be_init_project_no_arguments")
        self.assertEqual(stderr.getvalue(), "")

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    def test_be_init_project_twice(self, stdout, stderr):
        test_project = "test_project"
        self.execute_script("be_init_project", [test_project])
        with self.assertRaises(SystemExit) as cm:
            module = self.search_script("be_init_project")
            module.main([test_project])
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(
            stderr.getvalue(),
            f"Creating folder {test_project}\n"
            f"[Errno 17] File exists: '{test_project}'\n",
        )
        self.assertEqual(stdout.getvalue(), "")
