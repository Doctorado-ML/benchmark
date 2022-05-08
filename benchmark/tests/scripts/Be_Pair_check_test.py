from ..TestBase import TestBase
from ...Utils import NO_RESULTS


class BePairCheckTest(TestBase):
    def setUp(self):
        self.prepare_scripts_env()

    def test_be_pair_check(self):
        stdout, stderr = self.execute_script(
            "be_pair_check", ["-m1", "ODTE", "-m2", "STree"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.check_output_file(stdout, "paircheck")

    def test_be_pair_check_no_data_a(self):
        stdout, stderr = self.execute_script(
            "be_pair_check", ["-m1", "SVC", "-m2", "ODTE"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), f"{NO_RESULTS}\n")

    def test_be_pair_check_no_data_b(self):
        stdout, stderr = self.execute_script(
            "be_pair_check", ["-m1", "STree", "-m2", "SVC"]
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), f"{NO_RESULTS}\n")
