import os
from .TestBase import TestBase
from ..Experiments import BestResults, Datasets


class BestResultTest(TestBase):
    def test_load(self):
        expected = {
            "balance-scale": [
                0.98,
                {"splitter": "iwss", "max_features": "auto"},
                "results_accuracy_STree_iMac27_2021-10-27_09:40:40_0.json",
            ],
            "balloons": [
                0.86,
                {
                    "C": 7,
                    "gamma": 0.1,
                    "kernel": "rbf",
                    "max_iter": 10000.0,
                    "multiclass_strategy": "ovr",
                },
                "results_accuracy_STree_iMac27_2021-09-30_11:42:07_0.json",
            ],
        }
        dt = Datasets()
        model = "STree"
        best = BestResults(
            score="accuracy", model=model, datasets=dt, quiet=True
        )
        best.build()
        self.assertSequenceEqual(best.load({}), expected)

    def test_load_error(self):
        dt = Datasets()
        model = "STree"
        best = BestResults(
            score="accuracy", model=model, datasets=dt, quiet=True
        )
        file_name = best._get_file_name()
        os.rename(file_name, file_name + ".bak")
        try:
            best.load({})
        except ValueError:
            pass
        else:
            self.fail("BestResults.load() should raise ValueError")
        finally:
            os.rename(file_name + ".bak", file_name)

    def test_fill(self):
        dt = Datasets()
        model = "STree"
        best = BestResults(
            score="accuracy", model=model, datasets=dt, quiet=True
        )
        self.assertSequenceEqual(
            best.fill({"test": "test"}, {"balloons": []}),
            {"balloons": [], "balance-scale": (0.0, {"test": "test"}, "")},
        )
        self.assertSequenceEqual(
            best.fill({}),
            {"balance-scale": (0.0, {}, ""), "balloons": (0.0, {}, "")},
        )

    def test_build_error(self):
        dt = Datasets()
        model = "SVC"
        best = BestResults(
            score="accuracy", model=model, datasets=dt, quiet=True
        )
        with self.assertRaises(ValueError):
            best.build()
