from Results import Benchmark
from Utils import Files
import argparse


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-x",
        "--excel",
        type=bool,
        required=False,
        help="Generate Excel File",
    )
    args = ap.parse_args()
    return args.excel


excel = parse_arguments()
benchmark = Benchmark()
benchmark.compile_results()
benchmark.report()
benchmark.exreport()
if excel:
    benchmark.excel()
    Files.open(benchmark.get_excel_file_name())
