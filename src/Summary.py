from Results import Summary

summary = Summary()
summary.acquire()
print(summary.best_result())
print(summary.best_result(criterion="model", value="ODTE"))
summary.list()
