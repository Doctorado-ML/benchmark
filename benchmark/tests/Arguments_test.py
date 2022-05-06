from io import StringIO
from unittest.mock import patch
from .TestBase import TestBase
from ..Arguments import Arguments, ALL_METRICS


class ArgumentsTest(TestBase):
    def build_args(self):
        arguments = Arguments()
        arguments.xset("n_folds").xset("model", mandatory=True)
        arguments.xset("key", required=True)
        return arguments

    def test_build_hyperparams_file(self):
        expected_metrics = (
            "accuracy",
            "f1_macro",
            "f1_micro",
            "f1_weighted",
            "roc_auc_ovr",
        )
        self.assertSequenceEqual(ALL_METRICS, expected_metrics)

    def test_parameters(self):
        expected_parameters = {
            "best": ("-b", "--best"),
            "color": ("-c", "--color"),
            "compare": ("-c", "--compare"),
            "dataset": ("-d", "--dataset"),
            "excel": ("-x", "--excel"),
            "file": ("-f", "--file"),
            "grid": ("-g", "--grid"),
            "grid_paramfile": ("-g", "--grid_paramfile"),
            "hidden": ("--hidden",),
            "hyperparameters": ("-p", "--hyperparameters"),
            "key": ("-k", "--key"),
            "lose": ("-l", "--lose"),
            "model": ("-m", "--model"),
            "model1": ("-m1", "--model1"),
            "model2": ("-m2", "--model2"),
            "nan": ("--nan",),
            "number": ("-n", "--number"),
            "n_folds": ("-n", "--n_folds"),
            "paramfile": ("-f", "--paramfile"),
            "platform": ("-P", "--platform"),
            "quiet": ("-q", "--quiet"),
            "report": ("-r", "--report"),
            "score": ("-s", "--score"),
            "sql": ("-q", "--sql"),
            "stratified": ("-t", "--stratified"),
            "tex_output": ("-t", "--tex-output"),
            "title": ("--title",),
            "win": ("-w", "--win"),
        }
        arg = Arguments()
        for key, value in expected_parameters.items():
            self.assertSequenceEqual(arg.parameters[key][0], value, key)

    def test_xset(self):
        arguments = self.build_args()
        test_args = ["-n", "3", "--model", "SVC", "-k", "metric"]
        args = arguments.parse(test_args)
        self.assertEqual(args.n_folds, 3)
        self.assertEqual(args.model, "SVC")
        self.assertEqual(args.key, "metric")

    @patch("sys.stderr", new_callable=StringIO)
    def test_xset_mandatory(self, mock_stderr):
        arguments = self.build_args()
        test_args = ["-n", "3", "-k", "date"]
        with self.assertRaises(SystemExit):
            arguments.parse(test_args)
        self.assertRegexpMatches(
            mock_stderr.getvalue(),
            r"error: the following arguments are required: -m/--model",
        )

    @patch("sys.stderr", new_callable=StringIO)
    def test_xset_required(self, mock_stderr):
        arguments = self.build_args()
        test_args = ["-n", "3", "-m", "SVC"]
        with self.assertRaises(SystemExit):
            arguments.parse(test_args)
        self.assertRegexpMatches(
            mock_stderr.getvalue(),
            r"error: the following arguments are required: -k/--key",
        )
