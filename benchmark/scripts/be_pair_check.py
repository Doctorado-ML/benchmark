#!/usr/bin/env python
from benchmark.Results import PairCheck
from benchmark.Arguments import Arguments

"""Check best results of two models giving scores and win-tie-loose results
"""


def main(argx=None):
    arguments = Arguments()
    arguments.xset("score").xset("win").xset("model1").xset("model2")
    arguments.xset("lose")
    args = arguments.parse(argx)
    pair_check = PairCheck(
        args.score,
        args.model1,
        args.model2,
        args.win,
        args.lose,
    )
    try:
        pair_check.compute()
    except ValueError as e:
        print(str(e))
    else:
        pair_check.report()
