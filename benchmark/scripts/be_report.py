#!/usr/bin/env python
from benchmark.Results import Report, Excel, SQL, ReportBest, ReportDatasets
from benchmark.Utils import Files
from benchmark.Arguments import Arguments


"""Build report on screen of a result file, optionally generate excel and sql
file, and can compare results of report with best results obtained by model
If no argument is set, displays the datasets and its characteristics
"""


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
        ReportDatasets.report()
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
