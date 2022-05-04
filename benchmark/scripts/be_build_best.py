#!/usr/bin/env python
from benchmark.Results import ReportBest
from benchmark.Experiments import Datasets, BestResults
from benchmark.Arguments import Arguments

"""Build a json file with the best results of a model and its hyperparameters
"""


def main():
    arguments = Arguments()
    arguments.xset("score").xset("report").xset("model")
    args = arguments.parse()
    datasets = Datasets()
    best = BestResults(args.score, args.model, datasets)
    best.build()
    if args.report:
        report = ReportBest(args.score, args.model, best=True, grid=False)
        report.report()
