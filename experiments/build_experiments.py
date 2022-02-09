#!/usr/bin/env python
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
        help="score used in experiment",
    )
    ap.add_argument(
        "-p",
        "--platform",
        type=str,
        required=True,
        choices=["pbs", "slurm"],
        help="Platform used to run the experiments {pbs, slurm}",
    )
    args = ap.parse_args()

    return (
        args.score,
        args.platform,
    )


def content(file_name):
    with open(file_name) as f:
        return f.read().splitlines()


def generate_experiment(data, score, platform):
    generate_experiment.idx += 1
    path = content("path.txt")[0]
    file_name = "experiment.pbs" if platform == "pbs" else "experiment.slurm"
    lines = content(file_name)
    lines.extend(content("script.txt"))
    day = (
        f"{datetime.datetime.now().month:02d}{datetime.datetime.now().day:02d}"
    )
    (model, title, parameters) = data.split("&")
    file_name = f"{model}_{score}_{platform}_{day}_{generate_experiment.idx}"
    output_file_name = f"{file_name}.sh"
    strings = [
        ("<date>", day),
        ("<folder>", path),
        ("<score>", score),
        ("<model>", model),
        ("<title>", title),
        ("<parameters>", parameters),
        ("<file_name>", file_name),
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
) = parse_arguments()

generate_experiment.idx = 0
output = ""
with open("experiments.txt") as f:
    lines = f.read().splitlines()
    for line in lines:
        if line.startswith("#") or line.strip() == "":
            output += line + "\n"
        else:
            file_name = generate_experiment(line, score, platform)
            output += f"#{file_name}, {line}\n"
            print(f"Generated {file_name}")
with open("experiments.txt", "w") as f:
    print(output, file=f)
