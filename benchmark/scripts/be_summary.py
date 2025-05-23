#!/usr/bin/env python
from benchmark.ResultsBase import Summary
from benchmark.Arguments import ALL_METRICS, Arguments


def main(args_test=None):
    arguments = Arguments()
    metrics = list(ALL_METRICS)
    metrics.append("all")
    arguments.xset("score", choices=metrics).xset("model")
    args = arguments.parse(args_test)
    metrics = ALL_METRICS if args.score == "all" else [args.score]
    summary = Summary()
    summary.acquire()
    for metric in metrics:
        title = f"BEST RESULT of {metric} for {args.model}"
        try:
            best = summary.best_result(
                criterion="model", value=args.model, score=metric
            )
        except ValueError as e:
            print(e)
        else:
            summary.show_result(data=best, title=title)
            summary.show_result(
                summary.best_result(score=metric),
                title=f"BEST RESULT of {metric}",
            )
            summary.show_top(score=metric, n=10)
