#!/usr/bin/env python
from Results import Benchmark
from Utils import Files, EnvDefault
import argparse


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
        "-x",
        "--excel",
        type=bool,
        required=False,
        help="Generate Excel File",
    )
    args = ap.parse_args()
    return (args.score, args.excel)


(score, excel) = parse_arguments()
benchmark = Benchmark(score)
benchmark.compile_results()
benchmark.save_results()
benchmark.report()
benchmark.exreport()
if excel:
    benchmark.excel()
    Files.open(benchmark.get_excel_file_name())
