#!/usr/bin/env python
import argparse
from Results import Summary
from Utils import EnvDefault


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-m",
        "--model",
        type=str,
        action=EnvDefault,
        envvar="model",
        required=True,
        help="model name",
    )
    ap.add_argument(
        "-s",
        "--score",
        type=str,
        action=EnvDefault,
        envvar="score",
        required=True,
        help="score name {accuracy, f1_micro, f1_macro, all}",
    )
    ap.add_argument(
        "-l",
        "--list",
        type=bool,
        required=False,
        default=False,
        help="List all results",
    )
    args = ap.parse_args()
    return (
        args.score,
        args.model,
        args.list,
    )


(
    score,
    model,
    list_results,
) = parse_arguments()

all_metrics = ["accuracy", "f1-macro", "f1-micro"]

metrics = all_metrics if score == "all" else [score]

summary = Summary()
summary.acquire()

for metric in metrics:
    title = f"BEST RESULT of {metric} for {model}"
    best = summary.best_result(criterion="model", value=model, score=metric)
    summary.show_result(data=best, title=title)
    summary.show_result(
        summary.best_result(score=metric), title=f"BEST RESULT of {metric}"
    )
if list_results:
    summary.list_results()
