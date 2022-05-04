import argparse
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
from wodt import Wodt
from odte import Odte
from xgboost import XGBClassifier
from .Utils import Files

ALL_METRICS = (
    "accuracy",
    "f1-macro",
    "f1-micro",
    "f1-weighted",
    "roc-auc-ovr",
)


class Models:
    @staticmethod
    def define_models(random_state):
        return {
            "STree": Stree(random_state=random_state),
            "Cart": DecisionTreeClassifier(random_state=random_state),
            "ExtraTree": ExtraTreeClassifier(random_state=random_state),
            "Wodt": Wodt(random_state=random_state),
            "SVC": SVC(random_state=random_state),
            "ODTE": Odte(
                base_estimator=Stree(random_state=random_state),
                random_state=random_state,
            ),
            "BaggingStree": BaggingClassifier(
                base_estimator=Stree(random_state=random_state),
                random_state=random_state,
            ),
            "BaggingWodt": BaggingClassifier(
                base_estimator=Wodt(random_state=random_state),
                random_state=random_state,
            ),
            "XGBoost": XGBClassifier(random_state=random_state),
            "AdaBoostStree": AdaBoostClassifier(
                base_estimator=Stree(
                    random_state=random_state,
                ),
                algorithm="SAMME",
                random_state=random_state,
            ),
            "GBC": GradientBoostingClassifier(random_state=random_state),
            "RandomForest": RandomForestClassifier(random_state=random_state),
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


class EnvData:
    @staticmethod
    def load():
        args = {}
        with open(Files.dot_env) as f:
            for line in f.read().splitlines():
                if line == "" or line.startswith("#"):
                    continue
                key, value = line.split("=")
                args[key] = value
        return args


class EnvDefault(argparse.Action):
    # Thanks to https://stackoverflow.com/users/445507/russell-heilling
    def __init__(self, envvar, required=True, default=None, **kwargs):
        self._args = EnvData.load()
        default = self._args[envvar]
        required = False
        super(EnvDefault, self).__init__(
            default=default, required=required, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class Arguments:
    def __init__(self):
        self.ap = argparse.ArgumentParser()
        models_data = Models.define_models(random_state=0)
        self.parameters = {
            "best": [
                ("-b", "--best"),
                {
                    "type": str,
                    "required": False,
                    "help": "best results of models",
                },
            ],
            "color": [],
            "compare": [
                ("-c", "--compare"),
                {
                    "type": bool,
                    "required": False,
                    "help": "Compare accuracy with best results",
                },
            ],
            "dataset": [],
            "excel": [
                ("-x", "--excel"),
                {
                    "type": bool,
                    "required": False,
                    "default": False,
                    "help": "Generate Excel File",
                },
            ],
            "file": [
                ("-f", "--file"),
                {"type": str, "required": False, "help": "Result file"},
            ],
            "grid": [
                ("-g", "--grid"),
                {
                    "type": str,
                    "required": False,
                    "help": "grid results of model",
                },
            ],
            "grid_paramfile": [],
            "hidden": [],
            "hyperparameters": [],
            "key": [],
            "lose": [],
            "model": [
                ("-m", "--model"),
                {
                    "type": str,
                    "required": True,
                    "choices": list(models_data),
                    "action": EnvDefault,
                    "envvar": "model",
                    "help": f"model name",
                },
            ],
            "model1": [],
            "model2": [],
            "nan": [],
            "number": [],
            "n_folds": [],
            "paramfile": [],
            "platform": [],
            "quiet": [],
            "report": [],
            "score": [
                ("-s", "--score"),
                {
                    "action": EnvDefault,
                    "envvar": "score",
                    "type": str,
                    "required": True,
                    "choices": ALL_METRICS,
                },
            ],
            "sql": [
                ("-q", "--sql"),
                {"type": bool, "required": False, "help": "Generate SQL File"},
            ],
            "stratified": [],
            "tex_output": [
                ("-t", "--tex-output"),
                {
                    "type": bool,
                    "required": False,
                    "default": False,
                    "help": "Generate Tex file with the table",
                },
            ],
            "title": [],
            "win": [],
        }

    def xset(self, *arg_name, **kwargs):
        names, default = self.parameters[arg_name[0]]
        self.ap.add_argument(
            *names,
            **{**default, **kwargs},
        )
        return self

    def parse(self):
        return self.ap.parse_args()
