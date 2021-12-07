import argparse
from Results import Summary


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
        help="model name",
    )
    ap.add_argument(
        "-s",
        "--score",
        type=str,
        required=True,
        help="score name {accuracy, f1_micro, f1_macro, all}",
    )
    args = ap.parse_args()
    return (
        args.score,
        args.model,
    )


(
    score,
    model,
) = parse_arguments()

all_metrics = ["accuracy", "f1-macro", "f1-micro"]

metrics = all_metrics if score == "all" else [score]

summary = Summary()
summary.acquire()

for metric in metrics:
    title = f"BEST RESULT of {metric} for {model}"
    best = summary.best_result(criterion="model", value=model, score=metric)
    summary.show_result(data=best, title=title)
    summary.show_result(
        summary.best_result(score=metric), title=f"BEST RESULT of {metric}"
    )
