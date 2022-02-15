#! /usr/bin/env python
import argparse
from Results import Summary

"""List experiments of a model
"""


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-x",
        "--excel",
        type=bool,
        required=False,
        help="Generate Excel file",
    )
    ap.add_argument(
        "-s",
        "--score",
        type=str,
        required=False,
        help="score used in experiment",
    )
    ap.add_argument(
        "-m",
        "--model",
        type=str,
        required=False,
        help="model used in experiment",
    )
    ap.add_argument(
        "-k",
        "--key",
        type=str,
        required=False,
        default="date",
        help="key to sort results",
    )
    ap.add_argument(
        "-n",
        "--number",
        type=int,
        required=False,
        default=0,
        help="number of results to show, 0 to any",
    )
    args = ap.parse_args()

    return (args.excel, args.score, args.model, args.key, args.number)


(excel, score, model, key, number) = parse_arguments()

data = Summary()
data.acquire()
data.list_results(score=score, model=model, sort_key=key, number=number)
