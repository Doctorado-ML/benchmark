from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.svm import SVC
from stree import Stree
from wodt import TreeClassifier
from odte import Odte


class Models:
    @staticmethod
    def get_model(name):
        if name == "STree":
            return Stree
        elif name == "Cart":
            return DecisionTreeClassifier
        elif name == "ExtraTree":
            return ExtraTreeClassifier
        elif name == "Wodt":
            return TreeClassifier
        elif name == "SVC":
            return SVC
        elif name == "ODTE":
            return Odte
        else:
            msg = f"No model recognized {name}"
            if name == "Stree" or name == "stree":
                msg += ", did you mean STree?"
            elif name == "odte" or name == "Odte":
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
        elif name == "SVC":
            nodes = leaves = depth = 0
        else:
            nodes, leaves = result.nodes_leaves()
            depth = result.depth_ if hasattr(result, "depth_") else 0
        return nodes, leaves, depth
