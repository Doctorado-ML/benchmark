import os
import subprocess
import argparse
import json
from stree import Stree
from graphviz import Source
from Experiments import Datasets
from Utils import Files, Folders


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c",
        "--color",
        type=bool,
        required=False,
        default=False,
        help="use colors for the tree",
    )
    args = ap.parse_args()
    return (args.color,)


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


def print_stree(clf, dataset, X, y):
    output_folder = "img"
    samples, features = X.shape
    classes = max(y) + 1
    accuracy = clf.score(X, y)
    nodes, _ = clf.nodes_leaves()
    title = build_title(dataset, accuracy, samples, features, classes, nodes)
    grp = Source(clf.graph(title))
    file_name = os.path.join(output_folder, f"stree_{dataset}")
    grp.render(format="png", filename=f"{file_name}")
    os.remove(f"{file_name}")
    print(f"File {file_name}.png generated")
    cmd_open = "/usr/bin/open"
    if os.path.isfile(cmd_open) and os.access(cmd_open, os.X_OK):
        subprocess.run([cmd_open, f"{file_name}.png"])


if __name__ == "__main__":
    (color,) = parse_arguments()
    hyperparameters = load_hyperparams("accuracy", "ODTE")
    random_state = 57
    dt = Datasets()
    for dataset in dt:
        X, y = dt.load(dataset)
        clf = Stree(random_state=random_state)
        hyperparams_dataset = hyperparam_filter(hyperparameters[dataset][1])
        clf.set_params(**hyperparams_dataset)
        clf.fit(X, y)
        print_stree(clf, dataset, X, y)
