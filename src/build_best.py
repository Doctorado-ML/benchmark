import argparse
from Results import ReportBest
from Experiments import Datasets, BestResults

"""Build a json file with the best results of a model and its hyperparameters
"""


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-s",
        "--score",
        type=str,
        required=True,
        help="score name {accuracy, f1_macro, ...}",
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
        "-r",
        "--report",
        type=bool,
        required=False,
        help="Generate Report",
    )
    args = ap.parse_args()
    return (args.score, args.model, args.report)


(score, model, report) = parse_arguments()
datasets = Datasets()
best = BestResults(score, model, datasets)
best.build()
if report:
    report = ReportBest(score, model)
    report.report()
