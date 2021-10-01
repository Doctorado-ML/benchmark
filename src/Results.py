import os
import json
import abc
import shutil
import subprocess
import xlsxwriter
from tqdm import tqdm
from Experiments import Datasets, BestResults
from Utils import Folders, Files, Symbols


class BaseReport(abc.ABC):
    def __init__(self, file_name, best_file=False):
        self.file_name = file_name
        if not os.path.isfile(file_name):
            raise ValueError(f"{file_name} does not exists!")
        with open(file_name) as f:
            self.data = json.load(f)
        self.best_acc_file = best_file
        self.lines = self.data if best_file else self.data["results"]

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

    def _compute_status(self, dataset, accuracy):
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

    @abc.abstractmethod
    def header(self):
        pass

    @abc.abstractmethod
    def print_line(self, result):
        pass

    @abc.abstractmethod
    def footer(self, accuracy):
        pass


class Report(BaseReport):
    header_lengths = [30, 5, 3, 3, 7, 7, 7, 15, 15, 15]
    header_cols = [
        "Dataset",
        "Samp",
        "Var",
        "Cls",
        "Nodes",
        "Leaves",
        "Depth",
        "Score",
        "Time",
        "Hyperparameters",
    ]

    def __init__(self, file_name, compare=False):
        super().__init__(file_name)
        self.compare = compare

    def header_line(self, text):
        length = sum(self.header_lengths) + len(self.header_lengths) - 3
        if text == "*":
            print("*" * (length + 2))
        else:
            print(f"*{text:{length}s}*")

    def print_line(self, result):
        hl = self.header_lengths
        i = 0
        print(f"{result['dataset']:{hl[i]}s} ", end="")
        i += 1
        print(f"{result['samples']:{hl[i]},d} ", end="")
        i += 1
        print(f"{result['features']:{hl[i]}d} ", end="")
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
            f"{result['time']:8.6f}±{result['time_std']:6.4f} ",
            end="",
        )
        i += 1
        print(f"{str(result['hyperparameters']):{hl[i]}s} ")

    def header(self):
        if self.compare:
            self._load_best_results(
                self.data["score_name"], self.data["model"]
            )
            self._compare_totals = {}
        self.header_line("*")
        self.header_line(
            f" Report {self.data['model']} with {self.data['folds']} Folds "
            f"cross validation and {len(self.data['seeds'])} random seeds"
        )
        self.header_line(
            f" Random seeds: {self.data['seeds']} Stratified: "
            f"{self.data['stratified']}"
        )
        self.header_line(
            f" Execution took {self.data['duration']:7.2f} seconds on an "
            f"{self.data['platform']}"
        )
        self.header_line(f" Score is {self.data['score_name']}")
        self.header_line("*")
        print("")
        line_col = ""
        for field, underscore in zip(self.header_cols, self.header_lengths):
            print(f"{field:{underscore}s} ", end="")
            line_col += "=" * underscore + " "
        print(f"\n{line_col}")

    def footer(self, accuracy):
        self.header_line("*")
        if self.compare:
            for key, value in self._compare_totals.items():
                self.header_line(
                    f" {key} {self._status_meaning(key)} .....: {value:2d}"
                )
        self.header_line(
            f" Accuracy compared to stree_default (liblinear-ovr) .: "
            f"{accuracy/40.282203:7.4f}"
        )
        self.header_line("*")


class ReportBest(BaseReport):
    header_lengths = [30, 8, 50, 35]
    header_cols = [
        "Dataset",
        "Score",
        "File",
        "Hyperparameters",
    ]

    def __init__(self, score, model):
        file_name = os.path.join(
            Folders.results, Files.best_results(score, model)
        )
        super().__init__(file_name, best_file=True)
        self.compare = False
        self.score_name = score
        self.model = model

    def header_line(self, text):
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
        self.header_line(
            f" Report Best {self.score_name} Scores with {self.model} in any "
            "platform"
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
        if self.compare:
            for key, value in self._compare_totals.items():
                self.header_line(
                    f" {key} {self._status_meaning(key)} .....: {value:2d}"
                )
        self.header_line(
            f" Scores compared to stree_default accuracy (liblinear-ovr) .: "
            f"{accuracy/40.282203:7.4f}"
        )
        self.header_line("*")


class Excel(BaseReport):
    row = 5

    def __init__(self, file_name, compare=False):
        super().__init__(file_name)
        self.compare = compare

    def get_file_name(self):
        return self.excel_file_name

    def header(self):
        if self.compare:
            self._load_best_results(
                self.data["score_name"], self.data["model"]
            )
            self._compare_totals = {}
        self.excel_file_name = self.file_name.replace(".json", ".xlsx")
        self.book = xlsxwriter.Workbook(self.excel_file_name)
        self.sheet = self.book.add_worksheet(self.data["model"])
        header = self.book.add_format()
        header.set_font_size(18)
        subheader = self.book.add_format()
        subheader.set_font_size(16)
        self.sheet.write(
            0,
            0,
            f" Report {self.data['model']} with {self.data['folds']} Folds "
            f"cross validation and {len(self.data['seeds'])} random seeds",
            header,
        )
        self.sheet.write(
            1,
            0,
            f" Execution took {self.data['duration']:7.2f} seconds on an "
            f"{self.data['platform']}",
            subheader,
        )
        self.sheet.write(
            1,
            5,
            f"Random seeds: {self.data['seeds']}",
            subheader,
        )
        self.sheet.write(
            2, 0, f" Score is {self.data['score_name']}", subheader
        )
        self.sheet.write(
            2,
            5,
            f"Stratified: {self.data['stratified']}",
            subheader,
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
            ("Parameters", 50),
        ]
        if self.compare:
            header_cols.insert(8, ("Stat", 3))
        bold = self.book.add_format({"bold": True, "font_size": 14})
        i = 0
        for item, length in header_cols:
            self.sheet.write(4, i, item, bold)
            self.sheet.set_column(i, i, length)
            i += 1

    def print_line(self, result):
        size_n = 14
        decimal = self.book.add_format(
            {"num_format": "0.000000", "font_size": size_n}
        )
        integer = self.book.add_format(
            {"num_format": "#,###", "font_size": size_n}
        )
        normal = self.book.add_format({"font_size": size_n})
        col = 0
        self.sheet.write(self.row, col, result["dataset"], normal)
        self.sheet.write(self.row, col + 1, result["samples"], integer)
        self.sheet.write(self.row, col + 2, result["features"], normal)
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
            f"** Accuracy compared to stree_default (liblinear-ovr) .: "
            f"{accuracy/40.282203:7.4f}"
        )
        bold = self.book.add_format({"bold": True, "font_size": 14})
        self.sheet.write(self.row + 1, 0, message, bold)
        for c in range(self.row + 2):
            self.sheet.set_row(c, 20)
        self.sheet.set_row(0, 25)
        self.book.close()


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
            "stratified",
            "score_name",
            "score",
            "score_std",
            "dataset",
            "classifier",
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
            "1" if self.data["stratified"] else "0",
            self.data["score_name"],
            result["score"],
            result["score_std"],
            result["dataset"],
            self.data["model"],
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
    @staticmethod
    def get_result_file_name(score):
        return os.path.join(Folders.results, Files.exreport(score))

    @staticmethod
    def _process_dataset(results, data):
        model = data["model"]
        for record in data["results"]:
            dataset = record["dataset"]
            if (model, dataset) in results:
                if record["score"] > results[model, dataset][0]:
                    results[model, dataset] = (
                        record["score"],
                        record["score_std"],
                    )
            else:
                results[model, dataset] = (
                    record["score"],
                    record["score_std"],
                )

    @staticmethod
    def compile_results(score):
        # build Files.exreport
        result_file_name = Benchmark.get_result_file_name(score)
        results = {}
        init_suffix, end_suffix = Files.results_suffixes(score=score)
        all_files = list(os.walk(Folders.results))
        for root, _, files in tqdm(all_files, desc="files"):
            for name in files:
                if name.startswith(init_suffix) and name.endswith(end_suffix):
                    file_name = os.path.join(root, name)
                    with open(file_name) as fp:
                        data = json.load(fp)
                        Benchmark._process_dataset(results, data)

        with open(result_file_name, "w") as f:
            f.write(f"classifier, dataset, {score}, stdev\n")
            for (model, dataset), (accuracy, stdev) in results.items():
                f.write(f"{model}, {dataset}, {accuracy}, {stdev}\n")

    @staticmethod
    def exreport(score):
        def end_message(message, file):
            length = 100
            print("*" * length)
            print(message)
            print("*" * length)
            with open(os.path.join(Folders.results, file)) as f:
                data = f.read().splitlines()
                for line in data:
                    print(line)

        # Remove previous results
        try:
            shutil.rmtree(Folders.report)
            os.remove(Files.exreport_pdf)
        except FileNotFoundError:
            pass
        except OSError as e:
            print("Error: %s : %s" % (Folders.report, e.strerror))
        # Compute Friedman & Holm Tests
        fout = open(
            os.path.join(Folders.results, Files.exreport_output(score)), "w"
        )
        ferr = open(
            os.path.join(Folders.results, Files.exreport_err(score)), "w"
        )
        result = subprocess.run(
            ["Rscript", os.path.join(Folders.src, Files.benchmark_r), score],
            stdout=fout,
            stderr=ferr,
        )
        fout.close()
        ferr.close()
        if result.returncode != 0:
            end_message("Error computing benchmark", Files.exreport_err(score))
        else:
            end_message("Benchmark Ok", Files.exreport_output(score))
        Files.open(Files.exreport_pdf)

    @staticmethod
    def build_results(score):
        # Build results data structure
        file_name = Benchmark.get_result_file_name(score)
        results = {}
        with open(file_name) as f:
            data = f.read().splitlines()
            data = data[1:]
        for line in data:
            model, dataset, accuracy, stdev = line.split(", ")
            if model not in results:
                results[model] = {}
            results[model][dataset] = (accuracy, stdev)
        return results

    @staticmethod
    def report(score):
        def show(results):
            datasets = results[list(results)[0]]
            print(f"{'Dataset':30s} ", end="")
            lines = "=" * 30 + " "
            for model in results:
                print(f"{model:^13s} ", end="")
                lines += "=" * 13 + " "
            print(f"\n{lines}")
            for dataset, _ in datasets.items():
                print(f"{dataset:30s} ", end="")
                for model in results:
                    print(f"{float(results[model][dataset][0]):.5f}±", end="")
                    print(f"{float(results[model][dataset][1]):.3f} ", end="")
                print("")

        print(f"* Score is: {score}")
        show(Benchmark.build_results(score))

    @staticmethod
    def get_excel_file_name(score):
        return os.path.join(Folders.exreport, Files.exreport_excel(score))

    @staticmethod
    def excel(score):
        results = Benchmark.build_results(score)
        book = xlsxwriter.Workbook(Benchmark.get_excel_file_name(score))
        sheet = book.add_worksheet("Benchmark")
        normal = book.add_format({"font_size": 14})
        bold = book.add_format({"bold": True, "font_size": 14})
        decimal = book.add_format({"num_format": "0.000000", "font_size": 14})
        merge_format = book.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 14,
            }
        )
        row = row_init = 4

        def header():
            nonlocal row
            sheet.merge_range(0, 0, 1, 0, "Benchmark of Models", merge_format)
            sheet.write(1, 2, f"Score is {score}", bold)
            sheet.set_row(1, 20)
            # Set columns width
            sheet.set_column(0, 0, 40)
            for column in range(2 * len(results)):
                sheet.set_column(column + 1, column + 1, 15)
            # Set report header
            # Merge 2 rows
            sheet.merge_range(row, 0, row + 1, 0, "Dataset", merge_format)
            column = 1
            for model in results:
                # Merge 2 columns
                sheet.merge_range(
                    row, column, row, column + 1, model, merge_format
                )
                column += 2
            row += 1
            column = 1
            for _ in range(len(results)):
                sheet.write(row, column, "Score", merge_format)
                sheet.write(row, column + 1, "Stdev", merge_format)
                column += 2

        def body():
            nonlocal row
            datasets = results[list(results)[0]]
            for dataset, _ in datasets.items():
                row += 1
                sheet.write(row, 0, f"{dataset:30s}", normal)
                column = 1
                for model in results:
                    sheet.write(
                        row,
                        column,
                        float(results[model][dataset][0]),
                        decimal,
                    )
                    column += 1
                    sheet.write(
                        row,
                        column,
                        float(results[model][dataset][1]),
                        decimal,
                    )
                    column += 1

        def footer():
            for c in range(row_init, row + 1):
                sheet.set_row(c, 20)

        header()
        body()
        footer()

        book.close()
