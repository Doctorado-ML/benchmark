#! /usr/bin/env python
from benchmark.Results import Summary
from benchmark.Utils import Files
from benchmark.Arguments import Arguments

"""List experiments of a model
"""


def main(args_test=None):
    is_test = args_test is not None
    arguments = Arguments(prog="be_list")
    arguments.xset("number").xset("model", required=False).xset("key")
    arguments.xset("score", required=False).xset("compare").xset("hidden")
    args = arguments.parse(args_test)
    data = Summary(hidden=args.hidden, compare=args.compare)
    data.acquire()
    try:
        data.list_results(
            score=args.score,
            model=args.model,
            sort_key=args.key,
            number=args.number,
        )
    except ValueError as e:
        print(e)
        return
    excel_generated = data.manage_results(is_test=is_test)
    if excel_generated:
        print(f"Generated file: {Files.be_list_excel}")
        Files.open(Files.be_list_excel, is_test)
