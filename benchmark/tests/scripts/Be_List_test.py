import os
from ...Utils import Folders
from ..TestBase import TestBase


class BeListTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def test_be_list(self):
        stdout, stderr = self.execute_script("be_list", ["-m", "STree"])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "summary_list_model")

    def test_be_list_no_data(self):
        stdout, stderr = self.execute_script(
            "be_list", ["-m", "Wodt", "-s", "f1-macro"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "** No results found **\n")

    def test_be_list_nan(self):
        def swap_files(source_folder, target_folder, file_name):
            source = os.path.join(source_folder, file_name)
            target = os.path.join(target_folder, file_name)
            os.rename(source, target)

        # move nan result from hidden to results
        file_name = (
            "results_accuracy_XGBoost_MacBookpro16_2022-05-04_11:00:"
            "35_0.json"
        )
        swap_files(Folders.hidden_results, Folders.results, file_name)
        try:
            stdout, stderr = self.execute_script("be_list", ["--nan", "1"])
            self.assertEqual(stderr.getvalue(), "")
            self.check_output_file(stdout, "be_list_nan")
        except Exception:
            # move back nan result file
            swap_files(Folders.results, Folders.hidden_results, file_name)
            self.fail("test_be_list_nan() should not raise exception")

    def test_be_list_nan_no_nan(self):
        stdout, stderr = self.execute_script("be_list", ["--nan", "1"])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "be_list_no_nan")
