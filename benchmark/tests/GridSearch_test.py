import json
from .TestBase import TestBase
from ..Experiments import GridSearch
from ..Datasets import Datasets


class GridSearchTest(TestBase):
    def setUp(self):
        self.grid = self.build_exp()

    def tearDown(self) -> None:
        grid = self.build_exp()
        grid.do_gridsearch()
        return super().tearDown()

    def build_exp(self):
        params = {
            "score_name": "accuracy",
            "model_name": "STree",
            "stratified": "0",
            "datasets": Datasets(),
            "progress_bar": False,
            "platform": "Test",
            "folds": 2,
            "test": True,
        }
        return GridSearch(**params)

    def test_get_output_file(self):
        file_name = self.grid.get_output_file()
        self.assertEqual(file_name, "results/grid_output_accuracy_STree.json")

    def test_out_file_not_exits(self):
        file_name = self.grid.get_output_file()
        self.remove_files(
            [
                file_name,
            ],
            ".",
        )
        grid = self.build_exp()
        grid._init_data()
        # check the output file is initialized
        with open(file_name) as f:
            data = json.load(f)
        expected = {
            "balance-scale": [
                0.0,
                {},
                "",
            ],
            "balloons": [
                0.0,
                {},
                "",
            ],
        }
        self.assertSequenceEqual(data, expected)

    def test_do_gridsearch(self):
        self.grid.do_gridsearch()
        file_name = self.grid.get_output_file()
        with open(file_name) as f:
            data = json.load(f)
        expected = {
            "balance-scale": [
                0.9199946751863685,
                {
                    "C": 1.0,
                    "kernel": "liblinear",
                    "multiclass_strategy": "ovr",
                },
                "v. 1.2.4, Computed on Test on 2022-02-22 at 12:00:00 took 1s",
            ],
            "balloons": [
                0.625,
                {"C": 1.0, "kernel": "linear", "multiclass_strategy": "ovr"},
                "v. 1.2.4, Computed on Test on 2022-02-22 at 12:00:00 took 1s",
            ],
        }
        for key, value in expected.items():
            self.assertEqual(data[key][0], value[0])
            self.assertDictEqual(data[key][1], value[1])

    def test_duration_message(self):
        expected = ["47.234s", "5.421m", "1.177h"]
        for message, duration in zip(expected, [47.234, 325.237, 4237.173]):
            self.assertEqual(self.grid._duration_message(duration), message)
