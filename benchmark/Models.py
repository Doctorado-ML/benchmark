from statistics import mean
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    BaggingClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier,
)
from sklearn.svm import SVC
from stree import Stree
from bayesclass.clfs import TAN, KDB, AODE, KDBNew, TANNew, AODENew
from wodt import Wodt
from odte import Odte
from xgboost import XGBClassifier
import sklearn
import xgboost

import random


class MockModel(SVC):
    # Only used for testing
    def predict(self, X):
        if random.random() < 0.1:
            return [float("NaN")] * len(X)
        return super().predict(X)

    def nodes_leaves(self):
        return 0, 0

    def fit(self, X, y, **kwargs):
        kwargs.pop("state_names", None)
        kwargs.pop("features", None)
        return super().fit(X, y, **kwargs)


class Models:
    @staticmethod
    def define_models(random_state):
        return {
            "STree": Stree(random_state=random_state),
            "TAN": TAN(random_state=random_state),
            "KDB": KDB(k=2),
            "TANNew": TANNew(random_state=random_state),
            "KDBNew": KDBNew(k=2),
            "AODE": AODE(random_state=random_state),
            "Cart": DecisionTreeClassifier(random_state=random_state),
            "ExtraTree": ExtraTreeClassifier(random_state=random_state),
            "Wodt": Wodt(random_state=random_state),
            "SVC": SVC(random_state=random_state),
            "ODTE": Odte(
                estimator=Stree(random_state=random_state),
                random_state=random_state,
            ),
            "BaggingStree": BaggingClassifier(
                estimator=Stree(random_state=random_state),
                random_state=random_state,
            ),
            "BaggingWodt": BaggingClassifier(
                estimator=Wodt(random_state=random_state),
                random_state=random_state,
            ),
            "XGBoost": XGBClassifier(random_state=random_state),
            "AdaBoostStree": AdaBoostClassifier(
                estimator=Stree(
                    random_state=random_state,
                ),
                algorithm="SAMME",
                random_state=random_state,
            ),
            "GBC": GradientBoostingClassifier(random_state=random_state),
            "RandomForest": RandomForestClassifier(random_state=random_state),
            "Mock": MockModel(random_state=random_state),
        }

    @staticmethod
    def get_model(name, random_state=None):
        try:
            models = Models.define_models(random_state)
            return models[name]
        except KeyError:
            msg = f"No model recognized {name}"
            if name in ("Stree", "stree"):
                msg += ", did you mean STree?"
            elif name in ("odte", "Odte"):
                msg += ", did you mean ODTE?"
        raise ValueError(msg)

    @staticmethod
    def get_complexity(name, result):
        if name == "Cart":
            nodes = result.tree_.node_count
            depth = result.tree_.max_depth
            leaves = result.get_n_leaves()
        elif name == "ExtraTree":
            nodes = 0
            leaves = result.get_n_leaves()
            depth = 0
        elif name.startswith("Bagging") or name.startswith("AdaBoost"):
            nodes, leaves = list(
                zip(*[x.nodes_leaves() for x in result.estimators_])
            )
            nodes, leaves = mean(nodes), mean(leaves)
            depth = mean([x.depth_ for x in result.estimators_])
        elif name == "RandomForest":
            leaves = mean([x.get_n_leaves() for x in result.estimators_])
            depth = mean([x.get_depth() for x in result.estimators_])
            nodes = mean([x.tree_.node_count for x in result.estimators_])
        elif name == "GBC":
            leaves = mean([x[0].get_n_leaves() for x in result.estimators_])
            depth = mean([x[0].get_depth() for x in result.estimators_])
            nodes = mean([x[0].tree_.node_count for x in result.estimators_])
        elif name == "SVC" or name == "XGBoost":
            nodes = leaves = depth = 0
        else:
            nodes, leaves = result.nodes_leaves()
            depth = result.depth_ if hasattr(result, "depth_") else 0
        return nodes, leaves, depth

    @staticmethod
    def get_version(name, clf):
        if hasattr(clf, "version"):
            return clf.version()
        if name in ["Cart", "ExtraTree", "RandomForest", "GBC", "SVC"]:
            return sklearn.__version__
        elif name.startswith("Bagging") or name.startswith("AdaBoost"):
            return sklearn.__version__
        elif name == "XGBoost":
            return xgboost.__version__
        return "Error"
