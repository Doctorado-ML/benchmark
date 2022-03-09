import os
import json
import random
import warnings
import time
from datetime import datetime
from tqdm import tqdm
import numpy as np
import pandas as pd
from sklearn.model_selection import (
    StratifiedKFold,
    KFold,
    GridSearchCV,
    cross_validate,
)
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
    def __init__(self, dataset=None):
        if dataset is None:
            try:
                with open(os.path.join(Folders.data, Files.index)) as f:
                    self.data_sets = f.read().splitlines()
            except FileNotFoundError:
                with open(os.path.join("..", Folders.data, Files.index)) as f:
                    self.data_sets = f.read().splitlines()
        else:
            self.data_sets = [dataset]

    def load(self, name):
        try:
            data = pd.read_csv(
                os.path.join(Folders.data, Files.dataset(name)),
                sep="\t",
                index_col=0,
            )
        except FileNotFoundError:
            data = pd.read_csv(
                os.path.join("..", Folders.data, Files.dataset(name)),
                sep="\t",
                index_col=0,
            )
        X = data.drop("clase", axis=1).to_numpy()
        y = data["clase"].to_numpy()
        return X, y

    def __iter__(self) -> Diterator:
        return Diterator(self.data_sets)


class BestResults:
    def __init__(self, score, model, datasets):
        self.score_name = score
        self.datasets = datasets
        self.model = model
        self.data = {}

    def _get_file_name(self):
        return os.path.join(
            Folders.results, Files.best_results(self.score_name, self.model)
        )

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
                if record["score"] >= results[dataset]["score"]:
                    record["file_name"] = file_name
                    results[dataset] = record
            else:
                record["file_name"] = file_name
                results[dataset] = record

    def build(self):
        results = {}
        init_suffix, end_suffix = Files.results_suffixes(
            score=self.score_name, model=self.model
        )
        all_files = sorted(list(os.walk(Folders.results)))
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
                results[name]["score"],
                results[name]["hyperparameters"],
                results[name]["file_name"],
            )
        self.data = output
        with open(self._get_file_name(), "w") as fp:
            json.dump(output, fp)


class Experiment:
    def __init__(
        self,
        score_name,
        model_name,
        stratified,
        datasets,
        hyperparams_dict,
        hyperparams_file,
        platform,
        title,
        progress_bar=True,
        folds=5,
    ):
        today = datetime.now()
        self.time = today.strftime("%H:%M:%S")
        self.date = today.strftime("%Y-%m-%d")
        self.output_file = os.path.join(
            Folders.results,
            Files.results(
                score_name,
                model_name,
                platform,
                self.date,
                self.time,
                stratified,
            ),
        )
        self.score_name = score_name
        self.model_name = model_name
        self.title = title
        self.stratified = stratified == "1"
        self.stratified_class = StratifiedKFold if self.stratified else KFold
        self.datasets = datasets
        dictionary = json.loads(hyperparams_dict)
        hyper = BestResults(
            score=score_name, model=model_name, datasets=datasets
        )
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
        self.model = Models.get_model(self.model_name, random_state)
        clf = self.model
        clf.set_params(**hyperparameters)
        clf.set_params(random_state=random_state)
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
            kfold = self.stratified_class(
                shuffle=True, random_state=random_state, n_splits=self.folds
            )
            clf = self._build_classifier(random_state, hyperparameters)
            self.version = clf.version() if hasattr(clf, "version") else "-"
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                res = cross_validate(
                    clf,
                    X,
                    y,
                    cv=kfold,
                    return_estimator=True,
                    scoring=self.score_name,
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
        record["score"] = np.mean(self.scores)
        record["score_std"] = np.std(self.scores)
        record["time"] = np.mean(self.times)
        record["time_std"] = np.std(self.times)
        self.results.append(record)

    def _output_results(self):
        output = {}
        output["score_name"] = self.score_name
        output["title"] = self.title
        output["model"] = self.model_name
        output["version"] = self.version
        output["stratified"] = self.stratified
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


class GridSearch:
    def __init__(
        self,
        score_name,
        model_name,
        stratified,
        datasets,
        platform,
        progress_bar=True,
        folds=5,
    ):
        today = datetime.now()
        self.time = today.strftime("%H:%M:%S")
        self.date = today.strftime("%Y-%m-%d")
        self.output_file = os.path.join(
            Folders.results,
            Files.grid_output(
                score_name,
                model_name,
            ),
        )
        self.score_name = score_name
        self.model_name = model_name
        self.stratified = stratified == "1"
        self.stratified_class = StratifiedKFold if self.stratified else KFold
        self.datasets = datasets
        self.progress_bar = progress_bar
        self.folds = folds
        self.platform = platform
        self.random_seeds = Randomized.seeds
        self.grid_file = os.path.join(
            Folders.results, Files.grid_input(score_name, model_name)
        )
        with open(self.grid_file) as f:
            self.grid = json.load(f)
        self.duration = 0
        self._init_data()

    def _init_data(self):
        # if result file not exist initialize it
        try:
            with open(self.output_file, "r") as f:
                self.results = json.load(f)
        except FileNotFoundError:
            # init file
            output = {}
            data = Datasets()
            for item in data:
                output[item] = [0.0, {}, ""]
            with open(self.output_file, "w") as f:
                json.dump(output, f)
                self.results = output

    def _save_results(self):
        with open(self.output_file, "r") as f:
            data = json.load(f)
        for item in self.datasets:
            data[item] = self.results[item]
        with open(self.output_file, "w") as f:
            json.dump(data, f)

    def _store_result(self, name, grid, duration):
        d_message = f"{duration:.3f} s"
        if duration > 3600:
            d_message = f"{duration / 3600:.3f} h"
        elif duration > 60:
            d_message = f"{duration / 60:.3f} min"
        message = (
            f"v. {self.version}, Computed on {self.platform} on "
            f"{self.date} at {self.time} "
            f"took {d_message}"
        )
        score = grid.best_score_
        hyperparameters = grid.best_params_
        self.results[name] = [score, hyperparameters, message]

    def do_gridsearch(self):
        now = time.time()
        loop = tqdm(
            list(self.datasets),
            position=0,
            disable=not self.progress_bar,
        )
        for name in loop:
            loop.set_description(f"{name:30s}")
            X, y = self.datasets.load(name)
            result = self._n_fold_gridsearch(X, y)
            self._store_result(name, result, time.time() - now)
        self._save_results()

    def _n_fold_gridsearch(self, X, y):
        kfold = self.stratified_class(
            shuffle=True,
            random_state=self.random_seeds[0],
            n_splits=self.folds,
        )
        clf = Models.get_model(self.model_name)
        self.version = clf.version() if hasattr(clf, "version") else "-"
        self._num_warnings = 0
        warnings.warn = self._warn
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            grid = GridSearchCV(
                estimator=clf,
                cv=kfold,
                param_grid=self.grid,
                scoring=self.score_name,
                n_jobs=-1,
            )
            grid.fit(X, y)
            return grid

    def _warn(self, *args, **kwargs) -> None:
        self._num_warnings += 1
