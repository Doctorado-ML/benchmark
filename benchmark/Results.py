import math
import os
from operator import itemgetter
from types import SimpleNamespace

import xlsxwriter

from .Datasets import Datasets
from .ResultsBase import BaseReport, StubReport, get_input
from .ResultsFiles import Excel
from .Utils import NO_RESULTS, Files, Folders, TextColor


class Report(BaseReport):
    header_lengths = [30, 6, 5, 3, 7, 7, 7, 15, 17, 15]

    def __init__(self, file_name: str, compare: bool = False):
        super().__init__(file_name)
        self.nline = 0
        self.compare = compare
        self.header_cols = [
            "Dataset",
            "Sampl.",
            "Feat.",
            "Cls",
            self.nodes_label,
            self.leaves_label,
            self.depth_label,
            "Score",
            "Time",
            "Hyperparameters",
        ]

    def header_line(self, text: str) -> None:
        print(TextColor.LINE1, end="")
        length = sum(self.header_lengths) + len(self.header_lengths) - 3
        if text == "*":
            print("*" * (length + 2))
        else:
            print(f"*{text:{length}s}*")

    def print_line(self, result) -> None:
        self.nline += 1
        text_color = (
            TextColor.LINE1 if self.nline % 2 == 0 else TextColor.LINE2
        )
        print(text_color, end="")
        hl = self.header_lengths
        i = 0
        print(f"{result['dataset']:{hl[i]}s} ", end="")
        i += 1
        print(f"{result['samples']:{hl[i]},d} ", end="")
        i += 1
        print(f"{result['features']:{hl[i]},d} ", end="")
        i += 1
        print(f"{result['classes']:{hl[i]}d} ", end="")
        i += 1
        print(f"{result['nodes']:{hl[i]}.2f} ", end="")
        i += 1
        print(f"{result['leaves']:{hl[i]}.2f} ", end="")
        i += 1
        print(f"{result['depth']:{hl[i]}.2f} ", end="")
        i += 1
        status = self._compute_status(result["dataset"], result["score"])
        print(
            f"{result['score']:8.6f}±{result['score_std']:6.4f}{status}",
            end="",
        )
        i += 1
        print(
            f"{result['time']:10.6f}±{result['time_std']:6.4f} ",
            end="",
        )
        i += 1
        print(f"{str(result['hyperparameters']):{hl[i]}s} ")

    def header(self) -> None:
        if self.compare:
            self._load_best_results(
                self.data["score_name"], self.data["model"]
            )
        self._compare_totals = {}
        self.header_line("*")
        self.header_line(
            f" {self.data['model']} ver. {self.data['version']}"
            f" {self.data['language']} ver. {self.data['language_version']}"
            f" with {self.data['folds']} Folds "
            f"cross validation and {len(self.data['seeds'])} random seeds. "
            f"{self.data['date']} {self.data['time']}"
        )
        self.header_line(f" {self.data['title']}")
        self.header_line(
            f" Random seeds: {self.data['seeds']} Stratified: "
            f"{self.data['stratified']}  Discretized: "
            f"{self.data['discretized']}"
        )
        hours = self.data["duration"] / 3600
        self.header_line(
            f" Execution took {self.data['duration']:7.2f} seconds, "
            f" {hours:5.2f} hours, on {self.data['platform']}"
        )
        self.header_line(f" Score is {self.data['score_name']}")
        self.header_line("*")
        print("")
        line_col = ""
        for field, underscore in zip(self.header_cols, self.header_lengths):
            print(f"{field:{underscore}s} ", end="")
            line_col += "=" * underscore + " "
        print(f"\n{line_col}")

    def footer(self, accuracy: float) -> None:
        self.header_line("*")
        for key, value in self._compare_totals.items():
            meaning = self._status_meaning(key)
            self.header_line(
                f" {key} {meaning}"
                + "." * (30 - len(meaning))
                + f": {value:2d}"
            )
        self.header_line(
            f" {self._get_message_best_accuracy()} "
            f"{accuracy/self._get_best_accuracy():7.4f}"
        )
        self.header_line("*")


class ReportBest(BaseReport):
    header_lengths = [30, 8, 76, 45]
    header_cols = [
        "Dataset",
        "Score",
        "File/Message",
        "Hyperparameters",
    ]

    def __init__(self, score, model, best):
        name = (
            Files.best_results(score, model)
            if best
            else Files.grid_output(score, model)
        )
        file_name = os.path.join(Folders.results, name)
        self.best = best
        self.score_name = score
        self.model = model
        super().__init__(file_name, best_file=True)

    def header_line(self, text: str) -> None:
        length = sum(self.header_lengths) + len(self.header_lengths) - 3
        if text == "*":
            print("*" * (length + 2))
        else:
            print(f"*{text:{length}s}*")

    def print_line(self, result):
        hl = self.header_lengths
        print(f"{result:{hl[0]}s} ", end="")
        print(
            f"{self.data[result][0]:8.6f} ",
            end="",
        )
        print(
            f"{self.data[result][2]:{hl[2]}s} ",
            end="",
        )
        print(f"{str(self.data[result][1]):{hl[1]}s} ")

    def header(self):
        self.header_line("*")
        kind = "Best" if self.best else "Grid"
        self.header_line(
            f" Report {kind} {self.score_name} Scores with {self.model} "
            "in any platform"
        )
        self.header_line("*")
        print("")
        line_col = ""
        for field, underscore in zip(self.header_cols, self.header_lengths):
            print(f"{field:{underscore}s} ", end="")
            line_col += "=" * underscore + " "
        print(f"\n{line_col}")

    def footer(self, accuracy):
        self.header_line("*")
        self.header_line(
            f" {self._get_message_best_accuracy()} "
            f"{accuracy/self._get_best_accuracy():7.4f}"
        )
        self.header_line("*")


class Summary:
    def __init__(self, hidden=False, compare=False) -> None:
        self.results = Files().get_all_results(hidden=hidden)
        self.data = []
        self.data_filtered = []
        self.datasets = {}
        self.models = set()
        self.hidden = hidden
        self.compare = compare

    def get_models(self):
        return sorted(self.models)

    def acquire(self, given_score="any") -> None:
        """Get all results"""
        for result in self.results:
            (
                score,
                model,
                platform,
                date,
                time,
                stratified,
            ) = Files().split_file_name(result)
            if given_score in ("any", score):
                self.models.add(model)
                report = StubReport(
                    os.path.join(
                        Folders.hidden_results
                        if self.hidden
                        else Folders.results,
                        result,
                    )
                )
                report.report()
                entry = dict(
                    score=score,
                    model=model,
                    title=report.title,
                    platform=platform,
                    date=date,
                    time=time,
                    stratified=stratified,
                    file=result,
                    metric=report.score,
                    duration=report.duration,
                )
                self.datasets[result] = report.lines
                self.data.append(entry)

    def get_results_criteria(
        self, score, model, input_data, sort_key, number, nan=False
    ):
        data = self.data.copy() if input_data is None else input_data
        if score:
            data = [x for x in data if x["score"] == score]
        if model:
            data = [x for x in data if x["model"] == model]
        if nan:
            data = [x for x in data if x["metric"] != x["metric"]]
        keys = (
            itemgetter(sort_key, "time")
            if sort_key == "date"
            else itemgetter(sort_key, "date", "time")
        )
        data = sorted(data, key=keys, reverse=True)
        if number > 0:
            data = data[:number]
        return data

    def list_results(
        self,
        score=None,
        model=None,
        input_data=None,
        sort_key="date",
        number=0,
        nan=False,
    ) -> None:
        """Print the list of results"""
        if self.data_filtered == []:
            self.data_filtered = self.get_results_criteria(
                score, model, input_data, sort_key, number, nan=nan
            )
        if self.data_filtered == []:
            raise ValueError(NO_RESULTS)
        max_file = max(len(x["file"]) for x in self.data_filtered)
        max_title = max(len(x["title"]) for x in self.data_filtered)
        if self.hidden:
            color1 = TextColor.GREEN
            color2 = TextColor.YELLOW
        else:
            color1 = TextColor.LINE1
            color2 = TextColor.LINE2
        print(color1, end="")
        print(
            f" #  {'Date':10s} {'File':{max_file}s} {'Score':8s} "
            f"{'Time(h)':7s} {'Title':s}"
        )
        print(
            "===",
            "=" * 10
            + " "
            + "=" * max_file
            + " "
            + "=" * 8
            + " "
            + "=" * 7
            + " "
            + "=" * max_title,
        )
        print(
            "\n".join(
                [
                    (color2 if n % 2 == 0 else color1) + f"{n:3d} "
                    f"{x['date']} {x['file']:{max_file}s} "
                    f"{x['metric']:8.5f} "
                    f"{x['duration']/3600:7.3f} "
                    f"{x['title']}"
                    for n, x in enumerate(self.data_filtered)
                ]
            )
        )

    def manage_results(self):
        """Manage results showed in the summary
        return True if excel file is created False otherwise
        """

        def process_file(num, command, path):
            num = int(num)
            name = self.data_filtered[num]["file"]
            file_name_result = os.path.join(path, name)
            verb1, verb2 = (
                ("delete", "Deleting")
                if command == cmd.delete
                else (
                    "hide",
                    "Hiding",
                )
            )
            conf_message = (
                TextColor.RED
                + f"Are you sure to {verb1} {file_name_result} (y/n)? "
            )
            confirm = get_input(message=conf_message)
            if confirm == "y":
                print(TextColor.YELLOW + f"{verb2} {file_name_result}")
                if command == cmd.delete:
                    os.unlink(file_name_result)
                else:
                    os.rename(
                        os.path.join(Folders.results, name),
                        os.path.join(Folders.hidden_results, name),
                    )
                self.data_filtered.pop(num)
                get_input(message="Press enter to continue")
                self.list_results()

        cmd = SimpleNamespace(
            quit="q", relist="r", delete="d", hide="h", excel="e"
        )
        message = (
            TextColor.ENDC
            + f"Choose option {str(cmd).replace('namespace', '')}: "
        )
        path = Folders.hidden_results if self.hidden else Folders.results
        book = None
        max_value = len(self.data_filtered)
        while True:
            match get_input(message=message).split():
                case [cmd.relist]:
                    self.list_results()
                case [cmd.quit]:
                    if book is not None:
                        book.close()
                        return True
                    return False
                case [cmd.hide, num] if num.isdigit() and int(num) < max_value:
                    if self.hidden:
                        print("Already hidden")
                    else:
                        process_file(num, path=path, command=cmd.hide)
                case [cmd.delete, num] if num.isdigit() and int(
                    num
                ) < max_value:
                    process_file(num=num, path=path, command=cmd.delete)
                case [cmd.excel, num] if num.isdigit() and int(
                    num
                ) < max_value:
                    # Add to excel file result #num
                    num = int(num)
                    file_name_result = os.path.join(
                        path, self.data_filtered[num]["file"]
                    )
                    if book is None:
                        file_name = os.path.join(
                            Folders.excel, Files.be_list_excel
                        )
                        book = xlsxwriter.Workbook(
                            file_name, {"nan_inf_to_errors": True}
                        )
                    excel = Excel(
                        file_name=file_name_result,
                        book=book,
                        compare=self.compare,
                    )
                    excel.report()
                    print(f"Added {file_name_result} to {Files.be_list_excel}")
                case [num] if num.isdigit() and int(num) < max_value:
                    # Report the result #num
                    num = int(num)
                    file_name_result = os.path.join(
                        path, self.data_filtered[num]["file"]
                    )
                    try:
                        rep = Report(file_name_result, compare=self.compare)
                        rep.report()
                    except ValueError as e:
                        print(e)
                case _:
                    print("Invalid option. Try again!")

    def show_result(self, data: dict, title: str = "") -> None:
        def whites(n: int) -> str:
            return " " * n + color1 + "*"

        if data == {}:
            print(f"** {title} has No data **")
            return
        color1 = TextColor.CYAN
        color2 = TextColor.YELLOW
        file_name = data["file"]
        metric = data["metric"]
        result = StubReport(os.path.join(Folders.results, file_name))
        length = 81
        print(color1 + "*" * length)
        if title != "":
            print(
                "*"
                + color2
                + TextColor.BOLD
                + f"{title:^{length - 2}s}"
                + TextColor.ENDC
                + color1
                + "*"
            )
            print("*" + "-" * (length - 2) + "*")
        print("*" + whites(length - 2))
        print(
            "* "
            + color2
            + f"{result.data['title']:^{length - 4}}"
            + color1
            + " *"
        )
        print("*" + whites(length - 2))
        print(
            "* Model: "
            + color2
            + f"{result.data['model']:15s} "
            + color1
            + "Ver. "
            + color2
            + f"{result.data['version']:10s} "
            + color1
            + "Score: "
            + color2
            + f"{result.data['score_name']:10s} "
            + color1
            + "Metric: "
            + color2
            + f"{metric:10.7f}"
            + whites(length - 78)
        )
        print(color1 + "*" + whites(length - 2))
        print(
            "* Date : "
            + color2
            + f"{result.data['date']:15s}"
            + color1
            + " Time: "
            + color2
            + f"{result.data['time']:18s} "
            + color1
            + "Time Spent: "
            + color2
            + f"{result.data['duration']:9,.2f}"
            + color1
            + " secs."
            + whites(length - 78)
        )
        seeds = str(result.data["seeds"])
        seeds_len = len(seeds)
        print(
            "* Seeds: "
            + color2
            + f"{seeds:{seeds_len}s} "
            + color1
            + "Platform: "
            + color2
            + f"{result.data['platform']:17s} "
            + whites(length - 79)
        )
        print(
            "* Stratified: "
            + color2
            + f"{str(result.data['stratified']):15s}"
            + whites(length - 30)
        )
        print("* " + color2 + f"{file_name:60s}" + whites(length - 63))
        print(color1 + "*" + whites(length - 2))
        print(color1 + "*" * length)

    def best_results(self, criterion=None, value=None, score="accuracy", n=10):
        # First filter the same score results (accuracy, f1, ...)
        haystack = [x for x in self.data if x["score"] == score]
        haystack = (
            haystack
            if criterion is None or value is None
            else [x for x in haystack if x[criterion] == value]
        )
        if haystack == []:
            raise ValueError(NO_RESULTS)
        return (
            sorted(
                haystack,
                key=lambda x: -1.0 if math.isnan(x["metric"]) else x["metric"],
                reverse=True,
            )[:n]
            if len(haystack) > 0
            else {}
        )

    def best_result(
        self, criterion=None, value=None, score="accuracy"
    ) -> dict:
        return self.best_results(criterion, value, score)[0]

    def best_results_datasets(self, score="accuracy") -> dict:
        """Get the best results for each dataset"""
        dt = Datasets()
        best_results = {}
        for dataset in dt:
            best_results[dataset] = (1, "", "", "")
        haystack = [x for x in self.data if x["score"] == score]
        # Search for the best results for each dataset
        for entry in haystack:
            for dataset in self.datasets[entry["file"]]:
                if dataset["score"] < best_results[dataset["dataset"]][0]:
                    best_results[dataset["dataset"]] = (
                        dataset["score"],
                        dataset["hyperparameters"],
                        entry["file"],
                        entry["title"],
                    )
        return best_results

    def show_top(self, score="accuracy", n=10):
        try:
            self.list_results(
                score=score,
                input_data=self.best_results(score=score, n=n),
                sort_key="metric",
            )
        except ValueError as e:
            print(e)


class PairCheck:
    def __init__(self, score, model_a, model_b, winners=False, losers=False):
        self.score = score
        self.model_a = model_a
        self.model_b = model_b
        self.show_winners = winners
        self.show_losers = losers
        self.winners = []
        self.losers = []
        self.tie = []

    def compute(self):
        summary = Summary()
        summary.acquire()
        best_a = summary.best_result(
            criterion="model", value=self.model_a, score=self.score
        )
        self.file_a = best_a["file"]
        best_b = summary.best_result(
            criterion="model", value=self.model_b, score=self.score
        )
        self.file_b = best_b["file"]
        report_a = StubReport(os.path.join(Folders.results, best_a["file"]))
        report_a.report()
        self.score_a = report_a.score
        report_b = StubReport(os.path.join(Folders.results, best_b["file"]))
        report_b.report()
        self.score_b = report_b.score
        for result_a, result_b in zip(report_a.lines, report_b.lines):
            result = result_a["score"] - result_b["score"]
            self._store_result(result, result_a["dataset"])

    def _store_result(self, result, dataset):
        if result > 0:
            self.winners.append(dataset)
        elif result < 0:
            self.losers.append(dataset)
        else:
            self.tie.append(dataset)

    def report(self):
        print(f"{'Model':<20} {'File':<70} {'Score':<10} Win Tie Lose")
        print("=" * 20 + " " + "=" * 70 + " " + "=" * 10 + " === === ====")
        print(f"{self.model_a:<20} {self.file_a:<70} {self.score_a:10.5f}")
        print(
            f"{self.model_b:<20} {self.file_b:<70} "
            f"{self.score_b:10.5f} "
            f"{TextColor.GREEN}{len(self.winners):3d} {TextColor.YELLOW}"
            f"{len(self.tie):3d} {TextColor.RED}{len(self.losers):4d}"
        )
        if self.show_winners:
            print(TextColor.GREEN + "Winners:")
            print(self.winners)
        if self.show_losers:
            print(TextColor.RED + "losers:")
            print(self.losers)
