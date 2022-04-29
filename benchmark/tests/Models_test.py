import warnings
from sklearn.exceptions import ConvergenceWarning
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    BaggingClassifier,
    AdaBoostClassifier,
)
from sklearn.svm import SVC
from sklearn.datasets import load_wine
from stree import Stree
from wodt import Wodt
from odte import Odte
from .TestBase import TestBase
from ..Models import Models


class ModelTest(TestBase):
    def test_Models(self):
        test = {
            "STree": Stree,
            "Wodt": Wodt,
            "ODTE": Odte,
            "Cart": DecisionTreeClassifier,
            "SVC": SVC,
            "RandomForest": RandomForestClassifier,
            "ExtraTree": ExtraTreeClassifier,
        }
        for key, value in test.items():
            self.assertIsInstance(Models.get_model(key), value)

    def test_BaggingStree(self):
        clf = Models.get_model("BaggingStree")
        self.assertIsInstance(clf, BaggingClassifier)
        clf_base = clf.base_estimator
        self.assertIsInstance(clf_base, Stree)

    def test_BaggingWodt(self):
        clf = Models.get_model("BaggingWodt")
        self.assertIsInstance(clf, BaggingClassifier)
        clf_base = clf.base_estimator
        self.assertIsInstance(clf_base, Wodt)

    def test_AdaBoostStree(self):
        clf = Models.get_model("AdaBoostStree")
        self.assertIsInstance(clf, AdaBoostClassifier)
        clf_base = clf.base_estimator
        self.assertIsInstance(clf_base, Stree)

    def test_unknown_classifier(self):
        with self.assertRaises(ValueError):
            Models.get_model("unknown")

    def test_bogus_Stree(self):
        with self.assertRaises(ValueError):
            Models.get_model("Stree")

    def test_bogus_Odte(self):
        with self.assertRaises(ValueError):
            Models.get_model("Odte")

    def test_get_complexity(self):
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        test = {
            "STree": (11, 6, 4),
            "Wodt": (303, 152, 50),
            "ODTE": (7.86, 4.43, 3.37),
            "Cart": (23, 12, 5),
            "SVC": (0, 0, 0),
            "RandomForest": (21.3, 11, 5.26),
            "ExtraTree": (0, 38, 0),
            "BaggingStree": (8.4, 4.7, 3.5),
            "BaggingWodt": (272, 136.5, 50),
        }
        X, y = load_wine(return_X_y=True)
        for key, value in test.items():
            clf = Models.get_model(key, random_state=1)
            clf.fit(X, y)
            # print(key, Models.get_complexity(key, clf))
            self.assertSequenceEqual(Models.get_complexity(key, clf), value)
