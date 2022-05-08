#!/usr/bin/env python
import os
import json
from stree import Stree
from graphviz import Source
from benchmark.Experiments import Datasets
from benchmark.Utils import Files, Folders
from benchmark.Arguments import Arguments


def load_hyperparams(score_name, model_name):
    grid_file = os.path.join(
        Folders.results, Files.grid_output(score_name, model_name)
    )
    with open(grid_file) as f:
        return json.load(f)


# def hyperparam_filter(hyperparams):
#     res = {}
#     for key, value in hyperparams.items():
#         if key.startswith("base_estimator"):
#             newkey = key.split("__")[1]
#             res[newkey] = value
#     return res


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
    samples, features = X.shape
    classes = max(y) + 1
    accuracy = clf.score(X, y)
    nodes, _ = clf.nodes_leaves()
    title = build_title(dataset, accuracy, samples, features, classes, nodes)
    dot_source = clf.graph(title)
    if color:
        dot_source = add_color(dot_source)
    grp = Source(dot_source)
    file_name = os.path.join(Folders.img, f"stree_{dataset}")
    grp.render(format="png", filename=f"{file_name}")
    os.remove(f"{file_name}")
    file_name += ".png"
    print(f"File {file_name} generated")
    Files.open(name=file_name, test=quiet)


def main(args_test=None):
    arguments = Arguments()
    arguments.xset("color").xset("dataset", default="all").xset("quiet")
    args = arguments.parse(args_test)
    hyperparameters = load_hyperparams("accuracy", "STree")
    random_state = 57
    dt = Datasets()
    for dataset in dt:
        if dataset == args.dataset or args.dataset == "all":
            X, y = dt.load(dataset)
            clf = Stree(random_state=random_state)
            hyperparams_dataset = hyperparameters[dataset][1]
            clf.set_params(**hyperparams_dataset)
            clf.fit(X, y)
            print_stree(clf, dataset, X, y, args.color, args.quiet)
