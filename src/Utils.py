import os
import subprocess
import argparse

BEST_ACCURACY_STREE = 40.282203


class Folders:
    data = "data"
    results = "results"
    src = "src"
    exreport = "exreport"
    report = os.path.join(exreport, "exreport_output")


class Files:
    index = "all.txt"
    report_ext = ".json"
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

    def split_file_name(self, name):
        _, score, model, platform, date, time, stratified = name.split("_")
        stratified = stratified.replace(self.report_ext, "")
        return score, model, platform, date, time, stratified

    def results_suffixes(self, score="", model=""):
        suffix = self.report_ext
        if model == "" and score == "":
            return "results_", suffix
        if model == "":
            return f"results_{score}_", suffix
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

    def get_all_results(self) -> list[str]:
        first_path = "."
        first_try = os.path.join(first_path, Folders.results)
        second_path = ".."
        second_try = os.path.join(second_path, first_try)
        if os.path.isdir(first_try):
            files_list = os.listdir(first_try)
        elif os.path.isdir(second_try):
            files_list = os.listdir(second_try)
        else:
            raise ValueError(f"{first_try} or {second_try} does not exist")
        result = []
        prefix, suffix = self.results_suffixes()
        for result_file in files_list:
            if result_file.startswith(prefix) and result_file.endswith(suffix):
                result.append(result_file)
        return result


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
