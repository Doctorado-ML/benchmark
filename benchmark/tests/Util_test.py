import os
import sys
import argparse
from .TestBase import TestBase
from ..Utils import Folders, Files, Symbols, TextColor
from ..Arguments import EnvData, EnvDefault


class UtilTest(TestBase):
    def test_Folders(self):
        self.assertEqual("results", Folders.results)
        self.assertEqual("hidden_results", Folders.hidden_results)
        self.assertEqual("exreport", Folders.exreport)
        self.assertEqual("excel", Folders.excel)
        self.assertEqual("img", Folders.img)
        self.assertEqual(
            os.path.join(Folders.exreport, "exreport_output"), Folders.report
        )
        self.assertTrue(
            Folders.src().endswith("benchmark/benchmark"), "Folders.src()"
        )

    def test_Files_attributes(self):
        self.assertEqual(Files.index, "all.txt", "Files.index")

        self.assertEqual(Files.report_ext, ".json", "Files.report_ext")
        self.assertEqual(
            Files.cmd_open_macos, "/usr/bin/open", "Files.cmd_open_macos"
        )

        self.assertEqual(
            Files.cmd_open_linux, "/usr/bin/xdg-open", "Files.cmd_open_linux"
        )
        self.assertEqual(
            Files.exreport_pdf, "Rplots.pdf", "Files.exreport_pdf"
        )

        self.assertEqual(Files.benchmark_r, "benchmark.r", "Files.benchmark_r")
        self.assertEqual(Files.dot_env, ".env", "Files.dot_env")

    def test_Files_methods(self):
        items = [
            "score_test",
            "model-test",
            "platform-test",
            "date-test",
            "time-test",
            "stratified-test",
        ]
        tests = [
            (Files.exreport_output("score_test"), "exreport_score-test.txt"),
            (Files.exreport_err("score_test"), "exreport_err_score-test.txt"),
            (Files.exreport_excel("score_test"), "exreport_score-test.xlsx"),
            (Files.exreport("score_test"), "exreport_score-test.csv"),
            (Files.tex_output("score_test"), "exreport_score-test.tex"),
            (
                Files.best_results("score_test", "model_test"),
                "best_results_score-test_model_test.json",
            ),
            (
                Files.results(*items),
                "results_score-test_model-test_platform-test_date-test_time-"
                "test_stratified-test.json",
            ),
            (
                Files.grid_input("score_test", "model_test"),
                "grid_input_score-test_model_test.json",
            ),
            (
                Files.grid_output("score_test", "model_test"),
                "grid_output_score-test_model_test.json",
            ),
            (
                Files.grid("input", "score_test", "model_test"),
                "grid_input_score-test_model_test.json",
            ),
            (
                Files.grid("output", "score_test", "model_test"),
                "grid_output_score-test_model_test.json",
            ),
        ]
        for computed, expected in tests:
            self.assertEqual(computed, expected)
        file_name = (
            "results_score-test_model-test_platform-test_date-test_time-"
            "test_stratified-test.json"
        )
        # split_file_name
        expected = items
        expected[0] = "score-test"
        self.assertSequenceEqual(Files().split_file_name(file_name), expected)
        # result_suffixes
        self.assertSequenceEqual(
            Files.results_suffixes(), ["results_", Files.report_ext]
        )
        self.assertSequenceEqual(
            Files.results_suffixes("score-test"),
            ["results_score-test_", Files.report_ext],
        )
        self.assertSequenceEqual(
            Files.results_suffixes("score-test", "model-test"),
            ["results_score-test_model-test_", Files.report_ext],
        )
        # is_exe
        self.assertTrue(Files.is_exe(sys.executable))

    def test_Files_open(self):
        self.assertIsNone(Files.open("xxx.xxx"))
        command = (
            Files.cmd_open_macos
            if Files.is_exe(Files.cmd_open_macos)
            else Files.cmd_open_linux
        )
        self.assertSequenceEqual(
            Files.open(__file__, test=True), [command, __file__]
        )

    def test_Files_get_results(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.assertCountEqual(
            Files().get_all_results(hidden=False),
            [
                "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0.json",
                "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json",
                "results_accuracy_STree_macbook-pro_2021-11-01_19:17:07_0."
                "json",
                "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0.json",
                "results_accuracy_RandomForest_iMac27_2022-01-14_12:39:30_0."
                "json",
            ],
        )
        self.assertCountEqual(
            Files().get_all_results(hidden=True),
            [
                "results_accuracy_STree_iMac27_2021-11-01_23:55:16_0.json",
                "results_accuracy_XGBoost_MacBookpro16_2022-05-04_11:00:35_"
                "0.json",
            ],
        )

    def test_Files_get_results_Error(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        # check with results
        os.rename(Folders.results, f"{Folders.results}.test")
        try:
            Files().get_all_results(hidden=False)
        except ValueError:
            pass
        else:
            self.fail("Files.get_all_results() should raise ValueError")
        finally:
            os.rename(f"{Folders.results}.test", Folders.results)
        # check with hidden_results
        os.rename(Folders.hidden_results, f"{Folders.hidden_results}.test")
        try:
            Files().get_all_results(hidden=True)
        except ValueError:
            pass
        else:
            self.fail("Files.get_all_results() should raise ValueError")
        finally:
            os.rename(f"{Folders.hidden_results}.test", Folders.hidden_results)

    def test_Symbols(self):
        self.assertEqual(Symbols.check_mark, "\N{heavy check mark}")

        self.assertEqual(
            Symbols.exclamation, "\N{heavy exclamation mark symbol}"
        )
        self.assertEqual(Symbols.black_star, "\N{black star}")
        self.assertEqual(Symbols.equal_best, Symbols.check_mark)
        self.assertEqual(Symbols.better_best, Symbols.black_star)

    def test_EnvData(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        expected = {
            "score": "accuracy",
            "platform": "iMac27",
            "n_folds": "5",
            "model": "ODTE",
            "stratified": "0",
            "source_data": "Tanveer",
            "seeds": "[57, 31, 1714, 17, 23, 79, 83, 97, 7, 1]",
            "discretize": "0",
            "nodes": "Nodes",
            "leaves": "Leaves",
            "depth": "Depth",
            "fit_features": "0",
        }
        computed = EnvData().load()
        self.assertDictEqual(computed, expected)

    def test_EnvDefault(self):
        expected = {
            "score": "accuracy",
            "platform": "iMac27",
            "n_folds": 5,
            "model": "STree",
            "stratified": "0",
        }
        ap = argparse.ArgumentParser()
        ap.add_argument(
            "-s",
            "--score",
            action=EnvDefault,
            envvar="score",
            type=str,
            required=True,
            help="score name {accuracy, f1_macro, ...}",
        )
        ap.add_argument(
            "-P",
            "--platform",
            action=EnvDefault,
            envvar="platform",
            type=str,
            required=True,
            help="Platform where the test is run",
        )
        ap.add_argument(
            "-m",
            "--model",
            action=EnvDefault,
            envvar="model",
            type=str,
            required=True,
            help="model name",
        )
        ap.add_argument(
            "-n",
            "--n_folds",
            action=EnvDefault,
            envvar="n_folds",
            type=int,
            required=True,
            help="number of folds",
        )
        ap.add_argument(
            "-t",
            "--stratified",
            action=EnvDefault,
            envvar="stratified",
            type=str,
            required=True,
            help="Stratified",
        )
        ap.add_argument(
            "--title",
            type=str,
            required=True,
        )
        ap.add_argument(
            "-r",
            "--report",
            type=bool,
            required=False,
            help="Generate Report",
        )
        args = ap.parse_args(
            ["--title", "test", "-m", "STree"],
        )
        computed = args.__dict__
        for key, value in expected.items():
            self.assertEqual(computed[key], value)

    def test_TextColor(self):
        self.assertEqual(TextColor.BLUE, "\033[94m")
        self.assertEqual(TextColor.CYAN, "\033[96m")
        self.assertEqual(TextColor.GREEN, "\033[92m")
        self.assertEqual(TextColor.MAGENTA, "\033[95m")
        self.assertEqual(TextColor.YELLOW, "\033[93m")
        self.assertEqual(TextColor.RED, "\033[91m")
        self.assertEqual(TextColor.HEADER, TextColor.MAGENTA)
        self.assertEqual(TextColor.LINE1, TextColor.BLUE)
        self.assertEqual(TextColor.LINE2, TextColor.CYAN)
        self.assertEqual(TextColor.SUCCESS, TextColor.GREEN)
        self.assertEqual(TextColor.WARNING, TextColor.YELLOW)
        self.assertEqual(TextColor.FAIL, TextColor.RED)
        self.assertEqual(TextColor.ENDC, "\033[0m")
        self.assertEqual(TextColor.BOLD, "\033[1m")
        self.assertEqual(TextColor.UNDERLINE, "\033[4m")
