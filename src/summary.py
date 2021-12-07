from Results import Summary

summary = Summary()
summary.acquire()

for metric in ["accuracy", "f1-macro", "f1-micro"]:
    for model in ["STree", "ODTE"]:
        title = f"BEST RESULT of {metric} for {model}"
        best = summary.best_result(
            criterion="model", value=model, score=metric
        )
        summary.show_result(data=best, title=title) if best != {} else print(
            "No best result for {} {}".format(model, metric)
        )
summary.show_result(
    summary.best_result(score="accuracy"), title="BEST RESULT accuracy"
)
summary.show_result(
    summary.best_result(score="f1-macro"), title="BEST RESULT f1_macro"
)
summary.show_result(
    summary.best_result(score="f1-micro"), title="BEST RESULT f1_micro"
)
