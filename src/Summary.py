from Results import Summary

summary = Summary()
summary.acquire()

for metric in ["accuracy", "f1_macro", "f1_micro"]:
    for model in ["STree", "ODTE"]:
        best = summary.best_result(
            criterion="model", value=model, score=metric
        )
        summary.show_result(
            best["file"], best["metric"]
        ) if best != {} else print(
            "No best result for {} {}".format(model, metric)
        )
