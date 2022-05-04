#!/usr/bin/env python
from benchmark.Experiments import GridSearch, Datasets
from benchmark.Arguments import Arguments

"""Do experiment and build result file, optionally print report with results
"""


def main():
    arguments = Arguments()
    arguments.xset("score").xset("platform").xset("model").xset("n_folds")
    arguments.xset("quiet").xset("stratified").xset("dataset")
    args = arguments.parse()
    job = GridSearch(
        score_name=args.score,
        model_name=args.model,
        stratified=args.stratified,
        datasets=Datasets(dataset_name=args.dataset),
        progress_bar=not args.quiet,
        platform=args.platform,
        folds=args.folds,
    )
    job.do_gridsearch()
