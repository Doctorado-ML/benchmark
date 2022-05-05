#!/usr/bin/env python
import os
import subprocess
import json
from stree import Stree
from graphviz import Source
from benchmark.Experiments import Datasets
from benchmark.Utils import Files, Folders
from benchmark.Arguments import Arguments


def compute_stree(X, y, random_state):
    clf = Stree(random_state=random_state)
    clf.fit(X, y)
    return clf


def load_hyperparams(score_name, model_name):
    grid_file = os.path.join(
        Folders.results, Files.grid_output(score_name, model_name)
    )
    with open(grid_file) as f:
        return json.load(f)


def hyperparam_filter(hyperparams):
    res = {}
    for key, value in hyperparams.items():
        if key.startswith("base_estimator"):
            newkey = key.split("__")[1]
            res[newkey] = value
    return res


def build_title(dataset, accuracy, n_samples, n_features, n_classes, nodes):
    dataset_chars = f"-{dataset}- f={n_features} s={n_samples} c={n_classes}"
    return (
        f'<font point-size="25" color="brown">{dataset_chars}<BR/></font>'
        f'<font point-size="20" color="red">accuracy: {accuracy:.6f} / '
        f"{nodes} nodes</font>"
    )


def add_color(source):
    return (
        source.replace(  # Background and title font color
            "fontcolor=blue", "fontcolor=white\nbgcolor=darkslateblue"
        )
        .replace("brown", "cyan")  # subtitle font color
        .replace(  # Fill leaves
            "style=filled", 'style="filled" fillcolor="/blues5/1:/blues5/4"'
        )
        .replace(  # Fill nodes
            "fontcolor=black",
            'style=radial fillcolor="orange:white" gradientangle=60',
        )
        .replace("color=black", "color=white")  # arrow color
        .replace(  # accuracy / # nodes
            'color="red"', 'color="darkolivegreen1"'
        )
    )


def print_stree(clf, dataset, X, y, color, quiet):
    output_folder = "img"
    samples, features = X.shape
    classes = max(y) + 1
    accuracy = clf.score(X, y)
    nodes, _ = clf.nodes_leaves()
    title = build_title(dataset, accuracy, samples, features, classes, nodes)
    dot_source = clf.graph(title)
    if color:
        dot_source = add_color(dot_source)
    grp = Source(dot_source)
    file_name = os.path.join(output_folder, f"stree_{dataset}")
    grp.render(format="png", filename=f"{file_name}")
    os.remove(f"{file_name}")
    print(f"File {file_name}.png generated")
    if not quiet:
        cmd_open = "/usr/bin/open"
        if os.path.isfile(cmd_open) and os.access(cmd_open, os.X_OK):
            subprocess.run([cmd_open, f"{file_name}.png"])


def main():
    arguments = Arguments()
    arguments.xset("color").xset("dataset", default="all").xset("quiet")
    args = arguments.parse()
    hyperparameters = load_hyperparams("accuracy", "ODTE")
    random_state = 57
    dt = Datasets()
    for dataset in dt:
        if dataset == args.dataset or args.dataset == "all":
            X, y = dt.load(dataset)
            clf = Stree(random_state=random_state)
            hyperparams_dataset = hyperparam_filter(
                hyperparameters[dataset][1]
            )
            clf.set_params(**hyperparams_dataset)
            clf.fit(X, y)
            print_stree(clf, dataset, X, y, args.color, args.quiet)
