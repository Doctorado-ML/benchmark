from io import StringIO
from unittest.mock import patch
from .TestBase import TestBase
from ..Results import Summary


class SummaryTest(TestBase):
    def test_summary_without_model(self):
        report = Summary()
        report.acquire()
        computed = report.best_results(score="accuracy")
        expected = [
            {
                "score": "accuracy",
                "model": "STree",
                "title": "With gridsearched hyperparameters",
                "platform": "iMac27",
                "date": "2021-09-30",
                "time": "11:42:07",
                "stratified": "0",
                "file": "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
                ".json",
                "metric": 0.04544339345094904,
                "duration": 624.2505249977112,
            },
            {
                "score": "accuracy",
                "model": "ODTE",
                "title": "Gridsearched hyperparams v022.1b random_init",
                "platform": "Galgo",
                "date": "2022-04-20",
                "time": "10:52:20",
                "stratified": "0",
                "file": "results_accuracy_ODTE_Galgo_2022-04-20_10:52:20_0."
                "json",
                "metric": 0.04340676203831255,
                "duration": 22591.471411943436,
            },
            {
                "score": "accuracy",
                "model": "STree",
                "title": "default A",
                "platform": "iMac27",
                "date": "2021-10-27",
                "time": "09:40:40",
                "stratified": "0",
                "file": "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0."
                "json",
                "metric": 0.04158163842230773,
                "duration": 3395.009148836136,
            },
            {
                "score": "accuracy",
                "model": "STree",
                "title": "default B",
                "platform": "macbook-pro",
                "date": "2021-11-01",
                "time": "19:17:07",
                "stratified": "0",
                "file": "results_accuracy_STree_macbook-pro_2021-11-01_19:17:"
                "07_0.json",
                "metric": 0.03789928437296904,
                "duration": 4115.042420864105,
            },
            {
                "score": "accuracy",
                "model": "RandomForest",
                "title": "Test default paramters with RandomForest",
                "platform": "iMac27",
                "date": "2022-01-14",
                "time": "12:39:30",
                "stratified": "0",
                "file": "results_accuracy_RandomForest_iMac27_2022-01-14_12:39"
                ":30_0.json",
                "metric": 0.03627309062515771,
                "duration": 272.7363500595093,
            },
        ]
        self.assertListEqual(computed, expected)

    def test_summary_with_model(self):
        report = Summary()
        report.acquire()
        computed = report.best_results(
            criterion="model", value="STree", score="accuracy"
        )
        expected = [
            {
                "score": "accuracy",
                "model": "STree",
                "title": "With gridsearched hyperparameters",
                "platform": "iMac27",
                "date": "2021-09-30",
                "time": "11:42:07",
                "stratified": "0",
                "file": "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0"
                ".json",
                "metric": 0.04544339345094904,
                "duration": 624.2505249977112,
            },
            {
                "score": "accuracy",
                "model": "STree",
                "title": "default A",
                "platform": "iMac27",
                "date": "2021-10-27",
                "time": "09:40:40",
                "stratified": "0",
                "file": "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0"
                ".json",
                "metric": 0.04158163842230773,
                "duration": 3395.009148836136,
            },
            {
                "score": "accuracy",
                "model": "STree",
                "title": "default B",
                "platform": "macbook-pro",
                "date": "2021-11-01",
                "time": "19:17:07",
                "stratified": "0",
                "file": "results_accuracy_STree_macbook-pro_2021-11-01_19:17:"
                "07_0.json",
                "metric": 0.03789928437296904,
                "duration": 4115.042420864105,
            },
        ]
        self.assertListEqual(computed, expected)

    def test_summary_list_results_model(self):
        report = Summary()
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            report.list_results(model="STree")
        self.check_output_file(fake_out, "summary_list_model.test")

    def test_summary_list_results_score(self):
        report = Summary()
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            report.list_results(score="accuracy")
        self.check_output_file(fake_out, "summary_list_score.test")

    def test_summary_list_results_n(self):
        report = Summary()
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            report.list_results(score="accuracy", number=3)
        self.check_output_file(fake_out, "summary_list_n.test")

    def test_summary_list_hidden(self):
        report = Summary(hidden=True)
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            report.list_results(score="accuracy")
        self.check_output_file(fake_out, "summary_list_hidden.test")

    def test_show_result_no_title(self):
        report = Summary()
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            title = ""
            best = report.best_result(
                criterion="model", value="STree", score="accuracy"
            )
            report.show_result(data=best, title=title)
        self.check_output_file(fake_out, "summary_show_results.test")

    def test_show_result_title(self):
        report = Summary()
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            title = "**Title**"
            best = report.best_result(
                criterion="model", value="STree", score="accuracy"
            )
            report.show_result(data=best, title=title)
        self.check_output_file(fake_out, "summary_show_results_title.test")

    def test_show_result_no_data(self):
        report = Summary()
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            title = "**Test**"
            report.show_result(data={}, title=title)
        computed = fake_out.getvalue()
        expected = "** **Test** has No data **\n"
        self.assertEqual(computed, expected)

    def test_best_results_datasets(self):
        report = Summary()
        report.acquire()
        computed = report.best_results_datasets()
        expected = {
            "balance-scale": (
                0.83616,
                {},
                "results_accuracy_RandomForest_iMac27_2022-01-14_12:39:30_0."
                "json",
                "Test default paramters with RandomForest",
            ),
            "balloons": (
                0.5566666666666668,
                {"max_features": "auto", "splitter": "mutual"},
                "results_accuracy_STree_macbook-pro_2021-11-01_19:17:07_0."
                "json",
                "default B",
            ),
        }
        self.assertSequenceEqual(computed, expected)

    def test_show_top(self):
        report = Summary()
        report.acquire()
        with patch(self.output, new=StringIO()) as fake_out:
            report.show_top()
        self.check_output_file(fake_out, "summary_show_top.test")

    @patch("sys.stdout", new_callable=StringIO)
    def test_show_top_no_data(self, fake_out):
        report = Summary()
        report.acquire()
        report.show_top(score="f1-macro")
        self.assertEqual(fake_out.getvalue(), "** No results found **\n")

    def test_no_data(self):
        report = Summary()
        report.acquire()
        with self.assertRaises(ValueError) as msg:
            report.list_results(score="f1-macro", model="STree")
        self.assertEqual(str(msg.exception), "** No results found **")
