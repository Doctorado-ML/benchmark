#!/usr/bin/env python
from benchmark.Results import Report, Excel, SQL, ReportBest, ReportDatasets
from benchmark.Utils import Files
from benchmark.Arguments import Arguments


"""Build report on screen of a result file, optionally generate excel and sql
file, and can compare results of report with best results obtained by model
If no argument is set, displays the datasets and its characteristics
"""


def main(args_test=None):
    arguments = Arguments(prog="be_report")
    arguments.add_subparser()
    arguments.add_subparsers_options(
        (
            "best",
            "Report best results obtained by any model/score. "
            "See be_build_best",
        ),
        [
            ("model", dict(required=False)),
            ("score", dict(required=False)),
        ],
    )
    arguments.add_subparsers_options(
        (
            "grid",
            "Report grid results obtained by any model/score. "
            "See be_build_grid",
        ),
        [
            ("model", dict(required=False)),
            ("score", dict(required=False)),
        ],
    )
    arguments.add_subparsers_options(
        ("file", "Report file results"),
        [
            ("file_name", {}),
            ("excel", {}),
            ("sql", {}),
            ("compare", {}),
        ],
    )
    arguments.add_subparsers_options(
        ("datasets", "Report datasets information"),
        [
            ("excel", {}),
        ],
    )
    args = arguments.parse(args_test)
    match args.subcommand:
        case "best" | "grid":
            best = args.subcommand == "best"
            report = ReportBest(args.score, args.model, best)
            report.report()
        case "file":
            try:
                report = Report(args.file_name, args.compare)
                report.report()
            except FileNotFoundError as e:
                print(e)
                return
            if args.sql:
                sql = SQL(args.file_name)
                sql.report()
            if args.excel:
                excel = Excel(
                    file_name=args.file_name,
                    compare=args.compare,
                )
                excel.report()
                is_test = args_test is not None
                Files.open(excel.get_file_name(), is_test)
        case "datasets":
            report = ReportDatasets(args.excel)
            report.report()
            if args.excel:
                is_test = args_test is not None
                Files.open(report.get_file_name(), is_test)
        case _:
            arguments.parse(["-h"])
