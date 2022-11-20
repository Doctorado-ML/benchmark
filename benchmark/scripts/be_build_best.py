#!/usr/bin/env python
from benchmark.Results import ReportBest
from benchmark.Experiments import BestResults
from benchmark.Datasets import Datasets
from benchmark.Arguments import Arguments

"""Build a json file with the best results of a model and its hyperparameters
"""


def main(args_test=None):
    arguments = Arguments()
    arguments.xset("score", mandatory=True).xset("report")
    arguments.xset("model", mandatory=True)
    args = arguments.parse(args_test)
    datasets = Datasets()
    best = BestResults(args.score, args.model, datasets)
    try:
        best.build()
    except ValueError as e:
        print(e)
    else:
        if args.report:
            report = ReportBest(args.score, args.model, best=True)
            report.report()
