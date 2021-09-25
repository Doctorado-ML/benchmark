import os
import json
import random
import warnings
import time
from datetime import datetime
from tqdm import tqdm
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from Utils import Folders, Files
from Models import Models


class Randomized:
    seeds = [57, 31, 1714, 17, 23, 79, 83, 97, 7, 1]


class Diterator:
    def __init__(self, data):
        self._stack = data.copy()

    def __next__(self):
        if len(self._stack) == 0:
            raise StopIteration()
        return self._stack.pop(0)


class Datasets:
    def __init__(self):
        with open(os.path.join(Folders.data, Files.index)) as f:
            self.data_sets = f.read().splitlines()

    def load(self, name):
        data = pd.read_csv(
            os.path.join(Folders.data, Files.dataset(name)),
            sep="\t",
            index_col=0,
        )
        X = data.drop("clase", axis=1).to_numpy()
        y = data["clase"].to_numpy()
        return X, y

    def __iter__(self) -> Diterator:
        return Diterator(self.data_sets)


class BestResults:
    def __init__(self, model, datasets):
        self.datasets = datasets
        self.model = model
        self.data = {}

    def _get_file_name(self):
        return os.path.join(Folders.results, Files.best_results(self.model))

    def load(self, dictionary):
        self.file_name = self._get_file_name()
        try:
            with open(self.file_name) as f:
                self.data = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"{self.file_name} does not exist")
        return self.fill(dictionary, self.data)

    def fill(self, dictionary, data=None):
        if data is None:
            data = {}
        for dataset in self.datasets:
            if dataset not in data:
                data[dataset] = (0.0, dictionary, "")
        return data

    def _process_datafile(self, results, data, file_name):
        for record in data["results"]:
            dataset = record["dataset"]
            if dataset in results:
                if record["accuracy"] > results[dataset]["accuracy"]:
                    record["file_name"] = file_name
                    results[dataset] = record
            else:
                record["file_name"] = file_name
                results[dataset] = record

    def build(self):
        results = {}
        init_suffix, end_suffix = Files.results_suffixes(self.model)
        all_files = list(os.walk(Folders.results))
        for root, _, files in tqdm(all_files, desc="files"):
            for name in files:
                if name.startswith(init_suffix) and name.endswith(end_suffix):
                    file_name = os.path.join(root, name)
                    with open(file_name) as fp:
                        data = json.load(fp)
                    self._process_datafile(results, data, name)
        # Build best results json file
        output = {}
        datasets = Datasets()
        for name in tqdm(list(datasets), desc="datasets"):
            output[name] = (
                results[name]["accuracy"],
                results[name]["hyperparameters"],
                results[name]["file_name"],
            )
        self.data = output
        with open(self._get_file_name(), "w") as fp:
            json.dump(output, fp)


class Experiment:
    def __init__(
        self,
        model_name,
        datasets,
        hyperparams_dict,
        hyperparams_file,
        platform,
        progress_bar=True,
        folds=5,
    ):
        today = datetime.now()
        self.time = today.strftime("%H:%M:%S")
        self.date = today.strftime("%Y-%m-%d")
        self.output_file = os.path.join(
            Folders.results,
            Files.results(model_name, platform, self.date, self.time),
        )
        self.model_name = model_name
        self.model = Models.get_model(model_name)
        self.datasets = datasets
        dictionary = json.loads(hyperparams_dict)
        hyper = BestResults(model=model_name, datasets=datasets)
        if hyperparams_file:
            self.hyperparameters_dict = hyper.load(
                dictionary=dictionary,
            )
        else:
            self.hyperparameters_dict = hyper.fill(
                dictionary=dictionary,
            )
        self.platform = platform
        self.progress_bar = progress_bar
        self.folds = folds
        self.random_seeds = Randomized.seeds
        self.results = []
        self.duration = 0
        self._init_experiment()

    def get_output_file(self):
        return self.output_file

    def _build_classifier(self, random_state, hyperparameters):
        clf = self.model(random_state=random_state)
        clf.set_params(**hyperparameters)
        return clf

    def _init_experiment(self):
        self.scores = []
        self.times = []
        self.nodes = []
        self.leaves = []
        self.depths = []

    def _n_fold_crossval(self, X, y, hyperparameters):
        if self.scores != []:
            raise ValueError("Must init experiment before!")
        loop = tqdm(
            self.random_seeds,
            position=1,
            leave=False,
            disable=not self.progress_bar,
        )
        for random_state in loop:
            loop.set_description(f"Seed({random_state:4d})")
            random.seed(random_state)
            np.random.seed(random_state)
            kfold = StratifiedKFold(
                shuffle=True, random_state=random_state, n_splits=self.folds
            )
            clf = self._build_classifier(random_state, hyperparameters)
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                res = cross_validate(
                    clf, X, y, cv=kfold, return_estimator=True
                )
            self.scores.append(res["test_score"])
            self.times.append(res["fit_time"])
            for result_item in res["estimator"]:
                nodes_item, leaves_item, depth_item = Models.get_complexity(
                    self.model_name, result_item
                )
                self.nodes.append(nodes_item)
                self.leaves.append(leaves_item)
                self.depths.append(depth_item)

    def _add_results(self, name, hyperparameters, samples, features, classes):
        record = {}
        record["dataset"] = name
        record["samples"] = samples
        record["features"] = features
        record["classes"] = classes
        record["hyperparameters"] = hyperparameters
        record["nodes"] = np.mean(self.nodes)
        record["leaves"] = np.mean(self.leaves)
        record["depth"] = np.mean(self.depths)
        record["accuracy"] = np.mean(self.scores)
        record["accuracy_std"] = np.std(self.scores)
        record["time"] = np.mean(self.times)
        record["time_std"] = np.std(self.times)
        self.results.append(record)

    def _output_results(self):
        output = {}
        output["model"] = self.model_name
        output["folds"] = self.folds
        output["date"] = self.date
        output["time"] = self.time
        output["duration"] = self.duration
        output["seeds"] = self.random_seeds
        output["platform"] = self.platform
        output["results"] = self.results
        with open(self.output_file, "w") as f:
            json.dump(output, f)

    def do_experiment(self):
        now = time.time()
        loop = tqdm(
            list(self.datasets),
            position=0,
            disable=not self.progress_bar,
        )
        for name in loop:
            loop.set_description(f"{name:30s}")
            X, y = self.datasets.load(name)
            samp, feat = X.shape
            n_classes = len(np.unique(y))
            hyperparameters = self.hyperparameters_dict[name][1]
            self._init_experiment()
            self._n_fold_crossval(X, y, hyperparameters)
            self._add_results(name, hyperparameters, samp, feat, n_classes)
        self.duration = time.time() - now
        self._output_results()
        if self.progress_bar:
            print(f"Results in {self.output_file}")
