#!/usr/bin/env python
import os
from benchmark.Experiments import Experiment, Datasets
from benchmark.Results import Report
from Arguments import Arguments

"""Do experiment and build result file, optionally print report with results
"""


def main():
    arguments = Arguments()
    arguments.xset("stratified").xset("score").xset("model").xset("dataset")
    arguments.xset("n_folds").xset("platform").xset("quiet").xset("title")
    arguments.xset("hyperparameters").xset("paramfile").xset("report")
    arguments.xset("grid_paramfile")
    args = arguments.parse()
    report = args.report or args.dataset is not None
    if args.grid_paramfile:
        args.paramfile = False
    job = Experiment(
        score_name=args.score,
        model_name=args.model,
        stratified=args.stratified,
        datasets=Datasets(dataset_name=args.dataset),
        hyperparams_dict=args.hyperparameters,
        hyperparams_file=args.paramfile,
        grid_paramfile=args.grid_paramfile,
        progress_bar=not args.quiet,
        platform=args.platform,
        title=args.experiment_title,
        folds=args.folds,
    )
    job.do_experiment()
    if report:
        result_file = job.get_output_file()
        report = Report(result_file)
        report.report()

    if args.dataset is not None:
        print(f"Partial result file removed: {result_file}")
        os.remove(result_file)
    else:
        print(f"Results in {job.get_output_file()}")
