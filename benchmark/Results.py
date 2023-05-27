import os
from .ResultsBase import BaseReport, StubReport, Summary
from .Utils import Files, Folders, TextColor


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
