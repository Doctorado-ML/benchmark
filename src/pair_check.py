#!/usr/bin/env python
import argparse
import os
from Results import Summary, StubReport
from Utils import EnvDefault, Folders, TextColor

"""Check best results of two models giving scores and win-tie-loose results
"""


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
        "-m1",
        "--model1",
        type=str,
        required=True,
        help="model 1 name",
    )
    ap.add_argument(
        "-m2",
        "--model2",
        type=str,
        required=True,
        help="model 2 name",
    )
    ap.add_argument(
        "-w",
        "--win",
        type=bool,
        default=False,
        required=False,
        help="show win results",
    )
    ap.add_argument(
        "-l",
        "--loose",
        type=bool,
        default=False,
        required=False,
        help="show loose results",
    )
    args = ap.parse_args()
    return (
        args.score,
        args.model1,
        args.model2,
        args.win,
        args.loose,
    )


(
    score,
    model1,
    model2,
    win_results,
    loose_results,
) = parse_arguments()

summary = Summary()
summary.acquire()
win = tie = loose = 0
winners = []
loosers = []
best_1 = summary.best_result(criterion="model", value=model1, score=score)
best_2 = summary.best_result(criterion="model", value=model2, score=score)
report_1 = StubReport(os.path.join(Folders.results, best_1["file"]))
report_1.report()
report_2 = StubReport(os.path.join(Folders.results, best_2["file"]))
report_2.report()
for result1, result2 in zip(report_1.lines, report_2.lines):
    result = result1["score"] - result2["score"]
    if result > 0:
        win += 1
        winners.append(result1["dataset"])
    elif result < 0:
        loose += 1
        loosers.append(result1["dataset"])
    else:
        tie += 1
print(f"{'Model':<20} {'File':<70} {'Score':<10} Win Tie Loose")
print("=" * 20 + " " + "=" * 70 + " " + "=" * 10 + " === === =====")
print(f"{model1:<20} {best_1['file']:<70} {report_1.score:10.5f}")
print(
    f"{model2:<20} {best_2['file']:<70} "
    f"{report_2.score:10.5f} "
    f"{TextColor.GREEN}{win:3d} {TextColor.YELLOW}{tie:3d} {TextColor.RED}{loose:5d}"
)
if win_results:
    print(TextColor.GREEN+"Winners:")
    print(winners)
if loose_results:
    print(TextColor.RED+"Loosers:")
    print(loosers)