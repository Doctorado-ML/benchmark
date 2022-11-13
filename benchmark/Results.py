import os
import sys
from operator import itemgetter
import math
import json
import abc
import shutil
import subprocess
import xlsxwriter
import numpy as np
from .Experiments import BestResults
from .Datasets import Datasets
from .Arguments import EnvData, ALL_METRICS
from .Utils import (
    Folders,
    Files,
    Symbols,
    TextColor,
    NO_RESULTS,
)
from ._version import __version__


class BestResultsEver:
    def __init__(self):
        self.data = {}
        for i in ["Tanveer", "Surcov", "Arff"]:
            self.data[i] = {}
            for metric in ALL_METRICS:
                self.data[i][metric.replace("-", "_")] = ["self", 1.0]
                self.data[i][metric] = ["self", 1.0]
        self.data["Tanveer"]["accuracy"] = [
            "STree_default (liblinear-ovr)",
            40.282203,
        ]
        self.data["Arff"]["accuracy"] = [
            "STree_default (linear-ovo)",
            22.063496,
        ]

    def get_name_value(self, key, score):
        return self.data[key][score]


class BaseReport(abc.ABC):
    def __init__(self, file_name, best_file=False):
        self.file_name = file_name
        if not os.path.isfile(file_name):
            if not os.path.isfile(os.path.join(Folders.results, file_name)):
                raise FileNotFoundError(f"{file_name} does not exists!")
            else:
                self.file_name = os.path.join(Folders.results, file_name)
        with open(self.file_name) as f:
            self.data = json.load(f)
        self.best_acc_file = best_file
        if best_file:
            self.lines = self.data
        else:
            self.lines = self.data["results"]
            self.score_name = self.data["score_name"]
        self.__compute_best_results_ever()

    def __compute_best_results_ever(self):
        args = EnvData.load()
        key = args["source_data"]
        best = BestResultsEver()
        self.best_score_name, self.best_score_value = best.get_name_value(
            key, self.score_name
        )

    def _get_accuracy(self, item):
        return self.data[item][0] if self.best_acc_file else item["score"]

    def report(self):
        self.header()
        accuracy_total = 0.0
        for result in self.lines:
            self.print_line(result)
            accuracy_total += self._get_accuracy(result)
        self.footer(accuracy_total)

    def _load_best_results(self, score, model):
        best = BestResults(score, model, Datasets())
        self.best_results = best.load({})

    def _compute_status(self, dataset, accuracy: float):
        best = self.best_results[dataset][0]
        status = " "
        if accuracy == best:
            status = Symbols.equal_best
        elif accuracy > best:
            status = Symbols.better_best
        if status != " ":
            if status not in self._compare_totals:
                self._compare_totals[status] = 1
            else:
                self._compare_totals[status] += 1
        return status

    @staticmethod
    def _status_meaning(status):
        meaning = {
            Symbols.equal_best: "Equal to best",
            Symbols.better_best: "Better than best",
        }
        return meaning[status]

    def _get_best_accuracy(self):
        return self.best_score_value

    def _get_message_best_accuracy(self):
        return f"{self.score_name} compared to {self.best_score_name} .:"

    @abc.abstractmethod
    def header(self) -> None:
        pass

    @abc.abstractmethod
    def print_line(self, result) -> None:
        pass

    @abc.abstractmethod
    def footer(self, accuracy: float) -> None:
        pass


class Report(BaseReport):
    header_lengths = [30, 6, 5, 3, 7, 7, 7, 15, 16, 15]
    header_cols = [
        "Dataset",
        "Sampl.",
        "Feat.",
        "Cls",
        "Nodes",
        "Leaves",
        "Depth",
        "Score",
        "Time",
        "Hyperparameters",
    ]

    def __init__(self, file_name: str, compare: bool = False):
        super().__init__(file_name)
        self.nline = 0
        self.compare = compare

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
        if self.compare:
            status = self._compute_status(result["dataset"], result["score"])
        else:
            status = " "
        print(
            f"{result['score']:8.6f}±{result['score_std']:6.4f}{status}",
            end="",
        )
        i += 1
        print(
            f"{result['time']:9.6f}±{result['time_std']:6.4f} ",
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
            f"{self.data['stratified']}"
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
        if self.compare:
            for key, value in self._compare_totals.items():
                self.header_line(
                    f" {key} {self._status_meaning(key)} .....: {value:2d}"
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

    def __init__(self, score, model, best, grid):
        name = (
            Files.best_results(score, model)
            if best
            else Files.grid_output(score, model)
        )
        file_name = os.path.join(Folders.results, name)
        self.best = best
        self.grid = grid
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


class Excel(BaseReport):
    row = 6
    # alternate lines colors
    color1 = "#DCE6F1"
    color2 = "#FDE9D9"
    color3 = "#B1A0C7"

    def __init__(self, file_name, compare=False, book=None):
        super().__init__(file_name)
        self.compare = compare
        if self.compare:
            self._load_best_results(
                self.data["score_name"], self.data["model"]
            )
            self._compare_totals = {}
        if book is None:
            self.excel_file_name = self.file_name.replace(".json", ".xlsx")
            self.book = xlsxwriter.Workbook(
                self.excel_file_name, {"nan_inf_to_errors": True}
            )
            self.set_book_properties()
            self.close = True
        else:
            self.book = book
            self.close = False
        self.sheet = self.book.add_worksheet(self.data["model"])
        self.max_hyper_width = 0
        self.col_hyperparams = 0

    @staticmethod
    def set_properties(book, title):
        book.set_properties(
            {
                "title": title,
                "subject": "Machine learning results",
                "author": "Ricardo Montañana Gómez",
                "manager": "Dr. J. A. Gámez, Dr. J. M. Puerta",
                "company": "UCLM",
                "comments": "Created with Python and XlsxWriter",
            }
        )

    def set_book_properties(self):
        self.set_properties(self.book, self.get_title())

    def get_title(self):
        return (
            f" {self.data['model']} ver. {self.data['version']}"
            f" {self.data['language']} ver. {self.data['language_version']}"
            f" with {self.data['folds']} Folds "
            f"cross validation and {len(self.data['seeds'])} random seeds. "
            f"{self.data['date']} {self.data['time']}"
        )

    def get_file_name(self):
        return self.excel_file_name

    def header(self):
        merge_format = self.book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 18,
                "bg_color": self.color3,
            }
        )
        merge_format_subheader = self.book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 16,
                "bg_color": self.color1,
            }
        )
        merge_format_subheader_left = self.book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "left",
                "valign": "vcenter",
                "font_size": 12,
                "bg_color": self.color1,
            }
        )
        header_text = self.get_title()
        self.sheet.merge_range(0, 0, 0, 11, header_text, merge_format)
        self.sheet.merge_range(
            1, 0, 1, 11, f" {self.data['title']}", merge_format_subheader
        )
        self.sheet.merge_range(
            2,
            0,
            3,
            0,
            f" Score is {self.data['score_name']}",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            2,
            1,
            3,
            3,
            " Execution time",
            merge_format_subheader,
        )
        hours = self.data["duration"] / 3600
        self.sheet.merge_range(
            2,
            4,
            2,
            5,
            f"{self.data['duration']:7,.2f} s",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            3,
            4,
            3,
            5,
            f" {hours:5.2f} h",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            2,
            6,
            3,
            6,
            " ",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            2,
            7,
            3,
            7,
            "Platform",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            2,
            8,
            3,
            8,
            f"{self.data['platform']}",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            2,
            9,
            2,
            11,
            f"Random seeds: {self.data['seeds']}",
            merge_format_subheader_left,
        )
        self.sheet.merge_range(
            3,
            9,
            3,
            11,
            f"Stratified: {self.data['stratified']}",
            merge_format_subheader_left,
        )
        header_cols = [
            ("Dataset", 30),
            ("Samples", 10),
            ("Features", 7),
            ("Classes", 7),
            ("Nodes", 7),
            ("Leaves", 7),
            ("Depth", 7),
            ("Score", 12),
            ("Score Std.", 12),
            ("Time", 12),
            ("Time Std.", 12),
            ("Hyperparameters", 50),
        ]
        if self.compare:
            header_cols.insert(8, ("Stat", 3))
        bold = self.book.add_format(
            {
                "bold": True,
                "font_size": 14,
                "bg_color": self.color3,
                "border": 1,
            }
        )
        i = 0
        for item, length in header_cols:
            self.sheet.write(5, i, item, bold)
            self.sheet.set_column(i, i, length)
            i += 1

    def print_line(self, result):
        size_n = 14
        decimal = self.book.add_format(
            {"num_format": "0.000000", "font_size": size_n, "border": 1}
        )
        integer = self.book.add_format(
            {"num_format": "#,###", "font_size": size_n, "border": 1}
        )
        normal = self.book.add_format({"font_size": size_n, "border": 1})
        col = 0
        if self.row % 2 == 0:
            normal.set_bg_color(self.color1)
            decimal.set_bg_color(self.color1)
            integer.set_bg_color(self.color1)
        else:
            normal.set_bg_color(self.color2)
            decimal.set_bg_color(self.color2)
            integer.set_bg_color(self.color2)
        self.sheet.write(self.row, col, result["dataset"], normal)
        self.sheet.write(self.row, col + 1, result["samples"], integer)
        self.sheet.write(self.row, col + 2, result["features"], integer)
        self.sheet.write(self.row, col + 3, result["classes"], normal)
        self.sheet.write(self.row, col + 4, result["nodes"], normal)
        self.sheet.write(self.row, col + 5, result["leaves"], normal)
        self.sheet.write(self.row, col + 6, result["depth"], normal)
        self.sheet.write(self.row, col + 7, result["score"], decimal)
        if self.compare:
            status = self._compute_status(result["dataset"], result["score"])
            self.sheet.write(self.row, col + 8, status, normal)
            col = 9
        else:
            col = 8
        self.sheet.write(self.row, col, result["score_std"], decimal)
        self.sheet.write(self.row, col + 1, result["time"], decimal)
        self.sheet.write(self.row, col + 2, result["time_std"], decimal)
        self.sheet.write(
            self.row, col + 3, str(result["hyperparameters"]), normal
        )
        self.col_hyperparams = col + 3
        self.max_hyper_width = max(
            self.max_hyper_width, len(str(result["hyperparameters"]))
        )
        self.row += 1

    def footer(self, accuracy):
        if self.compare:
            self.row += 2
            bold = self.book.add_format({"bold": True, "font_size": 16})
            for key, total in self._compare_totals.items():
                self.sheet.write(self.row, 1, key, bold)
                self.sheet.write(self.row, 2, total, bold)
                self.sheet.write(self.row, 3, self._status_meaning(key), bold)
                self.row += 1
        message = (
            f"** {self._get_message_best_accuracy()} "
            f"{accuracy/self._get_best_accuracy():7.4f}"
        )
        bold = self.book.add_format({"bold": True, "font_size": 14})
        # set width of the hyperparams column with the maximum width
        self.sheet.set_column(
            self.col_hyperparams,
            self.col_hyperparams,
            max(self.max_hyper_width + 1, 23),
        )
        self.sheet.write(self.row + 1, 0, message, bold)
        for c in range(self.row + 2):
            self.sheet.set_row(c, 20)
        self.sheet.set_row(0, 25)
        self.sheet.freeze_panes(6, 1)
        self.sheet.hide_gridlines(2)
        if self.close:
            self.book.close()


class ReportDatasets:
    row = 6
    # alternate lines colors
    color1 = "#DCE6F1"
    color2 = "#FDE9D9"
    color3 = "#B1A0C7"

    def __init__(self, excel, book=None):
        self.excel = excel
        self.env = EnvData().load()
        self.close = False
        self.output = True
        self.header_text = f"Datasets used in benchmark ver. {__version__}"
        if excel:
            self.max_length = 0
            if book is None:
                self.excel_file_name = "ReportDatasets.xlsx"
                self.book = xlsxwriter.Workbook(
                    self.excel_file_name, {"nan_inf_to_errors": True}
                )
                self.set_properties(self.get_title())
                self.close = True
            else:
                self.book = book
                self.output = False
            self.sheet = self.book.add_worksheet("Datasets")

    def set_properties(self, title):
        self.book.set_properties(
            {
                "title": title,
                "subject": "Machine learning results",
                "author": "Ricardo Montañana Gómez",
                "manager": "Dr. J. A. Gámez, Dr. J. M. Puerta",
                "company": "UCLM",
                "comments": "Created with Python and XlsxWriter",
            }
        )

    @staticmethod
    def get_python_version():
        return "{}.{}".format(sys.version_info.major, sys.version_info.minor)

    def get_title(self):
        return (
            f" Benchmark ver. {__version__} - "
            f" Python ver. {self.get_python_version()}"
            f" with {self.env['n_folds']} Folds cross validation "
            f" Discretization: {self.env['discretize']}  "
            f"Stratification: {self.env['stratified']}"
        )

    def get_file_name(self):
        return self.excel_file_name

    def header(self):
        merge_format = self.book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 18,
                "bg_color": self.color3,
            }
        )
        merge_format_subheader = self.book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 16,
                "bg_color": self.color1,
            }
        )
        merge_format_subheader_right = self.book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "right",
                "valign": "vcenter",
                "font_size": 16,
                "bg_color": self.color1,
            }
        )
        merge_format_subheader_left = self.book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "left",
                "valign": "vcenter",
                "font_size": 16,
                "bg_color": self.color1,
            }
        )
        self.sheet.merge_range(0, 0, 0, 4, self.header_text, merge_format)
        self.sheet.merge_range(
            1,
            0,
            4,
            0,
            f" Default score {self.env['score']}",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            1,
            1,
            1,
            3,
            "Cross validation",
            merge_format_subheader_right,
        )
        self.sheet.write(
            1, 4, f"{self.env['n_folds']} Folds", merge_format_subheader_left
        )
        self.sheet.merge_range(
            2,
            1,
            2,
            3,
            "Stratified",
            merge_format_subheader_right,
        )
        self.sheet.write(
            2,
            4,
            f"{'True' if self.env['stratified']=='1' else 'False'}",
            merge_format_subheader_left,
        )
        self.sheet.merge_range(
            3,
            1,
            3,
            3,
            "Discretized",
            merge_format_subheader_right,
        )
        self.sheet.write(
            3,
            4,
            f"{'True' if self.env['discretize']=='1' else 'False'}",
            merge_format_subheader_left,
        )
        self.sheet.merge_range(
            4,
            1,
            4,
            3,
            "Seeds",
            merge_format_subheader_right,
        )
        self.sheet.write(
            4, 4, f"{self.env['seeds']}", merge_format_subheader_left
        )
        header_cols = [
            ("Dataset", 30),
            ("Samples", 10),
            ("Features", 10),
            ("Classes", 10),
            ("Balance", 50),
        ]
        bold = self.book.add_format(
            {
                "bold": True,
                "font_size": 14,
                "bg_color": self.color3,
                "border": 1,
            }
        )
        i = 0
        for item, length in header_cols:
            self.sheet.write(5, i, item, bold)
            self.sheet.set_column(i, i, length)
            i += 1

    def footer(self):
        # set Balance column width to max length
        self.sheet.set_column(4, 4, self.max_length)
        self.sheet.freeze_panes(6, 1)
        self.sheet.hide_gridlines(2)
        if self.close:
            self.book.close()

    def print_line(self, result):
        size_n = 14
        integer = self.book.add_format(
            {"num_format": "#,###", "font_size": size_n, "border": 1}
        )
        normal = self.book.add_format({"font_size": size_n, "border": 1})
        col = 0
        if self.row % 2 == 0:
            normal.set_bg_color(self.color1)
            integer.set_bg_color(self.color1)
        else:
            normal.set_bg_color(self.color2)
            integer.set_bg_color(self.color2)
        self.sheet.write(self.row, col, result.dataset, normal)
        self.sheet.write(self.row, col + 1, result.samples, integer)
        self.sheet.write(self.row, col + 2, result.features, integer)
        self.sheet.write(self.row, col + 3, result.classes, normal)
        self.sheet.write(self.row, col + 4, result.balance, normal)
        if len(result.balance) > self.max_length:
            self.max_length = len(result.balance)
        self.row += 1

    def report(self):
        data_sets = Datasets()
        color_line = TextColor.LINE1
        if self.excel:
            self.header()
        if self.output:
            print(color_line, end="")
            print(self.header_text)
            print("")
            print(f"{'Dataset':30s} Sampl. Feat. Cls Balance")
            print("=" * 30 + " ===== ====== === " + "=" * 60)
        for dataset in data_sets:
            attributes = data_sets.get_attributes(dataset)
            attributes.dataset = dataset
            if self.excel:
                self.print_line(attributes)
            color_line = (
                TextColor.LINE2
                if color_line == TextColor.LINE1
                else TextColor.LINE1
            )
            if self.output:
                print(color_line, end="")
                print(
                    f"{dataset:30s} {attributes.samples:6,d} "
                    f"{attributes.features:5,d} {attributes.classes:3d} "
                    f"{attributes.balance:40s}"
                )
        if self.excel:
            self.footer()


class SQL(BaseReport):
    table_name = "results"

    def header(self):
        file_name = self.file_name.replace(".json", ".sql")
        self.file = open(file_name, "w")

    def print_line(self, result):
        attributes = [
            "date",
            "time",
            "type",
            "title",
            "stratified",
            "score_name",
            "score",
            "score_std",
            "dataset",
            "classifier",
            "version",
            "norm",
            "stand",
            "time_spent",
            "time_spent_std",
            "parameters",
            "nodes",
            "leaves",
            "depth",
            "platform",
            "nfolds",
            "seeds",
        ]
        command_insert = (
            f"replace into {self.table_name} ("
            + ",".join(attributes)
            + ") values("
            + ("'%s'," * len(attributes))[:-1]
            + ");\n"
        )
        values = (
            self.data["date"],
            self.data["time"],
            "crossval",
            self.data["title"],
            "1" if self.data["stratified"] else "0",
            self.data["score_name"],
            result["score"],
            result["score_std"],
            result["dataset"],
            self.data["model"],
            self.data["version"],
            0,
            1,
            result["time"],
            result["time_std"],
            str(result["hyperparameters"]).replace("'", '"'),
            result["nodes"],
            result["leaves"],
            result["depth"],
            self.data["platform"],
            self.data["folds"],
            str(self.data["seeds"]),
        )
        self.file.write(command_insert % values)

    def footer(self, accuracy):
        self.file.close()


class Benchmark:
    def __init__(self, score, visualize=True):
        self._score = score
        self._results = []
        self._models = []
        self._report = {}
        self._datasets = set()
        self.visualize = visualize
        self.__compute_best_results_ever()

    def __compute_best_results_ever(self):
        args = EnvData.load()
        key = args["source_data"]
        best = BestResultsEver()
        _, self.best_score_value = best.get_name_value(key, self._score)

    def get_result_file_name(self):
        return os.path.join(Folders.exreport, Files.exreport(self._score))

    def compile_results(self):
        summary = Summary()
        summary.acquire(given_score=self._score)
        self._models = summary.get_models()
        if self._models == []:
            raise ValueError(NO_RESULTS)
        for model in self._models:
            best = summary.best_result(
                criterion="model", value=model, score=self._score
            )
            file_name = os.path.join(Folders.results, best["file"])
            with open(file_name) as fi:
                experiment = json.load(fi)
                for result in experiment["results"]:
                    dataset = result["dataset"]
                    record = {
                        "model": model,
                        "dataset": dataset,
                        "score": result["score"],
                        "score_std": result["score_std"],
                        "file_name": file_name,
                    }
                    self._results.append(record)
                    if model not in self._report:
                        self._report[model] = {}
                    self._report[model][dataset] = record
                    self._datasets.add(dataset)
        self._datasets = sorted(self._datasets)

    def save_results(self):
        # build Files.exreport
        result_file_name = self.get_result_file_name()
        with open(result_file_name, "w") as f:
            f.write(
                f"classifier, dataset, {self._score.replace('-','')}, "
                "stdev, file_name\n"
            )
            for record in self._results:
                f.write(
                    f"{record['model']}, {record['dataset']}, "
                    f"{record['score']}, {record['score_std']}, "
                    f"{record['file_name']}\n"
                )

    def exreport(self):
        def end_message(message, file):
            length = 100
            print("*" * length)
            print(message)
            print("*" * length)
            with open(os.path.join(Folders.exreport, file)) as f:
                data = f.read().splitlines()
                for line in data:
                    print(line)

        # Remove previous results
        if os.path.exists(Folders.report):
            shutil.rmtree(Folders.report)
        if os.path.exists(Files.exreport_pdf):
            os.remove(Files.exreport_pdf)
        # Compute Friedman & Holm Tests
        fout = open(
            os.path.join(Folders.exreport, Files.exreport_output(self._score)),
            "w",
        )
        ferr = open(
            os.path.join(Folders.exreport, Files.exreport_err(self._score)),
            "w",
        )
        result = subprocess.run(
            [
                "Rscript",
                os.path.join(Folders.src(), Files.benchmark_r),
                self._score.replace("-", ""),
                os.path.join(Folders.exreport, f"exreport_{self._score}"),
                "1" if self.visualize else "0",
            ],
            stdout=fout,
            stderr=ferr,
        )
        fout.close()
        ferr.close()
        if result.returncode != 0:
            end_message(
                "Error computing benchmark", Files.exreport_err(self._score)
            )
        else:
            end_message("Benchmark Ok", Files.exreport_output(self._score))
        Files.open(Files.exreport_pdf)

    def report(self, tex_output):
        # Report Header
        print(f"{'Dataset':30s} ", end="")
        lines = "=" * 30 + " "
        for model in self._models:
            print(f"{model:^13s} ", end="")
            lines += "=" * 13 + " "
        print(f"\n{lines}")
        if tex_output:
            self.print_tex_header()
        # Report Body
        for num, dataset in enumerate(self._datasets):
            print(f"{dataset:30s} ", end="")
            scores = []
            for model in self._models:
                result = self._report[model][dataset]
                score = float(result["score"])
                score_std = float(result["score_std"])
                print(f"{score:.5f}±", end="")
                print(f"{score_std:.3f} ", end="")
                scores.append((score, score_std))
            print("")
            if tex_output:
                self.print_tex_line(num, dataset, scores)
        if tex_output:
            self.print_tex_footer()
        # Summary of result files used
        d_name = next(iter(self._datasets))
        print(f"\n{'Model':30s} {'File Name':75s} Score")
        print("=" * 30 + " " + "=" * 75 + " ========")
        for model in self._models:
            file_name = self._report[model][d_name]["file_name"]
            report = StubReport(file_name)
            report.report()
            print(f"{model:^30s} {file_name:75s} {report.score:8.5f}")

    def get_tex_file(self):
        return os.path.join(Folders.exreport, Files.tex_output(self._score))

    def print_tex_header(self):
        with open(self.get_tex_file(), "w") as f:
            header_data = "# & Dataset & \\#S & \\#F & \\#L & " + " & ".join(
                self._models
            )
            tabular = "{rlrrr" + "c" * len(self._models) + "}"
            header = (
                "\\begin{sidewaystable}[ht]\n"
                "\\centering\n"
                "\\renewcommand{\\arraystretch}{1.2}\n"
                "\\renewcommand{\\tabcolsep}{0.07cm}\n"
                "\\caption{Accuracy results (mean ± std) for all the "
                "algorithms and datasets}\n"
                "\\label{table:datasets}\n"
                "\\resizebox{0.95\\textwidth}{!}{\n"
                "\\begin {tabular} {" + tabular + "}\\hline\n"
                "\\" + header_data + "\\\\\n"
                "\\hline\n"
            )
            f.write(header)

    def print_tex_line(self, num, dataset, scores):
        dt = Datasets()
        with open(self.get_tex_file(), "a") as f:
            X, y = dt.load(dataset)
            samples, features = X.shape
            n_classes = len(np.unique(y))
            dataset_name = dataset.replace("_", "\\_")
            print_line = (
                f"{num + 1} & {dataset_name} & {samples} & {features} "
                f"& {n_classes}"
            )
            max_value = max(scores)[0]
            for score, score_std in scores:
                # Add score and score_std
                value = f"{score:.4f}±{score_std:.3f}"
                value_formated = (
                    "\\bfseries " + value + " "
                    if score == max_value
                    else value
                )
                print_line += " & " + value_formated
            print_line += "\\\\"
            f.write(f"{print_line}\n")

    def print_tex_footer(self):
        with open(self.get_tex_file(), "a") as f:
            f.write("\\hline\n\\end{tabular}}\n\\end{sidewaystable}\n")

    def get_excel_file_name(self):
        return os.path.join(
            Folders.exreport, Files.exreport_excel(self._score)
        )

    def excel(self):
        book = xlsxwriter.Workbook(
            self.get_excel_file_name(), {"nan_inf_to_errors": True}
        )
        Excel.set_properties(book, "Experimentation summary")
        sheet = book.add_worksheet("Benchmark")
        normal = book.add_format({"font_size": 14, "border": 1})
        decimal = book.add_format(
            {"num_format": "0.000000", "font_size": 14, "border": 1}
        )
        decimal_total = book.add_format(
            {
                "num_format": "0.000000",
                "font_size": 14,
                "border": 1,
                "bold": True,
                "bg_color": Excel.color3,
            }
        )
        two_decimal_total = book.add_format(
            {
                "num_format": "0.00",
                "font_size": 14,
                "border": 1,
                "bold": True,
                "bg_color": Excel.color3,
            }
        )
        merge_format_header = book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 14,
                "bg_color": Excel.color1,
            }
        )
        merge_format = book.add_format(
            {
                "border": 1,
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 14,
                "bg_color": Excel.color3,
            }
        )
        merge_format_normal = book.add_format(
            {
                "border": 1,
                "valign": "vcenter",
                "font_size": 14,
            }
        )
        row = row_init = 4

        def header():
            nonlocal row
            sheet.merge_range(
                0, 0, 1, 0, "Benchmark of Models", merge_format_header
            )
            sheet.merge_range(
                0, 1, 1, 2, f"Score is {self._score}", merge_format_header
            )
            sheet.set_row(1, 20)
            # Set columns width
            sheet.set_column(0, 0, 40)
            for column in range(2 * len(self._results)):
                sheet.set_column(column + 1, column + 1, 15)
            # Set report header
            # Merge 2 rows
            sheet.merge_range(row, 0, row + 1, 0, "Dataset", merge_format)
            column = 1
            for model in self._models:
                # Merge 3 columns
                sheet.merge_range(
                    row, column, row, column + 2, model, merge_format
                )
                column += 3
            row += 1
            column = 1
            for _ in range(len(self._models)):
                sheet.write(row, column, "Score", merge_format)
                sheet.write(row, column + 1, "Stdev", merge_format)
                sheet.write(row, column + 2, "Rank", merge_format)
                column += 3

        def body():
            nonlocal row
            for dataset in self._datasets:
                row += 1
                normal = book.add_format({"font_size": 14, "border": 1})
                decimal = book.add_format(
                    {
                        "num_format": "0.000000",
                        "font_size": 14,
                        "border": 1,
                    }
                )
                if row % 2 == 0:
                    normal.set_bg_color(Excel.color1)
                    decimal.set_bg_color(Excel.color1)
                else:
                    normal.set_bg_color(Excel.color2)
                    decimal.set_bg_color(Excel.color2)
                sheet.write(row, 0, f"{dataset:30s}", normal)
                column = 1
                range_cells = ""
                for col in range(0, len(self._models) * 3, 3):
                    range_cells += chr(ord("B") + col) + str(row + 1) + ","
                range_cells = range_cells[:-1]
                for model in self._models:
                    sheet.write(
                        row,
                        column,
                        float(self._report[model][dataset]["score"]),
                        decimal,
                    )
                    column += 1
                    sheet.write(
                        row,
                        column,
                        float(self._report[model][dataset]["score_std"]),
                        decimal,
                    )
                    column += 1
                    cell_target = chr(ord("B") + column - 3) + str(row + 1)
                    sheet.write_formula(
                        row,
                        column,
                        f"=rank({cell_target},({range_cells}))",
                        normal,
                    )
                    column += 1

        def footer():
            nonlocal row
            for c in range(row_init, row + 2):
                sheet.set_row(c, 20)
            # Write totals
            row += 1
            sheet.write(row, 0, "Total", merge_format)
            for col in range(0, len(self._models) * 3, 3):
                range_metric = (
                    f"{chr(ord('B') + col )}7:{chr(ord('B') + col )}{row}"
                )
                sheet.write_formula(
                    row,
                    col + 1,
                    f"=sum({range_metric})/{self.best_score_value}",
                    decimal_total,
                )
                range_rank = (
                    f"{chr(ord('B') + col + 2)}7:"
                    f"{chr(ord('B') + col + 2)}{row}"
                )
                sheet.write_formula(
                    row,
                    col + 3,
                    f"=average({range_rank})",
                    two_decimal_total,
                )
            row += 1

        def models_files():
            nonlocal row
            row += 2
            # Set report header
            # Merge 2 rows
            sheet.merge_range(row, 0, row + 1, 0, "Model", merge_format)
            sheet.merge_range(row, 1, row + 1, 5, "File", merge_format)
            sheet.merge_range(row, 6, row + 1, 6, "Score", merge_format)
            sheet.freeze_panes(6, 1)
            sheet.hide_gridlines(2)
            d_name = next(iter(self._datasets))
            for model in self._models:
                file_name = self._report[model][d_name]["file_name"]
                report = StubReport(file_name)
                report.report()
                row += 1
                sheet.write(
                    row,
                    0,
                    model,
                    normal,
                )
                sheet.merge_range(
                    row, 1, row, 5, file_name, merge_format_normal
                )
                sheet.write(
                    row,
                    6,
                    report.score,
                    decimal,
                )
                k = Excel(file_name=file_name, book=book)
                k.report()

            # Add datasets sheet
            re = ReportDatasets(excel=True, book=book)
            re.report()

        def exreport_output():
            file_name = os.path.join(
                Folders.exreport, Files.exreport_output(self._score)
            )
            sheet = book.add_worksheet("Exreport")
            normal = book.add_format(
                {
                    "font_size": 14,
                    "border": 1,
                    "font_color": "blue",
                    "font_name": "Courier",
                    "bold": True,
                }
            )
            with open(file_name) as f:
                lines = f.read().splitlines()
            row = 0
            for line in lines:
                sheet.write(row, 0, line, normal)
                row += 1

        header()
        body()
        footer()
        models_files()
        exreport_output()
        book.close()


class StubReport(BaseReport):
    def __init__(self, file_name):
        super().__init__(file_name=file_name, best_file=False)

    def print_line(self, line) -> None:
        pass

    def header(self) -> None:
        self.title = self.data["title"]
        self.duration = self.data["duration"]

    def footer(self, accuracy: float) -> None:
        self.accuracy = accuracy
        self.score = accuracy / self._get_best_accuracy()


class Summary:
    def __init__(self, hidden=False) -> None:
        self.results = Files().get_all_results(hidden=hidden)
        self.data = []
        self.datasets = {}
        self.models = set()
        self.hidden = hidden

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
        self,
        score,
        model,
        input_data,
        sort_key,
        number,
    ):
        data = self.data.copy() if input_data is None else input_data
        if score:
            data = [x for x in data if x["score"] == score]
        if model:
            data = [x for x in data if x["model"] == model]
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
    ) -> None:
        """Print the list of results"""
        data = self.get_results_criteria(
            score, model, input_data, sort_key, number
        )
        if data == []:
            raise ValueError(NO_RESULTS)
        max_file = max(len(x["file"]) for x in data)
        max_title = max(len(x["title"]) for x in data)
        if self.hidden:
            color1 = TextColor.GREEN
            color2 = TextColor.YELLOW
        else:
            color1 = TextColor.LINE1
            color2 = TextColor.LINE2
        print(color1, end="")
        print(
            f"{'Date':10s} {'File':{max_file}s} {'Score':8s} {'Time(h)':7s} "
            f"{'Title':s}"
        )
        print(
            "=" * 10
            + " "
            + "=" * max_file
            + " "
            + "=" * 8
            + " "
            + "=" * 7
            + " "
            + "=" * max_title
        )
        print(
            "\n".join(
                [
                    (color2 if n % 2 == 0 else color1)
                    + f"{x['date']} {x['file']:{max_file}s} "
                    f"{x['metric']:8.5f} "
                    f"{x['duration']/3600:7.3f} "
                    f"{x['title']}"
                    for n, x in enumerate(data)
                ]
            )
        )

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
