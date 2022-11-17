#! /usr/bin/env python
import os
from benchmark.Results import Summary
from benchmark.Utils import Folders, Files
from benchmark.Arguments import Arguments

"""List experiments of a model
"""


def main(args_test=None):
    arguments = Arguments()
    arguments.xset("number").xset("model", required=False).xset("key")
    arguments.xset("hidden").xset("nan").xset("score", required=False)
    arguments.xset("excel")
    args = arguments.parse(args_test)
    data = Summary(hidden=args.hidden)
    data.acquire()
    try:
        data.list_results(
            score=args.score,
            model=args.model,
            sort_key=args.key,
            number=args.number,
        )
        is_test = args_test is not None
        if not args.nan:
            excel_generated = data.manage_results(args.excel, is_test)
            if args.excel and excel_generated:
                print(f"Generated file: {Files.be_list_excel}")
                Files.open(Files.be_list_excel, is_test)
    except ValueError as e:
        print(e)
    else:
        if args.nan:
            results_nan = []
            results = data.get_results_criteria(
                score=args.score,
                model=args.model,
                input_data=None,
                sort_key=args.key,
                number=args.number,
            )
            for result in results:
                if result["metric"] != result["metric"]:
                    results_nan.append(result)
            if results_nan != []:
                print(
                    "\n"
                    + "*" * 30
                    + " Results with nan moved to hidden "
                    + "*" * 30
                )
                data.data_filtered = []
                data.list_results(input_data=results_nan)
                for result in results_nan:
                    name = result["file"]
                    os.rename(
                        os.path.join(Folders.results, name),
                        os.path.join(Folders.hidden_results, name),
                    )
