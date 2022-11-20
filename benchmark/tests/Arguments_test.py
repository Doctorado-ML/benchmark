import os
from io import StringIO
from unittest.mock import patch
from .TestBase import TestBase
from ..Arguments import Arguments, ALL_METRICS, NO_ENV


class ArgumentsTest(TestBase):
    def build_args(self):
        arguments = Arguments()
        arguments.xset("n_folds").xset("model", mandatory=True)
        arguments.xset("key", required=True)
        return arguments

    def test_build_hyperparams_file(self):
        expected_metrics = (
            "accuracy",
            "f1-macro",
            "f1-micro",
            "f1-weighted",
            "roc-auc-ovr",
        )
        self.assertSequenceEqual(ALL_METRICS, expected_metrics)

    def test_parameters(self):
        expected_parameters = {
            "color": ("-c", "--color"),
            "compare": ("-c", "--compare"),
            "dataset": ("-d", "--dataset"),
            "excel": ("-x", "--excel"),
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
    def test_xset_mandatory(self, stderr):
        arguments = self.build_args()
        test_args = ["-n", "3", "-k", "date"]
        with self.assertRaises(SystemExit):
            arguments.parse(test_args)
        self.assertRegexpMatches(
            stderr.getvalue(),
            r"error: the following arguments are required: -m/--model",
        )

    @patch("sys.stderr", new_callable=StringIO)
    def test_xset_required(self, stderr):
        arguments = self.build_args()
        test_args = ["-n", "3", "-m", "SVC"]
        with self.assertRaises(SystemExit):
            arguments.parse(test_args)
        self.assertRegexpMatches(
            stderr.getvalue(),
            r"error: the following arguments are required: -k/--key",
        )

    @patch("sys.stderr", new_callable=StringIO)
    def test_no_env(self, stderr):
        path = os.getcwd()
        os.chdir("..")
        try:
            self.build_args()
        except SystemExit:
            pass
        finally:
            os.chdir(path)
        self.assertEqual(stderr.getvalue(), f"{NO_ENV}\n")

    @patch("sys.stderr", new_callable=StringIO)
    def test_overrides(self, stderr):
        arguments = self.build_args()
        arguments.xset("title")
        arguments.xset("dataset", overrides="title", const="sample text")
        test_args = ["-n", "3", "-m", "SVC", "-k", "1", "-d", "dataset"]
        args = arguments.parse(test_args)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(args.title, "sample text")

    @patch("sys.stderr", new_callable=StringIO)
    def test_overrides_no_args(self, stderr):
        arguments = self.build_args()
        arguments.xset("title")
        arguments.xset("dataset", overrides="title", const="sample text")
        test_args = None
        with self.assertRaises(SystemExit):
            arguments.parse(test_args)
        self.assertRegexpMatches(
            stderr.getvalue(),
            r"error: the following arguments are required: -m/--model, "
            "-k/--key, --title",
        )
