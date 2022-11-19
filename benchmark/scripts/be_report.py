#!/usr/bin/env python
from benchmark.Results import Report, Excel, SQL, ReportBest, ReportDatasets
from benchmark.Utils import Files
from benchmark.Arguments import Arguments


"""Build report on screen of a result file, optionally generate excel and sql
file, and can compare results of report with best results obtained by model
If no argument is set, displays the datasets and its characteristics
"""


def main(args_test=None):
    arguments = Arguments()
    arguments.xset("file").xset("excel").xset("sql").xset("compare")
    arguments.xset("best").xset("grid").xset("model", required=False)
    arguments.xset("score", required=False)
    args = arguments.parse(args_test)
    if args.best:
        args.grid = False
    if args.grid:
        args.best = False
    if args.file is None and not args.best and not args.grid:
        report = ReportDatasets(args.excel)
        report.report()
        if args.excel:
            is_test = args_test is not None
            Files.open(report.get_file_name(), is_test)
    else:
        if args.best or args.grid:
            report = ReportBest(args.score, args.model, args.best, args.grid)
            report.report()
        else:
            try:
                report = Report(args.file, args.compare)
            except FileNotFoundError as e:
                print(e)
            else:
                report.report()
                if args.excel:
                    excel = Excel(
                        file_name=args.file,
                        compare=args.compare,
                    )
                    excel.report()
                    is_test = args_test is not None
                    Files.open(excel.get_file_name(), is_test)
                if args.sql:
                    sql = SQL(args.file)
                    sql.report()
