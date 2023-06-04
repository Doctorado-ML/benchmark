import os
from flask import Blueprint, current_app, render_template, url_for
from benchmark.Utils import Files, Folders
from benchmark.ResultsBase import StubReport

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
def index():
    # Get a list of files in a directory
    files = {}
    compare = False
    # names = Files.get_all_results(hidden=False)
    # for name in names:
    #     report = StubReport(os.path.join(Folders.results, name))
    #     report.report()
    #     files[name] = {
    #         "duration": report.duration,
    #         "score": report.score,
    #         "title": report.title,
    #     }
    # candidate = current_app.config["FRAMEWORKS"].copy()
    # candidate.remove(current_app.config["FRAMEWORK"])
    # return render_template(
    #     "select.html",
    #     files=files,
    #     candidate=candidate[0],
    #     framework=current_app.config["FRAMEWORK"],
    #     compare=compare.capitalize() == "True",
    # )
    return render_template("index.html")
