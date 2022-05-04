#!/usr/bin/env python
from benchmark.Results import PairCheck
from Arguments import Arguments

"""Check best results of two models giving scores and win-tie-loose results
"""


def main():
    arguments = Arguments()
    arguments.xset("score").xset("win").xset("model1").xset("model2")
    arguments.xset("lose")
    args = arguments.parse()
    pair_check = PairCheck(
        args.score,
        args.model1,
        args.model2,
        args.win_results,
        args.lose_results,
    )
    pair_check.compute()
    pair_check.report()
