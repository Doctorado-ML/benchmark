import abc
import json
import math
import os
from operator import itemgetter

from benchmark.Datasets import Datasets
from benchmark.Utils import NO_RESULTS, Files, Folders, TextColor

from .Arguments import ALL_METRICS, EnvData
from .Datasets import Datasets
from .Experiments import BestResults
from .Utils import Folders, Symbols


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
            22.109799,
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
        self.__load_env_data()
        self.__compute_best_results_ever()

    def __load_env_data(self):
        # Set the labels for nodes, leaves, depth
        env_data = EnvData.load()
        self.nodes_label = env_data["nodes"]
        self.leaves_label = env_data["leaves"]
        self.depth_label = env_data["depth"]
        self.key = env_data["source_data"]
        self.margin = float(env_data["margin"])

    def __compute_best_results_ever(self):
        best = BestResultsEver()
        self.best_score_name, self.best_score_value = best.get_name_value(
            self.key, self.score_name
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
        status = " "
        if self.compare:
            # Compare with best results
            best = self.best_results[dataset][0]
            if accuracy == best:
                status = Symbols.equal_best
            elif accuracy > best:
                status = Symbols.better_best
        else:
            # compare with dataset label distribution only if its a binary one
            # down_arrow if accuracy is less than the ZeroR
            # black_star if accuracy is greater than the ZeroR + margin%
            if self.score_name == "accuracy":
                dt = Datasets()
                attr = dt.get_attributes(dataset)
                if attr.classes == 2:
                    max_category = max(attr.distribution.values())
                    max_value = max_category * (1 + self.margin)
                    if max_value > 1:
                        max_value = 0.9995
                    status = (
                        Symbols.cross
                        if accuracy <= max_value
                        else Symbols.upward_arrow
                        if accuracy > max_value
                        else " "
                    )
        if status != " ":
            if status not in self._compare_totals:
                self._compare_totals[status] = 1
            else:
                self._compare_totals[status] += 1
        return status

    def _status_meaning(self, status):
        meaning = {
            Symbols.equal_best: "Equal to best",
            Symbols.better_best: "Better than best",
            Symbols.cross: "Less than or equal to ZeroR",
            Symbols.upward_arrow: f"Better than ZeroR + "
            f"{self.margin*100:3.1f}%",
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
