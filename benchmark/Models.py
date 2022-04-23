from statistics import mean
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    BaggingClassifier,
    AdaBoostClassifier,
)
from sklearn.svm import SVC
from stree import Stree
from wodt import Wodt
from odte import Odte


class Models:
    @staticmethod
    def get_model(name, random_state=None):
        if name == "STree":
            return Stree(random_state=random_state)
        if name == "Cart":
            return DecisionTreeClassifier(random_state=random_state)
        if name == "ExtraTree":
            return ExtraTreeClassifier(random_state=random_state)
        if name == "Wodt":
            return Wodt(random_state=random_state)
        if name == "SVC":
            return SVC(random_state=random_state)
        if name == "ODTE":
            return Odte(
                base_estimator=Stree(random_state=random_state),
                random_state=random_state,
            )
        if name == "BaggingStree":
            clf = Stree(random_state=random_state)
            return BaggingClassifier(
                base_estimator=clf, random_state=random_state
            )
        if name == "BaggingWodt":
            clf = Wodt(random_state=random_state)
            return BaggingClassifier(
                base_estimator=clf, random_state=random_state
            )
        if name == "AdaBoostStree":
            clf = Stree(
                random_state=random_state,
            )
            return AdaBoostClassifier(
                base_estimator=clf,
                algorithm="SAMME",
                random_state=random_state,
            )
        if name == "RandomForest":
            return RandomForestClassifier(random_state=random_state)
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
        elif name == "SVC":
            nodes = leaves = depth = 0
        else:
            nodes, leaves = result.nodes_leaves()
            depth = result.depth_ if hasattr(result, "depth_") else 0
        return nodes, leaves, depth
