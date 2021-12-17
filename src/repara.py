import os
import json

from Experiments import Files, Folders


versions = dict(SVC="-", STree="1.2.3", ODTE="0.3.1")

results = Files().get_all_results()
for result in results:
    print(result)
    file_name = os.path.join(Folders.results, result)
    with open(file_name) as f:
        data = json.load(f)
        if "version" not in data:
            print(f"Repairing version in {result}")
            model = data["model"]
            data["version"] = versions[model] if model in versions else "-"
        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)
