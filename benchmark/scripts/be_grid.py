#!/usr/bin/env python
from benchmark.Experiments import GridSearch, Datasets
from benchmark.Arguments import Arguments

"""Do experiment and build result file, optionally print report with results
"""


def main():
    arguments = Arguments()
    arguments.xset("score").xset("platform").xset("model", mandatory=True)
    arguments.xset("quiet").xset("stratified").xset("dataset").xset("n_folds")
    args = arguments.parse()
    if not args.quiet:
        print(f"Perform grid search with {args.model} model")
    job = GridSearch(
        score_name=args.score,
        model_name=args.model,
        stratified=args.stratified,
        datasets=Datasets(dataset_name=args.dataset),
        progress_bar=not args.quiet,
        platform=args.platform,
        folds=args.n_folds,
    )
    try:
        job.do_gridsearch()
    except FileNotFoundError:
        print(f"** The grid input file [{job.grid_file}] could not be found")
        print("")
