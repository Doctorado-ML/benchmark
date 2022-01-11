import argparse
from Results import Summary
from Utils import EnvDefault


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-s",
        "--score",
        type=str,
        action=EnvDefault,
        envvar="score",
        required=True,
        help="score name {accuracy, f1_micro, f1_macro, all}",
    )
    args = ap.parse_args()
    return (args.score,)


(score,) = parse_arguments()

all_metrics = ["accuracy", "f1-macro", "f1-micro"]

metrics = all_metrics if score == "all" else [score]

summary = Summary()
summary.acquire()

for metric in metrics:
    title = f"BEST RESULTS of {metric} for datasets"
    best = summary.best_results_datasets(score=metric)
    for key, item in best.items():
        print(f"{key}: {item}")
