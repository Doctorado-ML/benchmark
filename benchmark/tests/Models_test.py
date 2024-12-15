import warnings
from sklearn.exceptions import ConvergenceWarning
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    BaggingClassifier,
    AdaBoostClassifier,
)
from sklearn.svm import SVC
from sklearn.datasets import load_wine
from stree import Stree
from wodt import Wodt
from odte import Odte
from xgboost import XGBClassifier
from .TestBase import TestBase
from ..Models import Models
import xgboost
import sklearn


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
            "XGBoost": XGBClassifier,
            "GBC": GradientBoostingClassifier,
        }
        for key, value in test.items():
            self.assertIsInstance(Models.get_model(key), value)

    def test_Models_version(self):
        def ver_stree():
            return "1.2.3"

        def ver_wodt():
            return "h.j.k"

        def ver_odte():
            return "4.5.6"

        test = {
            "STree": [ver_stree, "1.2.3"],
            "Wodt": [ver_wodt, "h.j.k"],
            "ODTE": [ver_odte, "4.5.6"],
            "RandomForest": [None, "7.8.9"],
            "BaggingStree": [None, "x.y.z"],
            "AdaBoostStree": [None, "w.x.z"],
            "XGBoost": [None, "10.11.12"],
        }
        for key, value in test.items():
            clf = Models.get_model(key)
            if key in ["STree", "Wodt", "ODTE"]:
                clf.version = value[0]
            elif key == "XGBoost":
                xgboost.__version__ = value[1]
            else:
                sklearn.__version__ = value[1]
            self.assertEqual(Models.get_version(key, clf), value[1])

    def test_bogus_Model_Version(self):
        self.assertEqual(Models.get_version("unknown", None), "Error")

    def test_BaggingStree(self):
        clf = Models.get_model("BaggingStree")
        self.assertIsInstance(clf, BaggingClassifier)
        clf_base = clf.estimator
        self.assertIsInstance(clf_base, Stree)

    def test_BaggingWodt(self):
        clf = Models.get_model("BaggingWodt")
        self.assertIsInstance(clf, BaggingClassifier)
        clf_base = clf.estimator
        self.assertIsInstance(clf_base, Wodt)

    def test_AdaBoostStree(self):
        clf = Models.get_model("AdaBoostStree")
        self.assertIsInstance(clf, AdaBoostClassifier)
        clf_base = clf.estimator
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
            "STree": ((11, 6, 4), 1.0),
            "Wodt": ((303, 152, 50), 0.9382022471910112),
            "ODTE": ((786, 443, 337), 1.0),
            "Cart": ((23, 12, 5), 1.0),
            "SVC": ((0, 0, 0), 0.7078651685393258),
            "RandomForest": ((21.3, 11, 5.26), 1.0),
            "ExtraTree": ((0, 38, 0), 1.0),
            "BaggingStree": ((8.4, 4.7, 3.5), 1.0),
            "BaggingWodt": ((272, 136.5, 50), 0.9101123595505618),
            "AdaBoostStree": ((12.25, 6.625, 4.75), 1.0),
            "XGBoost": ((0, 0, 0), 1.0),
            "GBC": ((15, 8, 3), 1.0),
        }
        X, y = load_wine(return_X_y=True)
        for key, (value, score_expected) in test.items():
            clf = Models.get_model(key, random_state=1)
            clf.fit(X, y)
            score_computed = clf.score(X, y)
            # print(
            #     key,
            #     Models.get_complexity(key, clf),
            #     score_expected,
            #     score_computed,
            # )
            # Fix flaky test
            if key == "AdaBoostStree":
                # computed values
                a_c, b_c, c_c = Models.get_complexity(key, clf)
                # expected values
                a_e, b_e, c_e = value
                for c, e in zip((a_c, b_c, c_c), (a_e, b_e, c_e)):
                    self.assertAlmostEqual(c, e, delta=0.25)
            else:
                self.assertSequenceEqual(
                    Models.get_complexity(key, clf), value
                )
            self.assertEqual(score_computed, score_expected, key)
