import sys
import argparse
from .Models import Models
from .Utils import Files, NO_ENV

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
        try:
            with open(Files.dot_env) as f:
                for line in f.read().splitlines():
                    if line == "" or line.startswith("#"):
                        continue
                    key, value = line.split("=")
                    args[key] = value
        except FileNotFoundError:
            print(NO_ENV, file=sys.stderr)
            exit(1)
        else:
            return args


class EnvDefault(argparse.Action):
    # Thanks to https://stackoverflow.com/users/445507/russell-heilling
    def __init__(
        self, envvar, required=True, default=None, mandatory=False, **kwargs
    ):
        self._args = EnvData.load()
        self._overrides = {}
        if required and not mandatory:
            default = self._args[envvar]
            required = False
        super(EnvDefault, self).__init__(
            default=default, required=required, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class Arguments(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        models_data = Models.define_models(random_state=0)
        self._overrides = {}
        self._subparser = None
        self.parameters = {
            "best_paramfile": [
                ("-b", "--best_paramfile"),
                {
                    "action": "store_true",
                    "required": False,
                    "default": False,
                    "help": "Use best hyperparams file?",
                },
            ],
            "color": [
                ("-c", "--color"),
                {
                    "required": False,
                    "action": "store_true",
                    "default": False,
                    "help": "use colors for the tree",
                },
            ],
            "compare": [
                ("-c", "--compare"),
                {
                    "action": "store_true",
                    "required": False,
                    "default": False,
                    "help": "Compare accuracy with best results",
                },
            ],
            "dataset": [
                ("-d", "--dataset"),
                {
                    "type": str,
                    "envvar": "dataset",  # for compatiblity with EnvDefault
                    "action": EnvDefault,
                    "required": False,
                    "help": "dataset to work with",
                },
            ],
            "discretize": [
                ("--discretize",),
                {
                    "action": EnvDefault,
                    "envvar": "discretize",
                    "required": True,
                    "help": "Discretize dataset",
                    "const": "1",
                    "nargs": "?",
                },
            ],
            "excel": [
                ("-x", "--excel"),
                {
                    "required": False,
                    "action": "store_true",
                    "default": False,
                    "help": "Generate Excel File",
                },
            ],
            "fit_features": [
                ("--fit_features",),
                {
                    "action": EnvDefault,
                    "envvar": "fit_features",
                    "required": True,
                    "help": "Include features in fit call",
                    "const": "1",
                    "nargs": "?",
                },
            ],
            "grid_paramfile": [
                ("-g", "--grid_paramfile"),
                {
                    "required": False,
                    "action": "store_true",
                    "default": False,
                    "help": "Use grid output hyperparams file?",
                },
            ],
            "hidden": [
                ("--hidden",),
                {
                    "required": False,
                    "action": "store_true",
                    "default": False,
                    "help": "Show hidden results",
                },
            ],
            "hyperparameters": [
                ("-p", "--hyperparameters"),
                {"type": str, "required": False, "default": "{}"},
            ],
            "ignore_nan": [
                ("--ignore-nan",),
                {
                    "default": False,
                    "action": "store_true",
                    "required": False,
                    "help": "Ignore nan results",
                },
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
                    "default": False,
                    "action": "store_true",
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
                    "action": "store_true",
                    "required": False,
                    "default": False,
                    "help": "List nan results to hidden folder",
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
                    "action": "store_true",
                    "required": False,
                    "default": False,
                },
            ],
            "report": [
                ("-r", "--report"),
                {
                    "action": "store_true",
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
                {
                    "required": False,
                    "action": "store_true",
                    "default": False,
                    "help": "Generate SQL File",
                },
            ],
            "stratified": [
                ("-t", "--stratified"),
                {
                    "action": EnvDefault,
                    "envvar": "stratified",
                    "required": True,
                    "help": "Stratified",
                    "const": "1",
                    "nargs": "?",
                },
            ],
            "tex_output": [
                ("-t", "--tex-output"),
                {
                    "required": False,
                    "action": "store_true",
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
                    "default": False,
                    "action": "store_true",
                    "required": False,
                    "help": "show win results",
                },
            ],
        }

    def xset(self, *arg_name, **kwargs):
        names, parameters = self.parameters[arg_name[0]]
        if "overrides" in kwargs:
            self._overrides[names[0]] = (kwargs["overrides"], kwargs["const"])
            del kwargs["overrides"]
        self.add_argument(
            *names,
            **{**parameters, **kwargs},
        )
        return self

    def add_subparser(
        self, dest="subcommand", help_text="help for subcommand"
    ):
        self._subparser = self.add_subparsers(dest=dest, help=help_text)

    def add_subparsers_options(self, subparser, arguments):
        command, help_text = subparser
        parser = self._subparser.add_parser(command, help=help_text)
        for name, args in arguments:
            try:
                names, parameters = self.parameters[name]
            except KeyError:
                names = (name,)
                parameters = {}
            # Order of args is important
            parser.add_argument(*names, **{**args, **parameters})

    def add_exclusive(self, hyperparameters, required=False):
        group = self.add_mutually_exclusive_group(required=required)
        for name in hyperparameters:
            names, parameters = self.parameters[name]
            group.add_argument(*names, **parameters)

    def parse(self, args=None):
        for key, (dest_key, value) in self._overrides.items():
            if args is None:
                args = sys.argv[1:]
            if key in args:
                args.extend((f"--{dest_key}", value))
        return super().parse_args(args)
