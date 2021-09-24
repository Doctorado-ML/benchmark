import argparse
from Experiments import Experiment, Datasets
from Results import Report

"""Do experiment and build result file, optionally print report with results
"""


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-P",
        "--platform",
        type=str,
        required=True,
        help="Platform where the test is run",
    )
    ap.add_argument(
        "-m",
        "--model",
        type=str,
        required=False,
        default="STree",
        help="model name, dfault STree",
    )
    ap.add_argument(
        "-n",
        "--n_folds",
        type=int,
        required=False,
        default=5,
        help="number of folds",
    )
    ap.add_argument(
        "-p", "--hyperparameters", type=str, required=False, default="{}"
    )
    ap.add_argument(
        "-f", "--paramfile", type=bool, required=False, default=False
    )
    ap.add_argument(
        "-q",
        "--quiet",
        type=bool,
        default=False,
        required=False,
        help="Wether to show progress bar or not",
    )
    ap.add_argument(
        "-r",
        "--report",
        type=bool,
        default=False,
        required=False,
        help="Report results",
    )
    args = ap.parse_args()
    return (
        args.model,
        args.n_folds,
        args.platform,
        args.quiet,
        args.hyperparameters,
        args.paramfile,
        args.report,
    )


(
    model,
    folds,
    platform,
    quiet,
    hyperparameters,
    paramfile,
    report,
) = parse_arguments()
job = Experiment(
    model_name=model,
    datasets=Datasets(),
    hyperparams_dict=hyperparameters,
    hyperparams_file=paramfile,
    progress_bar=not quiet,
    platform=platform,
    folds=folds,
)
job.do_experiment()
if report:
    result_file = job.get_output_file()
    report = Report(result_file)
    report.report()
