import os
import sys
import subprocess

PYTHON_VERSION = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
NO_RESULTS = "** No results found **"
NO_ENV = "File .env not found"


class Folders:
    results = "results"
    hidden_results = "hidden_results"
    exreport = "exreport"
    report = os.path.join(exreport, "exreport_output")
    img = "img"
    excel = "excel"
    sql = "sql"
    current = os.getcwd()

    @staticmethod
    def src():
        return os.path.dirname(os.path.abspath(__file__))


class Files:
    index = "all.txt"
    report_ext = ".json"
    cmd_open_macos = "/usr/bin/open"
    cmd_open_linux = "/usr/bin/xdg-open"
    exreport_pdf = "Rplots.pdf"
    benchmark_r = "benchmark.r"
    dot_env = ".env"
    datasets_report_excel = "ReportDatasets.xlsx"
    be_list_excel = "some_results.xlsx"

    @staticmethod
    def exreport_output(score):
        return f"exreport_{score.replace('_','-')}.txt"

    @staticmethod
    def exreport_err(score):
        return f"exreport_err_{score.replace('_','-')}.txt"

    @staticmethod
    def exreport_excel(score):
        return f"exreport_{score.replace('_','-')}.xlsx"

    @staticmethod
    def exreport(score):
        return f"exreport_{score.replace('_','-')}.csv"

    @staticmethod
    def tex_output(score):
        return f"exreport_{score.replace('_','-')}.tex"

    @staticmethod
    def best_results(score, model):
        return f"best_results_{score.replace('_','-')}_{model}.json"

    @staticmethod
    def results(score, model, platform, date, time, stratified):
        return (
            f"results_{score.replace('_','-')}_{model}_{platform}_{date}_"
            f"{time}_{stratified}.json"
        )

    @staticmethod
    def grid_input(score, model):
        return Files.grid("input", score, model)

    @staticmethod
    def grid_output(score, model):
        return Files.grid("output", score, model)

    @staticmethod
    def grid(kind, score, model):
        return f"grid_{kind}_{score.replace('_','-')}_{model}.json"

    def split_file_name(self, name):
        _, score, model, platform, date, time, stratified = name.split("_")
        stratified = stratified.replace(self.report_ext, "")
        return score, model, platform, date, time, stratified

    @staticmethod
    def results_suffixes(score="", model=""):
        suffix = Files.report_ext
        if model == "" and score == "":
            return "results_", suffix
        if model == "":
            return f"results_{score}_", suffix
        return f"results_{score}_{model}_", suffix

    @staticmethod
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    @staticmethod
    def open(name, test=False):
        if os.path.isfile(name):
            command = (
                Files.cmd_open_macos
                if Files.is_exe(Files.cmd_open_macos)
                else Files.cmd_open_linux
            )
            return (
                subprocess.run([command, name])
                if not test
                else [command, name]
            )
        return None

    @staticmethod
    def get_all_results(hidden) -> list[str]:
        result_path = os.path.join(
            ".", Folders.hidden_results if hidden else Folders.results
        )
        if os.path.isdir(result_path):
            files_list = os.listdir(result_path)
        else:
            raise ValueError(f"{result_path} does not exist")
        result = []
        prefix, suffix = Files.results_suffixes()
        for result_file in files_list:
            if result_file.startswith(prefix) and result_file.endswith(suffix):
                result.append(result_file)
        return sorted(result)


class Symbols:
    check_mark = "\N{heavy check mark}"
    exclamation = "\N{heavy exclamation mark symbol}"
    black_star = "\N{black star}"
    cross = "\N{Ballot X}"
    upward_arrow = "\N{Black-feathered north east arrow}"
    down_arrow = "\N{downwards black arrow}"
    equal_best = check_mark
    better_best = black_star


class TextColor:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    HEADER = MAGENTA
    LINE1 = BLUE
    LINE2 = CYAN
    SUCCESS = GREEN
    WARNING = YELLOW
    FAIL = RED
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    BLACK = "\033[90m"
    DEFAULT = "\033[99m"
