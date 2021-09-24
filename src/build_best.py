import argparse
from Results import ReportBest
from Experiments import Datasets, BestResults

"""Build a json file with the best results of a model and its hyperparameters
"""


def parse_arguments():
    ap = argparse.ArgumentParser()
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
    return (args.model, args.report)


(model, report) = parse_arguments()
datasets = Datasets()
best = BestResults(model, datasets)
best.build()
if report:
    report = ReportBest(model)
    report.report()
