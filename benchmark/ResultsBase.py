import abc
import json
import os


from .Arguments import ALL_METRICS, EnvData
from .Datasets import Datasets
from .Experiments import BestResults
from .Utils import Folders, Symbols


def get_input(message="", is_test=False):
    return "test" if is_test else input(message)


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
