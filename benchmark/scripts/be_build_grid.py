#!/usr/bin/env python
import os
import json
from benchmark.Utils import Files, Folders
from benchmark.Arguments import Arguments

"""Build sample grid input file for the model with data taken from the
input grid used optimizing STree
"""


def main(args_test=None):
    arguments = Arguments()
    arguments.xset("model", mandatory=True).xset("score", mandatory=True)
    args = arguments.parse(args_test)
    data = [
        '{"C": 1e4, "gamma": 0.1, "kernel": "rbf"}',
        '{"C": 7, "gamma": 0.14, "kernel": "rbf"}',
        '{"C": 0.2, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 0.2, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 0.95, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 0.05, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"kernel": "rbf"}',
        '{"kernel": "rbf"}',
        '{"C": 1.05, "gamma": "auto","kernel": "rbf"}',
        '{"splitter": "random", "max_features": "auto"}',
        '{"C": 0.05, "max_features": "auto", "kernel": "liblinear", '
        '"multiclass_strategy": "ovr"}',
        '{"kernel": "rbf", "C": 0.05}',
        '{"C": 0.05, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 7, "gamma": 0.1, "kernel": "rbf"}',
        '{"kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 7, "gamma": 0.1, "kernel": "rbf"}',
        '{"C": 0.25, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 0.08, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 0.001, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 2.8, "kernel": "rbf", "gamma": "auto"}',
        '{"kernel": "rbf"}',
        '{"C": 0.05, "gamma": 0.1, "kernel": "poly"}',
        '{"C": 8.25, "gamma": 0.1, "kernel": "poly", "multiclass_strategy": '
        '"ovr"}',
        '{"kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 1.75, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C":57, "kernel": "rbf"}',
        '{"C": 7, "gamma": 0.1, "kernel": "rbf", "multiclass_strategy": '
        '"ovr"}',
        '{"C": 5, "kernel": "rbf", "gamma": "auto"}',
        '{"C": 0.05, "max_iter": 10000.0, "kernel": "liblinear", '
        '"multiclass_strategy": "ovr"}',
        '{"C":0.0275, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 7, "gamma": 10.0, "kernel": "rbf", "multiclass_strategy": '
        '"ovr"}',
        '{"kernel": "rbf", "gamma": 0.001}',
        '{"C": 1e4, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 1.75, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 7, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 2.83, "kernel": "rbf", "gamma": "auto"}',
        '{"C": 0.2, "gamma": 0.1, "kernel": "poly", "multiclass_strategy": '
        '"ovr"}',
        '{"kernel": "liblinear", "multiclass_strategy": "ovr"}',
        '{"C": 2, "gamma": "auto", "kernel": "rbf"}',
        '{"C": 1.75, "kernel": "liblinear", "multiclass_strategy": "ovr"}',
    ]

    results = {}
    output = []
    hyper = ["C", "gamma", "kernel", "multiclass_strategy"]
    kernels = ["linear", "liblinear", "rbf", "poly"]

    # initialize results
    for kernel in kernels:
        results[kernel] = {}
        for item in hyper:
            results[kernel][item] = []
    # load data
    for sample in data:
        line = json.loads(sample)
        if "kernel" not in line:
            line["kernel"] = "linear"
        kernel = line["kernel"]
        for item in hyper:
            if item in line and line[item] not in results[kernel][item]:
                results[kernel][item].append(line[item])

    # Add default values and remove inconsistent values
    results["linear"]["multiclass_strategy"] = ["ovo"]
    del results["linear"]["gamma"]
    del results["liblinear"]["gamma"]
    results["rbf"]["gamma"].append("scale")
    results["poly"]["gamma"].append("scale")
    results["poly"]["multiclass_strategy"].append("ovo")
    for kernel in kernels:
        results[kernel]["C"].append(1.0)

    for item in results:
        results_tmp = {"n_jobs": [-1], "n_estimators": [100]}
        for key, value in results[item].items():
            new_key = f"base_estimator__{key}"
            try:
                results_tmp[new_key] = sorted(value)
            except TypeError:
                t1 = sorted(
                    [
                        x
                        for x in value
                        if isinstance(x, int) or isinstance(x, float)
                    ]
                )
                t2 = sorted([x for x in value if isinstance(x, str)])
                results_tmp[new_key] = t1 + t2
        output.append(results_tmp)

    # save results
    file_name = Files.grid_input(args.score, args.model)
    file_output = os.path.join(Folders.results, file_name)
    with open(file_output, "w") as f:
        json.dump(output, f, indent=4)
    print(f"Generated grid input file to {file_output}")
