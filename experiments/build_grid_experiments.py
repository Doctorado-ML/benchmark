#!/usr/bin/env python
import os
import argparse
import datetime


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-s",
        "--score",
        type=str,
        required=False,
        default="accuracy",
        help="score used in gridsearch experiment",
    )
    ap.add_argument(
        "-p",
        "--platform",
        type=str,
        required=True,
        choices=["pbs", "slurm"],
        help="Platform used to run the gridsearch experiments {pbs, slurm}",
    )
    ap.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
        help="model to use",
    )
    args = ap.parse_args()

    return (args.score, args.platform, args.model)


def content(file_name):
    with open(file_name) as f:
        return f.read().splitlines()


def generate_experiment(dataset, model, score, platform):
    path = content("path.txt")[0]
    file_name = "experiment.pbs" if platform == "pbs" else "experiment.slurm"
    lines = content(file_name)
    lines.extend(content("script_grid.txt"))
    day = (
        f"{datetime.datetime.now().month:02d}{datetime.datetime.now().day:02d}"
    )
    file_name = f"grid_{model}_{platform}_{day}_{dataset}"
    output_file_name = os.path.join("grid", f"{file_name}.sh")
    strings = [
        ("<date>", day),
        ("<folder>", path),
        ("<score>", score),
        ("<model>", model),
        ("<file_name>", file_name),
        ("<dataset>", dataset),
    ]
    data = lines.copy()
    for item, value in strings:
        data = [line.replace(item, value) for line in data]
    with open(output_file_name, "w") as f:
        f.write("\n".join(data))
    return output_file_name


(
    score,
    platform,
    model,
) = parse_arguments()

with open(os.path.join("..", "data", "all.txt")) as f:
    lines = f.read().splitlines()
    for dataset in lines:
        if dataset.startswith("#") or dataset.strip() == "":
            continue
        else:
            file_name = generate_experiment(dataset, model, score, platform)
            print(f"Generated {file_name}")
