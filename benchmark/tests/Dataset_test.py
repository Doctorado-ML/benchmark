import shutil
from .TestBase import TestBase
from ..Experiments import Randomized
from ..Datasets import Datasets


class DatasetTest(TestBase):
    def setUp(self):
        self.datasets_values = {
            "balance-scale": (625, 4, 3),
            "balloons": (16, 4, 2),
            "iris": (150, 4, 3),
            "wine": (178, 13, 3),
        }

    def tearDown(self) -> None:
        self.set_env(".env.dist")
        return super().tearDown()

    @staticmethod
    def set_env(env):
        shutil.copy(env, ".env")

    def test_Randomized(self):
        expected = [57, 31, 1714, 17, 23, 79, 83, 97, 7, 1]
        self.assertSequenceEqual(Randomized.seeds, expected)

    def test_Datasets_iterator(self):
        test = {
            ".env.dist": ["balance-scale", "balloons"],
            ".env.surcov": ["iris", "wine"],
            ".env.arff": ["iris", "wine"],
        }
        for key, value in test.items():
            self.set_env(key)
            dt = Datasets()
            computed = []
            for dataset in dt:
                computed.append(dataset)
                X, y = dt.load(dataset)
                m, n = X.shape
                c = max(y) + 1
                # Check dataset integrity
                self.assertSequenceEqual(
                    (m, n, c), self.datasets_values[dataset]
                )
            self.assertSequenceEqual(computed, value)
        self.set_env(".env.dist")

    def test_load_dataset(self):
        dt = Datasets()
        X, y = dt.load("balance-scale")
        self.assertSequenceEqual(X.shape, (625, 4))
        self.assertSequenceEqual(y.shape, (625,))

    def test_create_with_unknown_dataset(self):
        with self.assertRaises(ValueError) as msg:
            Datasets("unknown")
        self.assertEqual(str(msg.exception), "Unknown dataset: unknown")

    def test_load_unknown_dataset(self):
        dt = Datasets()
        with self.assertRaises(ValueError) as msg:
            dt.load("unknown")
        self.assertEqual(str(msg.exception), "Unknown dataset: unknown")

    def test_Datasets_subset(self):
        test = {
            ".env.dist": "balloons",
            ".env.surcov": "wine",
            ".env.arff": "iris",
        }
        for key, value in test.items():
            self.set_env(key)
            dt = Datasets(value)
            computed = []
            for dataset in dt:
                computed.append(dataset)
                X, y = dt.load(dataset)
                m, n = X.shape
                c = max(y) + 1
                # Check dataset integrity
                self.assertSequenceEqual(
                    (m, n, c), self.datasets_values[dataset]
                )
            self.assertSequenceEqual(computed, [value])
        self.set_env(".env.dist")
