#!/usr/bin/env python
import numpy as np
from benchmark.Experiments import Datasets
from benchmark.Results import Report, Excel, SQL, ReportBest
from benchmark.Utils import (
    Files,
    TextColor,
)
from benchmark.Arguments import Arguments


"""Build report on screen of a result file, optionally generate excel and sql
file, and can compare results of report with best results obtained by model
If no argument is set, displays the datasets and its characteristics
"""


def default_report():
    sets = Datasets()
    color_line = TextColor.LINE1
    print(color_line, end="")
    print(f"{'Dataset':30s} Samp. Feat Cls Balance")
    print("=" * 30 + " ===== ==== === " + "=" * 40)
    for line in sets:
        X, y = sets.load(line)
        color_line = (
            TextColor.LINE2
            if color_line == TextColor.LINE1
            else TextColor.LINE1
        )
        values, counts = np.unique(y, return_counts=True)
        comp = ""
        sep = ""
        for value, count in zip(values, counts):
            comp += f"{sep}{count/sum(counts)*100:5.2f}%"
            sep = "/ "
        print(color_line, end="")
        print(
            f"{line:30s} {X.shape[0]:5,d} {X.shape[1]:4d} "
            f"{len(np.unique(y)):3d} {comp:40s}"
        )


def main():
    arguments = Arguments()
    arguments.xset("file").xset("excel").xset("sql").xset("compare")
    arguments.xset("best").xset("grid").xset("model", required=False).xset(
        "score"
    )
    args = arguments.parse()

    if args.grid:
        args.best = False
    if args.file is None and args.best is None:
        default_report()
    else:
        if args.best is not None or args.grid is not None:
            report = ReportBest(args.score, args.model, args.best, args.grid)
            report.report()
        else:
            report = Report(args.file, args.compare)
            report.report()
            if args.excel:
                excel = Excel(args.file, args.compare)
                excel.report()
                Files.open(excel.get_file_name())
            if args.sql:
                sql = SQL(args.file)
                sql.report()
