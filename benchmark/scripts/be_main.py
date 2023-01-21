#!/usr/bin/env python
import os
from benchmark.Experiments import Experiment
from benchmark.Datasets import Datasets
from benchmark.Results import Report
from benchmark.Arguments import Arguments

"""Do experiment and build result file, optionally print report with results
"""


def main(args_test=None):
    arguments = Arguments(prog="be_main")
    arguments.xset("stratified").xset("score").xset("model", mandatory=True)
    arguments.xset("n_folds").xset("platform").xset("quiet").xset("title")
    arguments.xset("report").xset("ignore_nan").xset("discretize")
    arguments.add_exclusive(
        ["grid_paramfile", "best_paramfile", "hyperparameters"]
    )
    arguments.xset(
        "dataset", overrides="title", const="Test with only one dataset"
    )
    args = arguments.parse(args_test)
    report = args.report or args.dataset is not None
    if args.grid_paramfile:
        args.best_paramfile = False
    try:
        job = Experiment(
            score_name=args.score,
            model_name=args.model,
            stratified=args.stratified,
            datasets=Datasets(
                dataset_name=args.dataset, discretize=args.discretize
            ),
            hyperparams_dict=args.hyperparameters,
            hyperparams_file=args.best_paramfile,
            grid_paramfile=args.grid_paramfile,
            progress_bar=not args.quiet,
            platform=args.platform,
            ignore_nan=args.ignore_nan,
            title=args.title,
            folds=args.n_folds,
        )
        job.do_experiment()
    except ValueError as e:
        print(e)
    else:
        if report:
            result_file = job.get_output_file()
            report = Report(result_file)
            report.report()
        if args.dataset is not None:
            print(f"Partial result file removed: {result_file}")
            os.remove(result_file)
        else:
            print(f"Results in {job.get_output_file()}")
