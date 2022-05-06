from ..TestBase import TestBase


class ListTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def test_be_list(self):
        stdout, stderr = self.execute_script("be_list", ["-m", "STree"])
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "summary_list_model.test")

    def test_be_list_no_data(self):
        stdout, stderr = self.execute_script(
            "be_list", ["-m", "Wodt", "-s", "f1-macro"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "** No results found **\n")

    def test_be_list_nan(self):
        pass
