import argparse
from .Experiments import Models
from .Utils import Files

ALL_METRICS = (
    "accuracy",
    "f1_macro",
    "f1_micro",
    "f1_weighted",
    "roc_auc_ovr",
)


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
    def __init__(
        self, envvar, required=True, default=None, mandatory=False, **kwargs
    ):
        self._args = EnvData.load()
        if required and not mandatory:
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
            "color": [
                ("-c", "--color"),
                {
                    "type": bool,
                    "required": False,
                    "default": False,
                    "help": "use colors for the tree",
                },
            ],
            "compare": [
                ("-c", "--compare"),
                {
                    "type": bool,
                    "required": False,
                    "help": "Compare accuracy with best results",
                },
            ],
            "dataset": [
                ("-d", "--dataset"),
                {
                    "type": str,
                    "required": False,
                    "help": "dataset to work with",
                },
            ],
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
            "grid_paramfile": [
                ("-g", "--grid_paramfile"),
                {
                    "type": bool,
                    "required": False,
                    "default": False,
                    "help": "Use best hyperparams file?",
                },
            ],
            "hidden": [
                ("--hidden",),
                {
                    "type": str,
                    "required": False,
                    "default": False,
                    "help": "Show hidden results",
                },
            ],
            "hyperparameters": [
                ("-p", "--hyperparameters"),
                {"type": str, "required": False, "default": "{}"},
            ],
            "key": [
                ("-k", "--key"),
                {
                    "type": str,
                    "required": False,
                    "default": "date",
                    "help": "key to sort results",
                },
            ],
            "lose": [
                ("-l", "--lose"),
                {
                    "type": bool,
                    "default": False,
                    "required": False,
                    "help": "show lose results",
                },
            ],
            "model": [
                ("-m", "--model"),
                {
                    "type": str,
                    "required": True,
                    "choices": list(models_data),
                    "action": EnvDefault,
                    "envvar": "model",
                    "help": "model name",
                },
            ],
            "model1": [
                ("-m1", "--model1"),
                {
                    "type": str,
                    "required": True,
                    "choices": list(models_data),
                    "help": "model name",
                },
            ],
            "model2": [
                ("-m2", "--model2"),
                {
                    "type": str,
                    "required": True,
                    "choices": list(models_data),
                    "help": "model name",
                },
            ],
            "nan": [
                ("--nan",),
                {
                    "type": bool,
                    "required": False,
                    "help": "Move nan results to hidden folder",
                },
            ],
            "number": [
                ("-n", "--number"),
                {
                    "type": int,
                    "required": False,
                    "default": 0,
                    "help": "number of results to show, 0 to any",
                },
            ],
            "n_folds": [
                ("-n", "--n_folds"),
                {
                    "action": EnvDefault,
                    "envvar": "n_folds",
                    "type": int,
                    "required": True,
                    "help": "number of folds",
                },
            ],
            "paramfile": [
                ("-f", "--paramfile"),
                {
                    "type": bool,
                    "required": False,
                    "default": False,
                    "help": "Use best hyperparams file?",
                },
            ],
            "platform": [
                ("-P", "--platform"),
                {
                    "action": EnvDefault,
                    "envvar": "platform",
                    "type": str,
                    "required": True,
                    "help": "Platform where the test is run",
                },
            ],
            "quiet": [
                ("-q", "--quiet"),
                {
                    "type": bool,
                    "required": False,
                    "default": False,
                },
            ],
            "report": [
                ("-r", "--report"),
                {
                    "type": bool,
                    "default": False,
                    "required": False,
                    "help": "Report results",
                },
            ],
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
            "stratified": [
                ("-t", "--stratified"),
                {
                    "action": EnvDefault,
                    "envvar": "stratified",
                    "type": str,
                    "required": True,
                    "help": "Stratified",
                },
            ],
            "tex_output": [
                ("-t", "--tex-output"),
                {
                    "type": bool,
                    "required": False,
                    "default": False,
                    "help": "Generate Tex file with the table",
                },
            ],
            "title": [
                ("--title",),
                {"type": str, "required": True, "help": "experiment title"},
            ],
            "win": [
                ("-w", "--win"),
                {
                    "type": bool,
                    "default": False,
                    "required": False,
                    "help": "show win results",
                },
            ],
        }

    def xset(self, *arg_name, **kwargs):
        names, default = self.parameters[arg_name[0]]
        self.ap.add_argument(
            *names,
            **{**default, **kwargs},
        )
        return self

    def parse(self, args=None):
        return self.ap.parse_args(args)
