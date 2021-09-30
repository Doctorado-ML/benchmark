import os
import subprocess
import argparse


class Folders:
    data = "data"
    results = "results"
    src = "src"
    exreport = "exreport"
    report = os.path.join(exreport, "exreport_output")


class Files:
    index = "all.txt"

    cmd_open_macos = "/usr/bin/open"
    cmd_open_linux = "/usr/bin/xdg-open"
    exreport_pdf = "Rplots.pdf"
    benchmark_r = "benchmark.r"
    arguments = ".env"

    @staticmethod
    def exreport_output(score):
        return f"exreport_{score}.txt"

    @staticmethod
    def exreport_err(score):
        return f"exreport_err_{score}.txt"

    @staticmethod
    def exreport_excel(score):
        return f"exreport_{score}.xlsx"

    @staticmethod
    def exreport(score):
        return f"exreport_{score}.csv"

    @staticmethod
    def best_results(score, model):
        return f"best_results_{score}_{model}.json"

    @staticmethod
    def results(score, model, platform, date, time, stratified):
        return (
            f"results_{score}_{model}_{platform}_{date}_{time}_"
            f"{stratified}.json"
        )

    @staticmethod
    def results_suffixes(score="", model=""):
        suffix = ".json"
        if model == "" and score == "":
            return "results_", suffix
        elif model == "":
            return f"results_{score}_", suffix
        else:
            return f"results_{score}_{model}_", suffix

    @staticmethod
    def dataset(name):
        return f"{name}_R.dat"

    @staticmethod
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    @staticmethod
    def open(name):
        if os.path.isfile(name):
            command = (
                Files.cmd_open_macos
                if Files.is_exe(Files.cmd_open_macos)
                else Files.cmd_open_linux
            )
            subprocess.run([command, name])


class Symbols:
    check_mark = "\N{heavy check mark}"
    exclamation = "\N{heavy exclamation mark symbol}"
    black_star = "\N{black star}"
    equal_best = check_mark
    better_best = black_star


class EnvDefault(argparse.Action):
    # Thanks to https://stackoverflow.com/users/445507/russell-heilling
    def __init__(self, envvar, required=True, default=None, **kwargs):
        self._args = {}
        with open(Files.arguments) as f:
            for line in f.read().splitlines():
                key, value = line.split("=")
                self._args[key] = value
        if not default and envvar in self._args:
            default = self._args[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(
            default=default, required=required, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
