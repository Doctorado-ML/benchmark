#!/usr/bin/env python
import json
from benchmark.Results import Summary
from benchmark.Arguments import ALL_METRICS, Arguments


def main(args_test=None):
    arguments = Arguments()
    metrics = list(ALL_METRICS)
    metrics.append("all")
    arguments.xset("score", choices=metrics)
    args = arguments.parse(args_test)
    metrics = ALL_METRICS if args.score == "all" else [args.score]
    summary = Summary()
    summary.acquire()
    nl = 50
    num = 100
    for metric in metrics:
        best = summary.best_results_datasets(score=metric)
        for key, item in best.items():
            print(f"{key:30s} {item[2]:{nl}s}")
            print("-" * num)
            print(f"{item[0]:30.7f} {json.dumps(item[1]):{nl}s}")
            print("-" * num)
            print(f"{item[3]:{nl+num}s}")
            print("*" * num)
