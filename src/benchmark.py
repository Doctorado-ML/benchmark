from Results import Benchmark


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
benchmark = Benchmark()
benchmark.compile_results()
benchmark.report()
benchmark.exreport()
