#!/usr/bin/env python
import argparse
import numpy as np
from Experiments import Datasets
from Results import Report, Excel, SQL, ReportBest
from Utils import Files, TextColor

"""Build report on screen of a result file, optionally generate excel and sql
file, and can compare results of report with best results obtained by model
If no argument is set, displays the datasets and its characteristics
"""


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-f",
        "--file",
        type=str,
        required=False,
        help="Result file",
    )
    ap.add_argument(
        "-x",
        "--excel",
        type=bool,
        required=False,
        help="Generate Excel file",
    )
    ap.add_argument(
        "-q",
        "--sql",
        type=bool,
        required=False,
        help="Generate sql file",
    )
    ap.add_argument(
        "-c",
        "--compare",
        type=bool,
        required=False,
        help="Compare accuracy with best results",
    )
    ap.add_argument(
        "-b",
        "--best",
        type=str,
        required=False,
        help="best results of models",
    )
    ap.add_argument(
        "-s",
        "--score",
        type=str,
        required=False,
        default="accuracy",
        help="score used in best results model",
    )
    args = ap.parse_args()

    return (
        args.file,
        args.excel,
        args.sql,
        args.compare,
        args.best,
        args.score,
    )


def default_report():
    sets = Datasets()
    color_line = TextColor.LINE1
    print(color_line, end="")
    print(f"{'Dataset':30s} Samp. Feat Cls")
    print("=" * 30 + " ===== ==== ===")
    for line in sets:
        X, y = sets.load(line)
        color_line = (
            TextColor.LINE2
            if color_line == TextColor.LINE1
            else TextColor.LINE1
        )
        print(color_line, end="")
        print(
            f"{line:30s} {X.shape[0]:5,d} {X.shape[1]:4d} "
            f"{len(np.unique(y)):3d}"
        )


(file, excel, sql, compare, best, score) = parse_arguments()

if file is None and best is None:
    default_report()
else:
    if best is not None:
        report = ReportBest(score, best)
        report.report()
    else:
        report = Report(file, compare)
        report.report()
        if excel:
            excel = Excel(file, compare)
            excel.report()
            Files.open(excel.get_file_name())
        if sql:
            sql = SQL(file)
            sql.report()
