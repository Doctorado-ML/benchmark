import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import xlsxwriter
from xlsxwriter.exceptions import DuplicateWorksheetName

from ._version import __version__
from .Arguments import EnvData
from .Datasets import Datasets
from .ResultsBase import BaseReport, BestResultsEver, Summary, StubReport
from .Utils import NO_RESULTS, Files, Folders, TextColor


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
            self.excel_file_name = Path(self.file_name).name.replace(
                Files.report_ext, ".xlsx"
            )
            self.book = xlsxwriter.Workbook(
                os.path.join(Folders.excel, self.excel_file_name),
                {"nan_inf_to_errors": True},
            )
            self.set_book_properties()
            self.close = True
        else:
            self.book = book
            self.close = False
        suffix = ""
        num = 1
        while True:
            try:
                self.sheet = self.book.add_worksheet(
                    self.data["model"] + suffix
                )
                break
            except DuplicateWorksheetName:
                num += 1
                suffix = str(num)
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
        self.sheet.merge_range(0, 0, 0, 12, header_text, merge_format)
        self.sheet.merge_range(
            1, 0, 1, 12, f" {self.data['title']}", merge_format_subheader
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
            7,
            "Platform",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            2,
            8,
            3,
            9,
            f"{self.data['platform']}",
            merge_format_subheader,
        )
        self.sheet.merge_range(
            2,
            10,
            2,
            12,
            f"Random seeds: {self.data['seeds']}",
            merge_format_subheader_left,
        )
        self.sheet.merge_range(
            3,
            10,
            3,
            11,
            f"Stratified: {self.data['stratified']}",
            merge_format_subheader_left,
        )
        self.sheet.write(
            3,
            12,
            f"Discretized: {self.data['discretized']}",
            merge_format_subheader_left,
        )
        header_cols = [
            ("Dataset", 30),
            ("Samples", 10),
            ("Features", 7),
            ("Classes", 7),
            (self.nodes_label, 7),
            (self.leaves_label, 7),
            (self.depth_label, 7),
            ("Score", 12),
            ("Score Std.", 12),
            ("Time", 12),
            ("Time Std.", 12),
            ("Hyperparameters", 50),
        ]
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
        status = self._compute_status(result["dataset"], result["score"])
        self.sheet.write(self.row, col + 8, status, normal)
        col = 9
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

    def __init__(self, excel=False, book=None, output=True):
        self.excel = excel
        self.env = EnvData().load()
        self.close = False
        self.output = output
        self.header_text = f"Datasets used in benchmark ver. {__version__}"
        if excel:
            self.max_length = 0
            if book is None:
                self.excel_file_name = os.path.join(
                    Folders.excel, Files.datasets_report_excel
                )
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
        self.sheet.merge_range(0, 0, 0, 5, self.header_text, merge_format)
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
            4,
            "Cross validation",
            merge_format_subheader_right,
        )
        self.sheet.write(
            1, 5, f"{self.env['n_folds']} Folds", merge_format_subheader_left
        )
        self.sheet.merge_range(
            2,
            1,
            2,
            4,
            "Stratified",
            merge_format_subheader_right,
        )
        self.sheet.write(
            2,
            5,
            f"{'True' if self.env['stratified']=='1' else 'False'}",
            merge_format_subheader_left,
        )
        self.sheet.merge_range(
            3,
            1,
            3,
            4,
            "Discretized",
            merge_format_subheader_right,
        )
        self.sheet.write(
            3,
            5,
            f"{'True' if self.env['discretize']=='1' else 'False'}",
            merge_format_subheader_left,
        )
        self.sheet.merge_range(
            4,
            1,
            4,
            4,
            "Seeds",
            merge_format_subheader_right,
        )
        self.sheet.write(
            4, 5, f"{self.env['seeds']}", merge_format_subheader_left
        )
        self.update_max_length(len(self.env["seeds"]) + 1)
        header_cols = [
            ("Dataset", 30),
            ("Samples", 10),
            ("Features", 10),
            ("Continuous", 10),
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
        self.sheet.set_column(5, 5, self.max_length)
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
        self.sheet.write(self.row, col + 3, result.cont_features, integer)
        self.sheet.write(self.row, col + 4, result.classes, normal)
        self.sheet.write(self.row, col + 5, result.balance, normal)
        self.update_max_length(len(result.balance))
        self.row += 1

    def update_max_length(self, value):
        if value > self.max_length:
            self.max_length = value

    def report(self):
        data_sets = Datasets()
        max_len = max(
            [len(data_sets.get_attributes(data).balance) for data in data_sets]
        )
        color_line = TextColor.LINE1
        if self.output:
            print(color_line, end="")
            print(self.header_text)
            print("")
            print(f"{'Dataset':30s} Sampl. Feat. Cont Cls Balance")
            print("=" * 30 + " ====== ===== ==== === " + "=" * max_len)
        if self.excel:
            self.header()
        for dataset in data_sets:
            attributes = data_sets.get_attributes(dataset)
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
                    f"{attributes.features:5,d} {attributes.cont_features:4,d}"
                    f" {attributes.classes:3d} {attributes.balance:40s}"
                )
        if self.excel:
            self.footer()


class SQLFile(BaseReport):
    table_name = "results"

    def header(self):
        file_name = Path(self.file_name).name.replace(Files.report_ext, ".sql")
        self.file = open(os.path.join(Folders.sql, file_name), "w")

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
        args = EnvData().load()
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
        return os.path.join(Folders.excel, Files.exreport_excel(self._score))

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
            row += 1
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
            sheet.freeze_panes(6, 1)
            sheet.hide_gridlines(2)

        def add_datasets_sheet():
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
        add_datasets_sheet()
        book.close()
