import argparse
from .Experiments import Models
from .Utils import Files

ALL_METRICS = (
    "accuracy",
    "f1-macro",
    "f1-micro",
    "f1-weighted",
    "roc-auc-ovr",
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
        models = "{" + ", ".join(models_data) + "}"
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
                    "help": f"model name: {models}",
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
        print("parameters", arg_name[0])
        names, default = self.parameters[arg_name[0]]
        self.ap.add_argument(
            *names,
            **{**default, **kwargs},
        )
        return self

    def parse(self):
        return self.ap.parse_args()
