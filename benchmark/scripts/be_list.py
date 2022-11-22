#! /usr/bin/env python
from benchmark.Results import Summary
from benchmark.Utils import Files
from benchmark.Arguments import Arguments

"""List experiments of a model
"""


def main(args_test=None):
    arguments = Arguments(prog="be_list")
    arguments.xset("number").xset("model", required=False).xset("key")
    arguments.xset("score", required=False).xset("compare").xset("hidden")
    arguments.xset("nan")
    args = arguments.parse(args_test)
    data = Summary(hidden=args.hidden, compare=args.compare)
    data.acquire()
    try:
        data.list_results(
            score=args.score,
            model=args.model,
            sort_key=args.key,
            number=args.number,
            nan=args.nan,
        )
    except ValueError as e:
        print(e)
        return
    excel_generated = data.manage_results()
    if excel_generated:
        print(f"Generated file: {Files.be_list_excel}")
        Files.open(Files.be_list_excel, test=args_test is not None)
