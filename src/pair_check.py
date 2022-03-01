#!/usr/bin/env python
import argparse
from Experiments import Experiment, Datasets
from Results import Report
from Utils import EnvDefault

"""Check best results of two models giving scores and win-tie-loose results
"""


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-s",
        "--score",
        action=EnvDefault,
        envvar="score",
        type=str,
        required=True,
        help="score name {accuracy, f1_macro, ...}",
    )
    ap.add_argument(
        "-m1",
        "--model1",
        type=str,
        required=True,
        help="model 1 name",
    )
    ap.add_argument(
        "-m2",
        "--model2",
        type=str,
        required=True,
        help="model 2 name",
    )
    args = ap.parse_args()
    return (
        args.score,
        args.model1 < args.model2,
    )


(
    score,
    model1,
    model2,
) = parse_arguments()
