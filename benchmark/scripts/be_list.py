#! /usr/bin/env python
import os
from benchmark.Results import Summary
from benchmark.Utils import Folders
from benchmark.Arguments import Arguments

"""List experiments of a model
"""


def main():
    arguments = Arguments()
    arguments.xset("number").xset("model", required=False).xset("score")
    arguments.xset("hidden").xset("nan").xset("key")
    args = arguments.parse()
    data = Summary(hidden=args.hidden)
    data.acquire()
    data.list_results(
        score=args.score,
        model=args.model,
        sort_key=args.key,
        number=args.number,
    )
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
            data.list_results(input_data=results_nan)
            for result in results_nan:
                name = result["file"]
                os.rename(
                    os.path.join(Folders.results, name),
                    os.path.join(Folders.hidden_results, name),
                )
