#!/usr/bin/env python
from benchmark.ResultsFiles import Benchmark
from benchmark.Utils import Files
from benchmark.Arguments import Arguments


def main(args_test=None):
    arguments = Arguments(prog="be_benchmark")
    arguments.xset("score").xset("excel").xset("tex_output").xset("quiet")
    args = arguments.parse(args_test)
    benchmark = Benchmark(score=args.score, visualize=not args.quiet)
    try:
        benchmark.compile_results()
    except ValueError as e:
        print(e)
    else:
        benchmark.save_results()
        benchmark.report(args.tex_output)
        benchmark.exreport()
        if args.excel:
            benchmark.excel()
            Files.open(benchmark.get_excel_file_name(), test=args.quiet)
        if args.tex_output:
            print(f"File {benchmark.get_tex_file()} generated")
