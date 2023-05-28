#!/usr/bin/env python
import os
import json
import webbrowser
from benchmark.Utils import Files, Folders, Symbols
from benchmark.Arguments import Arguments, EnvData
from benchmark.ResultsBase import StubReport
from flask import Flask
from flask import render_template, request, redirect, url_for


# Launch a flask server to serve the results
app = Flask(__name__)
FRAMEWORK = "framework"
FRAMEWORKS = "frameworks"
HIDDEN = "hidden"


def process_data(file_name, data):
    report = StubReport(os.path.join(Folders.results, file_name))
    new_list = []
    for result in data["results"]:
        symbol = report._compute_status(result["dataset"], result["score"])
        result["symbol"] = symbol if symbol != " " else "&nbsp;"
        new_list.append(result)
    data["results"] = new_list
    # Compute summary with explanation of symbols
    summary = {}
    for key, value in report._compare_totals.items():
        summary[key] = (report._status_meaning(key), value)
    return summary


@app.route("/index")
@app.route("/")
def index():
    # Get a list of files in a directory
    files = Files.get_all_results(hidden=app.config[HIDDEN])
    candidate = app.config[FRAMEWORKS].copy()
    candidate.remove(app.config[FRAMEWORK])
    return render_template(
        f"select.html",
        files=files,
        framework=candidate[0],
        used_framework=app.config[FRAMEWORK],
    )


@app.route("/show", methods=["post"])
def show():
    selected_file = request.form["selected-file"]
    with open(os.path.join(Folders.results, selected_file)) as f:
        data = json.load(f)
    summary = process_data(selected_file, data)
    return render_template(
        f"report.html",
        data=data,
        summary=summary,
        used_framework=app.config[FRAMEWORK],
    )


@app.route("/config/<framework>")
def config(framework):
    if not framework in app.config[FRAMEWORKS]:
        message = f"framework {framework} not supported"
        return render_template("error.html", message=message)
    env = EnvData()
    env.load()
    env.args[FRAMEWORK] = framework
    env.save()
    app.config[FRAMEWORK] = framework
    return redirect(url_for("index"))


def main(args_test=None):
    arguments = Arguments(prog="be_flask")
    arguments.xset("model", required=False)
    arguments.xset("score", required=False).xset("compare").xset("hidden")
    arguments.xset("nan")
    args = arguments.parse(args_test)
    app.config[FRAMEWORK] = EnvData().load()[FRAMEWORK]
    app.config[HIDDEN] = args.hidden
    app.config[FRAMEWORKS] = ["bootstrap", "bulma"]
    webbrowser.open_new("http://127.0.0.1:1234/")
    app.run(port=1234)

    # Poner checkboxes para seleccionar resultados y poner un botón abajo para hacer un excel con los seleccionados
    # Calcular símbolo igual que en list, o bien si ha puesto el parámetro de compare, con best o con zeror
